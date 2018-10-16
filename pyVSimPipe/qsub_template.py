qsub_header_template='''
#!/bin/bash
#PBS -l nodes={nodes}:ppn={ppn}
#PBS -N {name} 
#PBS -o {qsub_dir}/{name}.out
#PBS -e {qsub_dir}/{name}.err
{optional_pbs_directive}

{init_command}

'''

