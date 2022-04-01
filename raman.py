import os
import re
import sys
from shutil import copyfile
import click
from get_mode import modes
import numpy as np
from ase import Atoms, Atom
from ase.io import read, write
from utilities import check_input_files, get_epsilon_from_OUTCAR, make_runner
from raman_plot import *

@click.group()
def cli():
    """ Welcome to Raman Analysis tools. you can use vasp hessian calculation outcar to find raman active modes. To learn more use: raman --help"""
    pass

@cli.command()
@click.option('--outcar',default='OUTCAR',help='Name of vasp Hessian calculation OUTCAR file')
@click.option('--first_mode',default=1,help='index of first Raman mode')
@click.option('--last_mode',default=-1,help='index of last Raman mode by default it will take all positive frequency ')
def calculate(outcar,first_mode,last_mode):
    """Calculate Raman Spectra from VASP hessian Calculation. Make sure you have OUTCAR file present in the current folder"""
    if check_input_files():
        POSCAR=read(outcar,index=1)
        initial_atom_position=POSCAR.get_positions()
        nat=len(initial_atom_position)
        num_modes= 3*nat # Number of vibration modes real and imaginary
        disps=[-1.0,1.0] # Atom displacement in positive and negative direction for evaluation of dq using 2 point 
        step_size=0.01
        start_mode=first_mode
        if last_mode==-1:
            last_mode=3*nat-3
        eigvals,eigvecs,norms=modes(outcar,nat)
        for m in range(len(eigvals)):
            print(eigvals[m])
        output_folder='active_raman'
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        crc_command=[]
        run_directory=click.prompt('Please enter the directory address where you will run the calculation: ')
        for mode_index in range(start_mode-1,last_mode):
            for j in range(len(disps)):
                folder_name=output_folder+'/%02d_%+d' % (mode_index+1, disps[j])
                if not os.path.isdir(folder_name):
                    os.mkdir(folder_name)
                #--------------Make poscar with +- shift -----------
                dq=np.array(eigvecs[mode_index])*step_size*disps[j]/norms[mode_index]
                poscar_nfh=POSCAR.copy()
                poscar_nfh.translate(dq)
                write(folder_name+'/POSCAR',poscar_nfh)
                copyfile('./INCAR', folder_name+'/INCAR')
                copyfile('./KPOINTS', folder_name+'/KPOINTS')
                copyfile('./POTCAR', folder_name+'/POTCAR')
                f=open('submit_script.crc','r')
                crc_name='{}.crc'.format('%02d_%+d' % (mode_index+1, disps[j]))
                g=open(folder_name+'/'+crc_name,'w')
                lines=f.readlines()
                new_lines=[]
                for line in lines:
                    if 'cd' in line:
                        line='cd {}\n'.format(run_directory+'/'+folder_name)
                    g.write(line)
                pre_crc_name='{}'.format('%02d_%+d' % (mode_index+1, disps[j]))
                fcrc_name=os.path.join(pre_crc_name,crc_name)
                crc_command.append('qsub -q long {}'.format(fcrc_name))
        make_runner(crc_command,run_directory)


@cli.command()
@click.option('--outcar',default='OUTCAR',help='If name of your OUTCAR file file is something else, then use --name name_of_your_outcar_file')
@click.option('--first_mode',default=1,help='index of first Raman mode')
@click.option('--last_mode',default=-1,help='index of last Raman mode by default it will take all positive frequency ')
#@click.option('--plot', is_flag=True, help='plot a Frequency Vs Raman intensity plot')
def analysis(outcar,first_mode,last_mode):
    """Analyse raman calculation output data and create raman.dat file. which can be plot using "raman plot" command"""
    outcar_fh=open(outcar,'r')
    poscar_fh=read(outcar,index=1)
    nat=len(poscar_fh.get_positions())
    out_folder='active_raman' 
    num_modes= 3*nat # Number of vibration modes real and imaginary

    disps=[-1.0,1.0] # Atom displacement in positive and negative direction for evaluation of dq using 2 point 
    step_size=0.01
    start_mode=first_mode
    if last_mode==-1:
            last_mode=3*nat-3
    vol=poscar_fh.get_volume()
    coeffs = [-0.5, 0.5]

    eigvals,eigvecs,norms=modes(outcar,nat)

    #--------------------------- Calculate Active Raman ----------------------
    activit=[]
    output_file=open('raman.dat','w')
    for mode_index in range(start_mode-1,last_mode):
        ra = [[0.0 for x in range(3)] for y in range(3)]
        for j in range(len(disps)):
            folder_name=out_folder +'/'+'%02d_%+d' % (mode_index+1, disps[j])
            if os.path.exists(folder_name):
                outcar_fh = open(folder_name+'/OUTCAR', 'r')
                problem_modes=[]
                try:
                    eps = get_epsilon_from_OUTCAR(outcar_fh)
                    outcar_fh.close()
                    for m in range(3):
                        for n in range(3):
                                ra[m][n]   += eps[m][n] * coeffs[j]/step_size * norms[mode_index] * vol/(4.0*np.pi)
                            #units: A^2/amu^1/2 =         dimless   * 1/A         * 1/amu^1/2  * A^3
                except RuntimeError:
                    problem_modes.append(mode_index)
                    pass
        
        alpha = (ra[0][0] + ra[1][1] + ra[2][2])/3.0
        beta2 = ( (ra[0][0] - ra[1][1])**2 + (ra[0][0] - ra[2][2])**2 + (ra[1][1] - ra[2][2])**2 + 6.0 * (ra[0][1]**2 + ra[0][2]**2 + ra[1][2]**2) )/2.0
        activit.append(45.0*alpha**2 + 7.0*beta2)
        print ("%10.5f %10.5f " % (eigvals[mode_index],45.0*alpha**2 + 7.0*beta2))
        output_file.write("%10.5f %10.5f \n" % (eigvals[mode_index],45.0*alpha**2 + 7.0*beta2))
    output_file.close()

@cli.command()
@click.option('--nplots',default=300,help='Number of Rmana frequency grid points for interpolation')
@click.option('--broad', default=5.0,help='Bordening parameter')
@click.option('--name',default='ramanSpectrum.pdf',help='Name for saving plot')
def plot(nplots,broad,name):
    """Plot Raman spectrum after brordening raman peak"""
    if os.path.isfile('raman.dat'):
        f,rho=getRho('raman.dat',nplots,broad)
        n_rho=normalize_raman(rho)
        mdplot(f,n_rho,name)
    else:
        print('raman.dat file missing. run "raman analysis" command first')
