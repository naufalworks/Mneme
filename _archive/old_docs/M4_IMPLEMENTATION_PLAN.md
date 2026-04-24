# M4 Neural Engine Integration Plan

**Goal:** Leverage M4 Mac's 38 TOPS Neural Engine for 100x speedup

---

## Phase 1: Metal Setup (30 min)

### What is Metal?
- Apple's GPU programming framework
- Direct access to M4 Neural Engine
- Metal Performance Shaders (MPS) for ML operations

### Check Metal availability
```python
import Metal
device = Metal.MTLCreateSystemDefaultDevice()
print(f"GPU: {device.name()}")
```

---

## Phase 2: Metal Compute Shaders (2-3 hours)

### Operations to accelerate:
1. **Vector binding** (element-wise multiply)
2. **Vector bundling** (sum + threshold)
3. **Cosine similarity** (dot product + norms)
4. **LSH hashing** (random projections)

### Metal Shader Language (MSL)
```metal
kernel void vector_bind(
    device const int8_t* vec1 [[buffer(0)]],
    device const int8_t* vec2 [[buffer(1)]],
    device int8_t* result [[buffer(2)]],
    uint id [[thread_position_in_grid]]
) {
    result[id] = vec1[id] * vec2[id];
}
```

---

## Phase 3: Python Integration (2-3 hours)

### Use PyObjC for Metal bindings
```python
import Metal
import numpy as np

class MetalAccelerator:
    def __init__(self):
        self.device = Metal.MTLCreateSystemDefaultDevice()
        self.command_queue = self.device.newCommandQueue()
        self.library = self.device.newLibraryWithSource_options_error_(
            metal_shader_code, None, None
        )[0]
    
    def bind_vectors(self, vec1, vec2):
        # Create Metal buffers
        # Execute shader
        # Return result
        pass
```

---

## Phase 4: Benchmark (30 min)

### Expected Results:
- **Current:** 4.3ms per query
- **With Metal:** 0.006ms per query (700x faster)
- **Throughput:** 231 → 166,000 queries/sec

---

## Implementation Steps

### Step 1: Install Metal tools
```bash
# Already installed on macOS
xcode-select --install  # if needed
```

### Step 2: Create Metal shader file
- `metal_shaders.metal` with compute kernels

### Step 3: Python wrapper
- `src/metal_backend.py` with Metal integration

### Step 4: Update integration layer
- Detect Metal availability
- Fall back to Python/Rust if unavailable

---

## File Structure

```
memtxt/
├── metal_shaders.metal          # GPU compute kernels
├── src/
│   ├── metal_backend.py         # Metal Python wrapper
│   ├── metal_accelerator.py     # High-level API
│   └── integration.py           # Updated to use Metal
├── benchmark_metal.py           # Metal vs Python/Rust
└── hypervector_rs/              # Rust fallback
```

---

## Timeline

**Total: 6-8 hours (1-2 days)**

- ✅ Phase 1: Setup (30 min)
- ⏳ Phase 2: Shaders (2-3 hours)
- ⏳ Phase 3: Integration (2-3 hours)
- ⏳ Phase 4: Benchmark (30 min)
- ⏳ Phase 5: Optimization (1-2 hours)

---

## Let's Start!

First, let me check if Metal is available and create the shader code.
