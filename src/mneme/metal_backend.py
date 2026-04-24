"""
Metal Backend for M4 Neural Engine Acceleration

Provides GPU-accelerated vector operations using Metal Performance Shaders.
"""

import numpy as np
from Metal import (
    MTLCreateSystemDefaultDevice,
    MTLResourceStorageModeShared,
)
from pathlib import Path
import objc


class MetalAccelerator:
    """GPU acceleration using M4 Neural Engine via Metal."""

    def __init__(self):
        """Initialize Metal device and compile shaders."""
        self.device = MTLCreateSystemDefaultDevice()
        if not self.device:
            raise RuntimeError("Metal not available on this system")

        print(f"✓ Metal initialized: {self.device.name()}")

        # Create command queue
        self.command_queue = self.device.newCommandQueue()

        # Load and compile shaders
        self._load_shaders()

        # Cache for pipeline states
        self.pipelines = {}

    def _load_shaders(self):
        """Load Metal shader library."""
        shader_path = Path(__file__).parent.parent / "metal_shaders.metal"

        if not shader_path.exists():
            raise FileNotFoundError(f"Metal shaders not found at {shader_path}")

        with open(shader_path, 'r') as f:
            shader_code = f.read()

        # Compile shader library
        options = None
        error = objc.nil
        self.library, error = self.device.newLibraryWithSource_options_error_(
            shader_code, options, error
        )

        if error:
            raise RuntimeError(f"Failed to compile Metal shaders: {error}")

        print("✓ Metal shaders compiled")

    def _get_pipeline(self, function_name):
        """Get or create compute pipeline for function."""
        if function_name in self.pipelines:
            return self.pipelines[function_name]

        function = self.library.newFunctionWithName_(function_name)
        if not function:
            raise RuntimeError(f"Metal function '{function_name}' not found")

        error = objc.nil
        pipeline, error = self.device.newComputePipelineStateWithFunction_error_(
            function, error
        )

        if error:
            raise RuntimeError(f"Failed to create pipeline: {error}")

        self.pipelines[function_name] = pipeline
        return pipeline

    def _create_buffer(self, data):
        """Create Metal buffer from numpy array."""
        if not isinstance(data, np.ndarray):
            data = np.array(data)

        # Ensure contiguous array
        data = np.ascontiguousarray(data)

        buffer = self.device.newBufferWithBytes_length_options_(
            data.tobytes(),
            data.nbytes,
            MTLResourceStorageModeShared
        )

        return buffer

    def _create_empty_buffer(self, size, dtype=np.int8):
        """Create empty Metal buffer."""
        nbytes = size * np.dtype(dtype).itemsize
        buffer = self.device.newBufferWithLength_options_(
            nbytes,
            MTLResourceStorageModeShared
        )
        return buffer

    def _buffer_to_numpy(self, buffer, shape, dtype=np.int8):
        """Convert Metal buffer to numpy array."""
        size = int(np.prod(shape))
        nbytes = size * np.dtype(dtype).itemsize

        # Use PyObjC's buffer protocol
        contents = buffer.contents().as_buffer(nbytes)
        arr = np.frombuffer(contents, dtype=dtype, count=size)
        return arr.reshape(shape).copy()

    def bind(self, vec1, vec2):
        """Element-wise multiplication (GPU accelerated)."""
        vec1 = np.ascontiguousarray(vec1, dtype=np.int8)
        vec2 = np.ascontiguousarray(vec2, dtype=np.int8)

        if vec1.shape != vec2.shape:
            raise ValueError("Vectors must have same shape")

        dims = vec1.size

        # Create buffers
        buf1 = self._create_buffer(vec1)
        buf2 = self._create_buffer(vec2)
        buf_result = self._create_empty_buffer(dims, np.int8)

        # Get pipeline
        pipeline = self._get_pipeline("vector_bind")

        # Create command buffer and encoder
        command_buffer = self.command_queue.commandBuffer()
        encoder = command_buffer.computeCommandEncoder()

        encoder.setComputePipelineState_(pipeline)
        encoder.setBuffer_offset_atIndex_(buf1, 0, 0)
        encoder.setBuffer_offset_atIndex_(buf2, 0, 1)
        encoder.setBuffer_offset_atIndex_(buf_result, 0, 2)

        # Dispatch threads
        threads_per_group = min(pipeline.maxTotalThreadsPerThreadgroup(), dims)
        threadgroup_size = (threads_per_group, 1, 1)
        grid_size = (dims, 1, 1)

        encoder.dispatchThreads_threadsPerThreadgroup_(grid_size, threadgroup_size)
        encoder.endEncoding()

        # Execute
        command_buffer.commit()
        command_buffer.waitUntilCompleted()

        # Get result
        result = self._buffer_to_numpy(buf_result, vec1.shape, np.int8)
        return result

    def cosine_similarity(self, vec1, vec2):
        """Cosine similarity (GPU accelerated)."""
        vec1 = np.ascontiguousarray(vec1, dtype=np.int8)
        vec2 = np.ascontiguousarray(vec2, dtype=np.int8)

        if vec1.shape != vec2.shape:
            raise ValueError("Vectors must have same shape")

        # For now, use CPU for final computation
        # TODO: Implement full GPU reduction
        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot / (norm1 * norm2))

    def batch_cosine_similarity(self, query, vectors):
        """Batch cosine similarity (GPU accelerated)."""
        query = np.ascontiguousarray(query, dtype=np.int8)
        vectors = np.ascontiguousarray(vectors, dtype=np.int8)

        if vectors.ndim != 2:
            raise ValueError("Vectors must be 2D array")

        num_vectors, dims = vectors.shape

        if query.size != dims:
            raise ValueError("Query dimension mismatch")

        # Create buffers
        buf_query = self._create_buffer(query)
        buf_vectors = self._create_buffer(vectors)
        buf_result = self._create_empty_buffer(num_vectors, np.float32)

        # Create constant buffers
        dims_buf = self._create_buffer(np.array([dims], dtype=np.uint32))
        num_buf = self._create_buffer(np.array([num_vectors], dtype=np.uint32))

        # Get pipeline
        pipeline = self._get_pipeline("batch_cosine_similarity")

        # Create command buffer and encoder
        command_buffer = self.command_queue.commandBuffer()
        encoder = command_buffer.computeCommandEncoder()

        encoder.setComputePipelineState_(pipeline)
        encoder.setBuffer_offset_atIndex_(buf_query, 0, 0)
        encoder.setBuffer_offset_atIndex_(buf_vectors, 0, 1)
        encoder.setBuffer_offset_atIndex_(buf_result, 0, 2)
        encoder.setBuffer_offset_atIndex_(dims_buf, 0, 3)
        encoder.setBuffer_offset_atIndex_(num_buf, 0, 4)

        # Dispatch threads (one per vector)
        threads_per_group = min(pipeline.maxTotalThreadsPerThreadgroup(), num_vectors)
        threadgroup_size = (threads_per_group, 1, 1)
        grid_size = (num_vectors, 1, 1)

        encoder.dispatchThreads_threadsPerThreadgroup_(grid_size, threadgroup_size)
        encoder.endEncoding()

        # Execute
        command_buffer.commit()
        command_buffer.waitUntilCompleted()

        # Get result
        result = self._buffer_to_numpy(buf_result, (num_vectors,), np.float32)
        return result


# Singleton instance
_metal_accelerator = None


def get_metal_accelerator():
    """Get or create Metal accelerator instance."""
    global _metal_accelerator
    if _metal_accelerator is None:
        try:
            _metal_accelerator = MetalAccelerator()
        except Exception as e:
            print(f"⚠ Metal acceleration not available: {e}")
            _metal_accelerator = None
    return _metal_accelerator
