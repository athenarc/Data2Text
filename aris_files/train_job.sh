#!/bin/bash -l

#SBATCH --job-name=debug_train # Job name
#SBATCH --output=gpujob.%j.out # Stdout (%j expands to jobId)
#SBATCH --error=gpujob.%j.err # Stderr (%j expands to jobId)
#SBATCH --ntasks=1 # Total number of tasks
#SBATCH --gres=gpu:1 # GPUs per node
#SBATCH --nodes=1 # Total number of nodes requested
#SBATCH --ntasks-per-node=1 # Tasks per node
#SBATCH --cpus-per-task=10 # Threads per task
#SBATCH --mem=12000 # Memory per job in MB
#SBATCH -t 01:00:00 # Run time (hh:mm:ss) - (max 48h)
#SBATCH --partition=gpu # Run on the GPU nodes queue
#SBATCH -A pa210903 # Accounting project

# Load any necessary modules
module purge
module load gnu/8
module load cuda/10.1.168
module load pytorch/1.8.0

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Launch the executable
#pip install -r aris_requirements.txt
cd $HOME/projects/Data2Text
#source venv/bin/activate

#srun python3.8 entry_point.py --config_file configs/aris/pretrain/pretrain_t5_small_all_tasks.yaml --job_type pretrain
srun python3.8 entry_point.py
#srun python3 test.py
