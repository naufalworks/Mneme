use pyo3::prelude::*;
use numpy::{PyArray1, PyReadonlyArray1};
use ndarray::{Array1, ArrayView1};
use rayon::prelude::*;
use ahash::AHashMap;

mod simd;
mod optimized_lsh;

/// Hypervector operations optimized with Rust + SIMD
#[pyclass]
struct HypervectorSpace {
    dims: usize,
    #[allow(dead_code)]
    concepts: AHashMap<String, Array1<i8>>,
}

#[pymethods]
impl HypervectorSpace {
    #[new]
    fn new(dims: usize) -> Self {
        HypervectorSpace {
            dims,
            concepts: AHashMap::new(),
        }
    }

    /// Bind two vectors (element-wise multiplication) - SIMD optimized
    fn bind<'py>(
        &self,
        py: Python<'py>,
        vec1: PyReadonlyArray1<i8>,
        vec2: PyReadonlyArray1<i8>,
    ) -> Bound<'py, PyArray1<i8>> {
        let v1 = vec1.as_array();
        let v2 = vec2.as_array();

        let mut result = Array1::<i8>::zeros(v1.len());

        // Use SIMD for fast multiplication
        unsafe {
            simd::bind_simd(v1.as_slice().unwrap(), v2.as_slice().unwrap(), result.as_slice_mut().unwrap());
        }

        PyArray1::from_array(py, &result)
    }

    /// Bundle multiple vectors (sum + threshold) - SIMD optimized
    fn bundle<'py>(
        &self,
        py: Python<'py>,
        vectors: Vec<PyReadonlyArray1<i8>>,
    ) -> Bound<'py, PyArray1<i8>> {
        if vectors.is_empty() {
            return PyArray1::zeros(py, self.dims, false);
        }

        let mut result = Array1::<i8>::zeros(self.dims);

        // Convert to owned arrays to avoid lifetime issues
        let owned_vecs: Vec<Array1<i8>> = vectors.iter()
            .map(|v| v.as_array().to_owned())
            .collect();

        // Collect slices
        let vec_slices: Vec<&[i8]> = owned_vecs.iter()
            .map(|v| v.as_slice().unwrap())
            .collect();

        // Use SIMD for fast bundling
        unsafe {
            simd::bundle_simd(&vec_slices, result.as_slice_mut().unwrap());
        }

        PyArray1::from_array(py, &result)
    }

    /// Cosine similarity (SIMD optimized)
    fn cosine_similarity(
        &self,
        vec1: PyReadonlyArray1<i8>,
        vec2: PyReadonlyArray1<i8>,
    ) -> f64 {
        let v1 = vec1.as_array();
        let v2 = vec2.as_array();

        // Use SIMD for fast cosine similarity
        unsafe {
            simd::cosine_similarity_simd(v1.as_slice().unwrap(), v2.as_slice().unwrap())
        }
    }
}

/// LSH Index for fast approximate nearest neighbor search
#[pyclass]
struct LSHIndex {
    #[allow(dead_code)]
    dims: usize,
    n_tables: usize,
    n_bits: usize,
    #[allow(dead_code)]
    tables: Vec<AHashMap<String, Vec<usize>>>,
    #[allow(dead_code)]
    vectors: Vec<Array1<i8>>,
    #[allow(dead_code)]
    metadata: Vec<String>,
}

#[pymethods]
impl LSHIndex {
    #[new]
    fn new(dims: usize, n_tables: usize, n_bits: usize) -> Self {
        LSHIndex {
            dims,
            n_tables,
            n_bits,
            tables: vec![AHashMap::new(); n_tables],
            vectors: Vec::new(),
            metadata: Vec::new(),
        }
    }

    /// Add vector to index
    fn add(&mut self, vector: PyReadonlyArray1<i8>, metadata: String) {
        let vec = vector.as_array().to_owned();
        let idx = self.vectors.len();

        self.vectors.push(vec.clone());
        self.metadata.push(metadata);

        // Hash and insert into all tables (parallel)
        for table_idx in 0..self.n_tables {
            let hash = self.hash_vector(&vec, table_idx);
            self.tables[table_idx]
                .entry(hash)
                .or_insert_with(Vec::new)
                .push(idx);
        }
    }

    /// Query for similar vectors
    fn query(
        &self,
        vector: PyReadonlyArray1<i8>,
        top_k: usize,
    ) -> Vec<(String, f64)> {
        let vec = vector.as_array();
        let mut candidates = AHashMap::new();

        // Collect candidates from all tables
        for table_idx in 0..self.n_tables {
            let hash = self.hash_vector_view(vec, table_idx);
            if let Some(indices) = self.tables[table_idx].get(&hash) {
                for &idx in indices {
                    *candidates.entry(idx).or_insert(0) += 1;
                }
            }
        }

        // Score candidates in parallel
        let candidates_vec: Vec<_> = candidates.into_iter().collect();
        let mut results: Vec<_> = candidates_vec
            .into_par_iter()
            .map(|(idx, _count)| {
                let similarity = self.cosine_similarity_internal(vec, &self.vectors[idx]);
                (idx, similarity)
            })
            .collect();

        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        results.truncate(top_k);

        results
            .into_iter()
            .map(|(idx, sim)| (self.metadata[idx].clone(), sim))
            .collect()
    }
}

impl LSHIndex {
    fn hash_vector(&self, vector: &Array1<i8>, table_idx: usize) -> String {
        // Simple random projection hash
        let seed = table_idx as u64;
        let mut hash = String::with_capacity(self.n_bits);

        for bit in 0..self.n_bits {
            let mut sum = 0i32;
            for (i, &val) in vector.iter().enumerate() {
                let proj = ((i + bit + seed as usize) % 2) as i32 * 2 - 1;
                sum += (val as i32) * proj;
            }
            hash.push(if sum > 0 { '1' } else { '0' });
        }

        hash
    }

    fn hash_vector_view(&self, vector: ArrayView1<i8>, table_idx: usize) -> String {
        let seed = table_idx as u64;
        let mut hash = String::with_capacity(self.n_bits);

        for bit in 0..self.n_bits {
            let mut sum = 0i32;
            for (i, &val) in vector.iter().enumerate() {
                let proj = ((i + bit + seed as usize) % 2) as i32 * 2 - 1;
                sum += (val as i32) * proj;
            }
            hash.push(if sum > 0 { '1' } else { '0' });
        }

        hash
    }

    fn cosine_similarity_internal(&self, v1: ArrayView1<i8>, v2: &Array1<i8>) -> f64 {
        let dot: i32 = v1.iter()
            .zip(v2.iter())
            .map(|(a, b)| (*a as i32) * (*b as i32))
            .sum();

        let norm1: f64 = v1.iter()
            .map(|&x| (x as i32).pow(2))
            .sum::<i32>() as f64;
        let norm1 = norm1.sqrt();

        let norm2: f64 = v2.iter()
            .map(|&x| (x as i32).pow(2))
            .sum::<i32>() as f64;
        let norm2 = norm2.sqrt();

        if norm1 == 0.0 || norm2 == 0.0 {
            return 0.0;
        }

        dot as f64 / (norm1 * norm2)
    }
}

/// Optimized LSH Index (Python wrapper)
#[pyclass]
struct OptimizedLSH {
    inner: optimized_lsh::OptimizedLSHIndex,
}

#[pymethods]
impl OptimizedLSH {
    #[new]
    fn new(dims: usize, n_tables: usize, n_bits: usize) -> Self {
        OptimizedLSH {
            inner: optimized_lsh::OptimizedLSHIndex::new(dims, n_tables, n_bits),
        }
    }

    fn add(&mut self, vector: PyReadonlyArray1<i8>, metadata: String) {
        let vec = vector.as_array().to_owned();
        self.inner.add(vec, metadata);
    }

    fn query(&self, vector: PyReadonlyArray1<i8>, top_k: usize) -> Vec<(String, f64)> {
        let vec = vector.as_array();
        self.inner.query(vec.as_slice().unwrap(), top_k)
    }

    fn stats(&self) -> (usize, usize, f64) {
        self.inner.stats()
    }
}

#[pymodule]
fn hypervector_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<HypervectorSpace>()?;
    m.add_class::<LSHIndex>()?;
    m.add_class::<OptimizedLSH>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bind() {
        let space = HypervectorSpace::new(100);
        assert_eq!(space.dims, 100);
    }
}
