import m5
from m5.objects import Cache
# Add the common scripts to our path
m5.util.addToPath("../../")
from common import SimpleOpts
# Some specific options for caches
# For all options see src/mem/cache/BaseCache.py
class L1Cache(Cache):
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    #cache_line_size = 64
    def __init__(self, options=None):
        super(L1Cache, self).__init__()
        if options:
            if options.l1_assoc:
                self.assoc = options.l1_assoc
            #if options.l1_cache_line_size:
                #print(f'input cache size:')
                #self.cache_line_size = options.l1_cache_line_size    
        else:
            return
    def connectBus(self, bus):
        """Connect this cache to a memory-side bus"""
        self.mem_side = bus.cpu_side_ports
    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU-side port
        This must be defined in a subclass"""
        raise NotImplementedError
class L1ICache(L1Cache):
    # Set the default size
    size = "32kB"
    def __init__(self, options=None):
        super(L1ICache, self).__init__(options)
        if options:
            if options.l1d_size:
                self.size = options.l1d_size
        else:
            return
    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU icache port"""
        self.cpu_side = cpu.icache_port
class L1DCache(L1Cache):
    # Set the default size
    size = "32kB"
    def __init__(self, options =None):
        super(L1DCache, self).__init__(options)
        if options:
            if options.l1d_size:
                self.size = options.l1d_size
        else:
            return
    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU dcache port"""
        self.cpu_side = cpu.dcache_port
class L2Cache(Cache):
    # Default parameters
    size = "256kB"
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12
    #cache_line_size = 64
    def __init__(self, options=None):
        super(L2Cache, self).__init__()
        if options:
            if options.l2_size:
                self.size = options.l2_size
            if options.l2_assoc:
                self.assoc = options.l2_assoc
            #if options.cache_line_size:
                #self.cache_line_size = options.l2_cache_line_size    
        else:
            return
    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports
    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports