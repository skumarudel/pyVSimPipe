qsub_header_template='''#!/bin/bash
#SBATCH -n {ppn}
#SBATCH -o {qsub_dir}/{name}.out
#SBATCH -e {qsub_dir}/{name}.err
#SBATCH --account={account}
#SBATCH --job-name={name} 
#SBATCH --mem=1G 
{optional_pbs_directive}

{init_command}

'''

