# Performance Analysis

The Intel Parallel Studio Tool suite can be used to conduct performance analysis at different levels of granularity;

- Intel VTune Applicatio Performance Snapshot: Provides summary overview of performance as well as diagnosis of boundedness cause
- Intel Trace Analyzer & Collector (ITAC): MPI tuning and analysis
- Intel VTune Amplifier: Performance profiler on a single node
- Intel Advisor: Vectorization optimization, thread prototyping and flow graph analysis

The scripts `run_MPI_itac.sh`, `run_MPI_amplxe.sh` and `run_MPI_adapt.sh` each launch a Slurm job for the respective profilers on the given executable (default is `inte-qnlp/demos/hamming_RotY/exe_demo_hamming_RotY`) and configuration.

## Configure and build the simulator for profiling

### Build Makefiles for the simulator

In order to run the profiling scripts with full functionality, ensure that the Intel Quantum Simulator used for building the executable is built with the following flags set; `-trace -fno-omit-frame-pointer -fPIC -g -O3`. Note: that some of these flags will inhibit performance and should be removed for production runs and proper benchmarking statistics. The local static simulator must now be built with the same flags enabled. 

Both of these steps can be done by running the cmake with the `-DENABLE_PRFILING=ON` flag set.

```{bash}
cmake CC=mpiicc CXX=mpiicpc <PATH-TO-CMAKELISTS_FILE>/CMakeLists.txt -DENABLE_PROFILING=ON <ANY-OTHER-FLAGS>
```

### Set environment variables for profiling tools

Environment variables for the profiling suite need to be set by running the `psxevars.sh` script which is contained in the `parallel_studio_xe_*` directory, relative to the install location of the  Intel library being used.

```{bash}
source <PATH-TO-SCRIPT>/psxevars.sh
```

### Build simulator

Now the simmulator library is ready to be built by running

```{bash}
make
```

## Using the profiling tools

### Set up environment variables

Source the environment set up script, then load gcc version 8.2.0 and Intel 2019 update 5;

```{bash}
source <PATH-TO-INTEL-QNLP>/intel-qnlp/load_env.sh
module load gcc/8.2.0 intel/2019u5
cd ${QNLP_ROOT}
```

### Running the scripts

After setting up the environment variables, execute

```{bash}
sbatch <PERFORMANCE-ANALYSIS-SCRIPT>
```

where `<PERFORMANCE-ANALYSIS-SCRIPT>` is the appropriate profiling scipt - one of the following;

- run_MPI_vtune_aps.sh
- run_MPI_itac.sh
- run_MPI_vtune_amplxe.sh
- run_MPI_adapt.sh

The results of the analysis will be outputted into the directory `PROFILING_RESULTS`. To view the results the appropriate GUI application for that profiling type must be used.

Note: the provided scripts use some features which were only made available in Intel 2019 releases. These scripts were only tested using Intel 2019 update 5.

### Viewing the results with appropriate GUI

When launching the appropriate GUI to view the profiled results either shell forwarding must be enabled, else VNC can be used (preferable). Ensure the appropriate variable set-up script for that profiler was executed to update the environment variables after the appropriate module for Intel has been loaded (assuming some version of Intel 2019 was used), as shown below;

#### Intel Application Performance Snapshot

Simply open the resulting `.html` files to show results.

#### Intel Tace Analyser and Collector

```{bash}
source ${VTROOT}/bin/itacvars.sh
traceanalyzer
```

Open the corresponding results file in the GUI.

#### Intel VTUNE Amplifier

```{bash}
source ${VTUNE_AMPLIFIER_2019_DIR}/amplxe-vars.sh
amplxe-gui
```

Open the corresponding results file in the GUI.

#### Intel Advisor

```{bash}
source ${ADVISOR_XE_2019_DIR}/advixe-vars.sh
advixe-gui
```

Open the corresponding results file in the GUI.

# Determine best NUMA Node configuration 

The script `run_socket_node_config_perf.sh` can be run by specifying different NUMA node configurations for how many processes are to be run on each socket as well as their thread affinities. The execution times of an application for each configuration will be outputted.

From experimentation, the best NUMA node configurations was found to be binding each process to a single CPU, and only permitting 16 processes per socket (out of 20 CPUs).
