#!/bin/bash -l

#SBATCH --job-name=pretrain # Job name
#SBATCH --output=gpujob.%j.out # Stdout (%j expands to jobId)
#SBATCH --error=gpujob.%j.err # Stderr (%j expands to jobId)
#SBATCH --ntasks=1 # Total number of tasks
#SBATCH --gres=gpu:1 # GPUs per node
#SBATCH --nodes=1 # Total number of nodes requested
#SBATCH --ntasks-per-node=1 # Tasks per node
#SBATCH --cpus-per-task=10 # Threads per task
#SBATCH --mem=47000 # Memory per job in MB
#SBATCH -t 47:00:00 # Run time (hh:mm:ss) - (max 48h)
#SBATCH --partition=gpu # Run on the GPU nodes queue
#SBATCH -A pa210903 # Accounting project

# Load any necessary modules
module purge
module load gnu/8
module load cuda/10.1.168
module load pytorch/1.8.0

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export HF_DATASETS_OFFLINE="1"

# Launch the executable
cd $HOME/projects/Data2Text
srun python3.8 entry_point.py --config_file configs/aris/pretrain/pretrain_t5_base_all_tasks.yaml --job_type pretrain
