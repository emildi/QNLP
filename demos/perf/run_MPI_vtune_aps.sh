#!/bin/bash
#SBATCH -J aps
#SBATCH -N 4
#SBATCH -p DevQ
#SBATCH -t 01:00:00
#SBATCH -A "ichec001"
#no extra settings

START_TIME=`date '+%Y-%b-%d_%H.%M.%S'`
DATE=`date '+%Y%m%d'`

PROFILING_RESULTS_PATH=PROFILING_RESULTS
APS_VTUNE_RESULTS_PATH=${PROFILING_RESULTS_PATH}/APS_VTUNE_RESULTS
EXPERIMENT_RESULTS_DIR=APS_VTUNE_RESULTS_${START_TIME}_job${SLURM_JOBID}

#################################################
### MPI job configuration.
###
### Note: User may need to modify.
#################################################

NNODES=4
NTASKSPERNODE=2
NTHREADS=1
NPROCS=$(( NTASKSPERNODE*NNODES ))

export OMP_NUM_THREADS=${NTHREADS}
export AFF_THREAD=${NTHREADS}
export KMP_AFFINITY=compact

#################################################
### Application configuration.
###
### Note: User may need to modify.
#################################################

PATH_TO_EXECUTABLE=${QNLP_ROOT}/build/demos/hamming_RotY
EXECUTABLE=exe_demo_hamming_RotY

EXE_VERBOSE=0
EXE_TEST_PATTERN=0
EXE_NUM_EXP=500
#EXE_NUM_EXP=25
#EXE_LEN_PATTERNS=7
EXE_LEN_PATTERNS=6

EXECUTABLE_ARGS="${EXE_VERBOSE} ${EXE_TEST_PATTERN} ${EXE_NUM_EXP} ${EXE_LEN_PATTERNS}"

#################################################
### Modify to load appropriate intel, gcc and 
### qhipster libraries.
###
### Note: User may need to modify.
#################################################

module load qhipster

#################################################
### Set-up Command line variables and Environment
### for APS_VTUNE.
###
### Note: User may need to modify.
#################################################

source ${VTUNE_AMPLIFIER_XE_2019_DIR}/apsvars.sh

# Collect internal Id;s of communicators
export APS_COLLECT_COMM_IDS=1

# Increase MPI Imbalance Collection 
export MPS_STAT_LEVEL=5 # 4 # Use 4 if too much info given with 5.

#################################################
### Set-up directory for APS_VTUNE results.
#################################################

[ ! -d "${PROFILING_RESULTS_PATH}" ] && mkdir -p "${PROFILING_RESULTS_PATH}"
[ ! -d "${APS_VTUNE_RESULTS_PATH}" ] && mkdir -p "${APS_VTUNE_RESULTS_PATH}"
[ ! -d "${APS_VTUNE_RESULTS_PATH}/${EXPERIMENT_RESULTS_DIR}" ] && mkdir -p "${APS_VTUNE_RESULTS_PATH}/${EXPERIMENT_RESULTS_DIR}"

#################################################
### Run application using APS_VTUNE 
### (also collects timing metrics).
#################################################

start_time=`date +%s`

# Run APS on App
mpirun -n ${NPROCS} -ppn ${NTASKSPERNODE} aps ${PATH_TO_EXECUTABLE}/${EXECUTABLE} ${EXECUTABLE_ARGS}

end_time=`date +%s`
runtime=$((end_time-start_time))

echo "Execution time: ${runtime}"


#################################################
### Generate APS report
#################################################

echo "--------------- Generate report -----------------"
aps --report=aps_result_${DATE}

echo "--------------- Generate Detailed report -----------------"
aps-report -x --format=html aps_result_${DATE}

#################################################
### Move result directory to sub directory
#################################################
echo "--------------- Moving Dir-----------------"
output=$( find . -maxdepth 1 -name "aps_report_${DATE}_*.html" )
echo $output
mv aps_result_${DATE} ${output} ${APS_VTUNE_RESULTS_PATH}/${EXPERIMENT_RESULTS_DIR}/

#################################################
### Copy slurm output to log file location
#################################################

cp slurm-${SLURM_JOBID}.out ${APS_VTUNE_RESULTS_PATH}/${EXPERIMENT_RESULTS_DIR}/slurm-${SLURM_JOBID}.out
