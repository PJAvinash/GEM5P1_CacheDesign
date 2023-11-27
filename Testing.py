import os
thispath = os.path.dirname(os.path.realpath(__file__))
# create benchmarks path
benchmarkBinaryPath = os.path.join(
    thispath,
    "../../",
    f'CS6301P1/benchmarks/Project1_SPEC-master/test/src/benchmark'
)
print(benchmarkBinaryPath)