import os
from os import path

def check_input_files():
    all_present=True
    outcar_exists=os.path.isfile('OUTCAR')
    submit_script_exists=os.path.isfile('submit_script.crc')
    incar_exists=os.path.isfile('INCAR')
    potcar_exists=os.path.isfile('POTCAR')
    kpoints_exists=os.path.isfile('KPOINTS')
    
    if not outcar_exists:
        print('OUTCAR of hessian calculation doesnot exist in this folder.')
        all_present=False
    elif not incar_exists:
        print('Please provide a INCAR file for Raman Calculation')
        all_present=False
    elif not kpoints_exists:
        print('Please provide a KPOINTS file for Raman Calculation')
        all_present=False
    elif not potcar_exists:
        print('Please provide a POTCAR file for Raman Calculation')
        all_present=False
    elif not submit_script_exists:
        print('Please provide a submit_script.crc file for Raman Calculation')
        all_present=False
    else:
        print('INCAR, KPOINTS, POTCAR, OUTCAR, submit_script.crc all file exists')
    return all_present

def check_run_complete(outcar_path):
    search="General timing and accounting informations for this job:"
    complete=False
    if  path.exists(outcar_path):
        with open(outcar_path) as myfile:
            if search in myfile.read():
                complete=True
            else:
                print('Wait ! calculation is still running. if your job status shows complete then something went wrong and your job stooped before completion')
    else:
         print("{} does not exist".format(outcar_path))
    return complete


def get_epsilon_from_OUTCAR(outcar_fh):
    epsilon = []
    #
    outcar_fh.seek(0) # just in case
    while True:
        line = outcar_fh.readline()
        if not line:
            break
        #
        #if "MACROSCOPIC STATIC DIELECTRIC TENSOR" in line:
        if "MICROSCOPIC" in line:
            outcar_fh.readline()
            epsilon.append([float(x) for x in outcar_fh.readline().split()])
            epsilon.append([float(x) for x in outcar_fh.readline().split()])
            epsilon.append([float(x) for x in outcar_fh.readline().split()])
            return epsilon
    raise RuntimeError("[get_epsilon_from_OUTCAR]: ERROR Couldn't find dielectric tensor in OUTCAR")
    return 1

def make_runner(crc_command,run_directory):
    with open('active_raman/run','w') as run_file:
        run_file.write('#!/usr/bin/python \n')
        run_file.write('import os \n')
        for command in crc_command:
            run_file.write('os.system(\'{}\')\n'.format(command))
    run_file.close()
    instruction="""1. uplaod active_raman folder in {} folder of crc \n
                   2. goto crc and inside {}/active_raman folder \n
                   3. type: chmod +x run \n
                   4. type: ./run \n
                   5. after job is complete, download this active_raman folder to the same local directory \n """.format(run_directory,run_directory)
    print(instruction)