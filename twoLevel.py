
# import the m5 (gem5) library created when gem5 is built
import m5
# import all of the SimObjects
from m5.objects import *
from gem5.runtime import get_runtime_isa
from m5 import options
# Add the common scripts to our path
m5.util.addToPath("../../")
# import the caches which we made
from caches import *
# import the SimpleOpts module
from common import SimpleOpts

# grab the specific path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
default_binary = "401.bzip2"
# Arguments to the configuration
SimpleOpts.add_option("benchmark", nargs="?", default=default_binary)
SimpleOpts.add_option("--l1_assoc", nargs="?", default=2)
SimpleOpts.add_option("--l1_cache_line_size", nargs="?", default=64)
SimpleOpts.add_option("--l1i_size", nargs="?", default='32kB')
SimpleOpts.add_option("--l1d_size", nargs="?", default='32kB')
SimpleOpts.add_option("--l2_size", nargs="?", default='1MB')
SimpleOpts.add_option("--l2_assoc", nargs="?", default=2)
SimpleOpts.add_option("--l2_cache_line_size", nargs="?", default=64)

# Finalize the arguments and grab the args so we can pass it on to our objects
args = SimpleOpts.parse_args()
# create the system we are going to simulate
system = System()
# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "3GHz"
system.clk_domain.voltage_domain = VoltageDomain()
# Set up the system
system.mem_mode = "timing"  # Use timing accesses
system.mem_ranges = [AddrRange("1GB")]  # Create an address range
# Create a simple CPU
cpu = X86TimingSimpleCPU()
system.cpu = cpu

# Create an L1 instruction and data cache
system.cpu.icache = L1ICache(args)
system.cpu.dcache = L1DCache(args)
# Connect the instruction and data caches to the CPU
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)
# Create a memory bus, a coherent crossbar, in this case
system.l2bus = L2XBar()
# Hook the CPU ports up to the l2bus
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)
# Create an L2 cache and connect it to the l2bus
system.l2cache = L2Cache(args)
system.l2cache.connectCPUSideBus(system.l2bus)
# Create a memory bus
system.membus = SystemXBar()
# Connect the L2 cache to the membus
system.l2cache.connectMemSideBus(system.membus)
# create the interrupt controller for the CPU
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports
# Create a DDR3 memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# create benchmarks path
benchmarkBinaryPath = os.path.join(
    thispath,
    "../../",
    f'CS6301P1/benchmarks/Project1_SPEC-master/{args.benchmark}/src/benchmark',
)
#create ouput stats dump path
ouputStatsDump = os.path.join(
    '/root/gem5/configs/',
    f'CS6301P1/outputstats/{args.benchmark}/l1_i_{args.l1i_size}_d_{args.l1d_size}_asc_{args.l1_assoc}_blk_{args.l1_cache_line_size}_l2_{args.l2_size}_asc_{args.l2_assoc}_blk_{args.l2_cache_line_size}_stats',
)

#/root/gem5/configs/CS6301P1/benchmarks/Project1_SPEC-master/401.bzip2/data/input.program

def getCustomArgs(benchmarkName):
    folderpath = f'/root/gem5/configs/CS6301P1/benchmarks/Project1_SPEC-master/{benchmarkName}/data'
    switcher ={
        '401.bzip2':[f'{folderpath}/input.program','10'],
        '429.mcf':[f'{folderpath}/inp.in'],
        '456.hmmer':['--fixed','0','--mean','325','--num','45000','--sd','200','--seed','0',f'{folderpath}/bombesin.hmm'],
        '458.sjeng':[f'{folderpath}/test.txt'],
        '470.lbm':['20',f'{folderpath}/reference.dat','0','1',f'{folderpath}/100_100_130_cf_a.of'],
    }
    return switcher.get(benchmarkName, [])


system.workload = SEWorkload.init_compatible(benchmarkBinaryPath)

# Create a process for a simple "Hello World" application
process = Process()
process.cmd = [benchmarkBinaryPath] + getCustomArgs(args.benchmark)

# Set the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.createThreads()
# Limit maximum number of instructions 
max_insts = 100000000
options.maxinsts = max_insts 
# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()
print("Beginning simulation!")
exit_event = m5.simulate()
print("Exiting @ tick %i because %s" % (m5.curTick(), exit_event.getCause()))

# copy simulation stats
import shutil

src_dir = '/root/gem5/m5out'
dst_dir =  ouputStatsDump
if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)
# Copy all files in src_dir to dst_dir
for file_name in os.listdir(src_dir):
    src_path = os.path.join(src_dir, file_name)
    dst_path = os.path.join(dst_dir, file_name)
    shutil.move(src_path, dst_path)



