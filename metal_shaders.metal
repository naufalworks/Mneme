#include <metal_stdlib>
using namespace metal;

// ============================================================================
// Vector Binding (element-wise multiplication)
// ============================================================================
kernel void vector_bind(
    device const int8_t* vec1 [[buffer(0)]],
    device const int8_t* vec2 [[buffer(1)]],
    device int8_t* result [[buffer(2)]],
    uint id [[thread_position_in_grid]]
) {
    result[id] = vec1[id] * vec2[id];
}

// ============================================================================
// Vector Bundling (sum + threshold)
// ============================================================================
kernel void vector_bundle_sum(
    device const int8_t* vectors [[buffer(0)]],
    device int32_t* partial_sums [[buffer(1)]],
    constant uint& num_vectors [[buffer(2)]],
    constant uint& dims [[buffer(3)]],
    uint id [[thread_position_in_grid]]
) {
    int32_t sum = 0;
    for (uint i = 0; i < num_vectors; i++) {
        sum += vectors[i * dims + id];
    }
    partial_sums[id] = sum;
}

kernel void vector_bundle_threshold(
    device const int32_t* sums [[buffer(0)]],
    device int8_t* result [[buffer(1)]],
    uint id [[thread_position_in_grid]]
) {
    int32_t val = sums[id];
    result[id] = (val > 0) ? 1 : ((val < 0) ? -1 : 0);
}

// ============================================================================
// Cosine Similarity (optimized with parallel reduction)
// ============================================================================
kernel void cosine_similarity_dot(
    device const int8_t* vec1 [[buffer(0)]],
    device const int8_t* vec2 [[buffer(1)]],
    device int32_t* partial_dots [[buffer(2)]],
    uint id [[thread_position_in_grid]],
    uint tid [[thread_index_in_threadgroup]],
    uint threads_per_group [[threads_per_threadgroup]]
) {
    // Each thread computes partial dot product
    int32_t dot = vec1[id] * vec2[id];

    // Store in shared memory for reduction
    threadgroup int32_t shared_dots[1024];
    shared_dots[tid] = dot;
    threadgroup_barrier(mem_flags::mem_threadgroup);

    // Parallel reduction
    for (uint stride = threads_per_group / 2; stride > 0; stride >>= 1) {
        if (tid < stride) {
            shared_dots[tid] += shared_dots[tid + stride];
        }
        threadgroup_barrier(mem_flags::mem_threadgroup);
    }

    // First thread writes result
    if (tid == 0) {
        partial_dots[id / threads_per_group] = shared_dots[0];
    }
}

kernel void cosine_similarity_norms(
    device const int8_t* vec1 [[buffer(0)]],
    device const int8_t* vec2 [[buffer(1)]],
    device int32_t* partial_norm1 [[buffer(2)]],
    device int32_t* partial_norm2 [[buffer(3)]],
    uint id [[thread_position_in_grid]],
    uint tid [[thread_index_in_threadgroup]],
    uint threads_per_group [[threads_per_threadgroup]]
) {
    // Compute partial norms
    int32_t n1 = vec1[id] * vec1[id];
    int32_t n2 = vec2[id] * vec2[id];

    threadgroup int32_t shared_n1[1024];
    threadgroup int32_t shared_n2[1024];
    shared_n1[tid] = n1;
    shared_n2[tid] = n2;
    threadgroup_barrier(mem_flags::mem_threadgroup);

    // Parallel reduction
    for (uint stride = threads_per_group / 2; stride > 0; stride >>= 1) {
        if (tid < stride) {
            shared_n1[tid] += shared_n1[tid + stride];
            shared_n2[tid] += shared_n2[tid + stride];
        }
        threadgroup_barrier(mem_flags::mem_threadgroup);
    }

    if (tid == 0) {
        partial_norm1[id / threads_per_group] = shared_n1[0];
        partial_norm2[id / threads_per_group] = shared_n2[0];
    }
}

// ============================================================================
// LSH Random Projection Hashing
// ============================================================================
kernel void lsh_hash_projection(
    device const int8_t* vector [[buffer(0)]],
    device const float* projection_matrix [[buffer(1)]],
    device float* projections [[buffer(2)]],
    constant uint& dims [[buffer(3)]],
    constant uint& n_bits [[buffer(4)]],
    uint bit_id [[thread_position_in_grid]]
) {
    // Each thread computes one bit of the hash
    float sum = 0.0f;
    for (uint i = 0; i < dims; i++) {
        sum += vector[i] * projection_matrix[bit_id * dims + i];
    }
    projections[bit_id] = sum;
}

kernel void lsh_hash_threshold(
    device const float* projections [[buffer(0)]],
    device uint8_t* hash_bits [[buffer(1)]],
    uint id [[thread_position_in_grid]]
) {
    hash_bits[id] = (projections[id] > 0.0f) ? 1 : 0;
}

// ============================================================================
// Batch Operations (process multiple vectors at once)
// ============================================================================
kernel void batch_cosine_similarity(
    device const int8_t* query [[buffer(0)]],
    device const int8_t* vectors [[buffer(1)]],
    device float* similarities [[buffer(2)]],
    constant uint& dims [[buffer(3)]],
    constant uint& num_vectors [[buffer(4)]],
    uint vec_id [[thread_position_in_grid]]
) {
    if (vec_id >= num_vectors) return;

    // Compute dot product and norms for this vector (int64 for precision)
    int64_t dot = 0;
    int64_t norm_q = 0;
    int64_t norm_v = 0;

    device const int8_t* vec = vectors + (vec_id * dims);

    // Vectorized loop - process 4 elements at a time
    uint i = 0;
    uint vec_limit = (dims / 4) * 4;

    for (; i < vec_limit; i += 4) {
        // Load 4 elements at once
        int8_t q0 = query[i];
        int8_t q1 = query[i+1];
        int8_t q2 = query[i+2];
        int8_t q3 = query[i+3];

        int8_t v0 = vec[i];
        int8_t v1 = vec[i+1];
        int8_t v2 = vec[i+2];
        int8_t v3 = vec[i+3];

        // Accumulate
        dot += int64_t(q0) * int64_t(v0);
        dot += int64_t(q1) * int64_t(v1);
        dot += int64_t(q2) * int64_t(v2);
        dot += int64_t(q3) * int64_t(v3);

        norm_q += int64_t(q0) * int64_t(q0);
        norm_q += int64_t(q1) * int64_t(q1);
        norm_q += int64_t(q2) * int64_t(q2);
        norm_q += int64_t(q3) * int64_t(q3);

        norm_v += int64_t(v0) * int64_t(v0);
        norm_v += int64_t(v1) * int64_t(v1);
        norm_v += int64_t(v2) * int64_t(v2);
        norm_v += int64_t(v3) * int64_t(v3);
    }

    // Handle remaining elements
    for (; i < dims; i++) {
        int8_t q = query[i];
        int8_t v = vec[i];
        dot += int64_t(q) * int64_t(v);
        norm_q += int64_t(q) * int64_t(q);
        norm_v += int64_t(v) * int64_t(v);
    }

    // Compute similarity with float precision (Metal doesn't support double)
    float norm_product = sqrt(float(norm_q)) * sqrt(float(norm_v));
    similarities[vec_id] = (norm_product > 0.0f) ? (float(dot) / norm_product) : 0.0f;
}

// ============================================================================
// Memory Copy Optimizations
// ============================================================================
kernel void fast_copy_int8(
    device const int8_t* src [[buffer(0)]],
    device int8_t* dst [[buffer(1)]],
    uint id [[thread_position_in_grid]]
) {
    dst[id] = src[id];
}
