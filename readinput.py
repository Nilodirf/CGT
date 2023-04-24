import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import constants as sp
from scipy import interpolate as ipl
import os
import sys

from classes import samplechoice



###Here you define the parameters for the Gaussian pump pulse
pump_fluence=1.3                                                                     #fluence of optical pulse in mJ/cm^2 (center of gaussian)
pump_sigma=0.050e-12                                                               #sigma of gaussian pulse in s
pump_delay=1.0e-12                                                                 #offset of maximum of gaussian laser pulse in s

pump_fluence=pump_fluence/np.sqrt(2*np.pi)/pump_sigma*10                              # recalculate to to W/m^2 for the pump profile calculated below and in tempdyn.py

### Here you prepare your sample!
sam=[samplechoice('hBN'), samplechoice('CGT'), samplechoice('SiO2')]       #Choose what elements you want to stick together (N constituents):
samplesize=[13, 73, 367]
samplesize_t=[samplesize[i]*int(sam[i].dz*1e10) for i in range(len(sam))]

#Choose the layer thickness of each constituent (units of dz). hBN: 10-20 nm. dz=7.71 AA. Number of layers: 15e-9/7.71e-10=19.43. CGT_2 flake: 15 nm. dz=20.531 AA. Number of layers: 15e-9/20.531e-10=7
pendep=['inf', 30e-9, 'inf']                                                       #penetration depth of pump pulse in each constituent                                                                
nj=sum(samplesize)+0                                                                    #total film thickness


###Here you define the coupling constants for heat diffusion, spin diffusion and exchange coupling between constituents:
kint=[100., 100.]
kphint=[5.52, 5.52]                                                                 #interface thermal consuctivities between constituents (N-1)
musint=[0., 0.]                                                                    #interace spin diffusion constants (N-1)
Jint=[0., 0.]                                                                      #interface exchange coupling (N) (see exch. coupling definition in the sample class)



###Here you define inital temperature  and longitudinal external magnetic field
initemp=6.                                                                       #initial temperature of electron and phonon bath [K]
h_ext=0.0                                                                           #external magnetic field


####Here you define the simulation time parameters
dt=1e-18                                                                           #timestep of simulation in s
simlen=1.1e-9                                                                      #length of simulation in s
simlen =int(simlen/dt)


qes=1                                                                              #[1,0] if 0, energy flow between electron and spin system is deactivated. if 1, it is activated
qpos=1
qpas=0                                                                              #same for lattice spin-lattice energy exchange in m5tm




















###The following is all automized and should not be changed
alexpump=False
fpflo=False


Jint=[0.]+Jint+[0.]                                                       

if len(sam)==1:
    kint=[0.]
    kphint=[0.]
    musint=[0.]
    Jint=[0., 0.]
    sam[0].kappa=0
    sam[0].kappaph=0


if alexpump:
    pumpfile=open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'3TM_Data/Pump.txt'),'r')
    dpump=np.array([float(i)**2 for i in pumpfile.readlines()])*pump_power
    t=np.arange(len(dpump))*2e-14-2.04e-12+pump_delay
    pump=ipl.interp1d(t,dpump, fill_value=(0,0), bounds_error=False)


#exchange coupling constants of multilayers. This prepares for easier handling of the constants in later use in functions, it is only computed once:
Jints=[[Jint[i], Jint[i+1]] for i in range(len(sam))]
Jhere=[[sample.J*sample.coupl[1] for i in range(samplesize[j])] for j, sample in enumerate(sam)]

Jnext=[[] for i in sam]
for i, sample in enumerate(sam):
    for j in range(samplesize[i]-1):
        Jnext[i].append(sample.J*sample.coupl[-1])
    Jnext[i].append(Jints[i][1])

Jlast=[[] for i in sam]
for i, sample in enumerate(sam):
    Jlast[i].append(Jints[i][0])
    for j in range(samplesize[i]-1):
        Jlast[i].append(sample.J*sample.coupl[0])


Jlochere=[[sample.Jloc*sample.coupl[1] for i in range(samplesize[j])] for j, sample in enumerate(sam)]
Jlocnext=[[] for i in sam]
for i, sample in enumerate(sam):
    for j in range(samplesize[i]-1):
        Jlocnext[i].append(sample.Jloc*sample.coupl[-1])
    Jlocnext[i].append(Jints[i][1])
Jloclast=[[] for i in sam]
for i, sample in enumerate(sam):
    Jloclast[i].append(Jints[i][0])
    for j in range(samplesize[i]-1):
        Jloclast[i].append(sample.Jloc*sample.coupl[0])
        
        
#Compute the Lambert-Beer absorption profile:
def pump(flu):
    pump_profile=[]
    for i, sample in enumerate(sam):
        if pendep[i]=='inf':
            pump_profile.append(np.array([0 for j in range(samplesize_t[i])]))
        else:
            pump_profile.append(np.array([flu/pendep[i]*np.exp(-j*sample.dz/pendep[i]) for j in range(samplesize_t[i])]))
            flu=pump_profile[i][-1]
    return pump_profile
    
pp=pump(pump_fluence)

def get_abs_fluence(pump_profile):
    abs_fluence=0
    for i, sample in enumerate(sam):
        abs_fluence+=sum(pump_profile[i]*sample.dz)*np.sqrt(2*np.pi)*pump_sigma
    print(abs_fluence)
    return abs_fluence
    
abs_flu=get_abs_fluence(pp)

#set up a grid of grain sizes dz for the computation of diffusion:
def get_dz_array():
    dz_nested_list=[[sam[i].dz for _ in range(samplesize[i])] for i in range(len(sam))]
    dz_flat = []
    for sublist in dz_nested_list:
        for item in sublist:
            dz_flat.append(item)
    return np.array(dz_flat)

dz_arr=get_dz_array()

def get_kappa_arrays():
    kappae_nested_list=[[sam[i].kappa for _ in range(samplesize[i])] for i in range(len(sam))]
    kappae_flat = []
    for sublist in kappae_nested_list:
        for item in sublist:
            kappae_flat.append(item)

    kappap_nested_list = [[sam[i].kappaph for _ in range(samplesize[i])] for i in range(len(sam))]
    kappap_flat = []
    for sublist in kappap_nested_list:
        for item in sublist:
            kappap_flat.append(item)

    return np.array(kappae_flat), np.array(kappap_flat)

kappae_arr, kappap_arr=get_kappa_arrays()

def get_c_g_arrays():
    ce_list = [mat.celfit for mat in sam]
    cp_list = [mat.cphfit for mat in sam]
    gep_list=[mat.gepfit for mat in sam]

    return ce_list, cp_list, gep_list

ce_arr, cp_arr, gep_arr =get_c_g_arrays()


def get_spin_diff_coeff_map():
    D_to_next=[]
    D_to_last=[]
    for i, sample in enumerate(sam):
        if math.isclose(sample.musdiff, 0., abs_tol=1e-4):
            D_to_next.append(np.zeros(samplesize[i]))
            D_to_last.append(np.zeros(samplesize[i]))

        else:
            D_to_next.append(np.array([sample.musdiff/sample.dz**2 for _ in range(samplesize[i])]))
            D_to_last.append(np.array([sample.musdiff/sample.dz**2 for _ in range(samplesize[i])]))
            if i<len(sam)-1:
                D_to_next[i][-1]*=musint[i]/sample.musdiff
            if i>0:
                D_to_last[i][0]*=musint[i-1]/sample.musdiff*sample.dz**2/sam[i-1].dz**2

    return D_to_next, D_to_last
    
D_to_next, D_to_last=get_spin_diff_coeff_map()
    
#### This is the list of parameters given to output.output() (after possible modification in main file). All sample parameters are stored in the list of class object 'sam'
param={ 'filename':'AuNiTa', 'sam':sam,                 # file name and all parameters of all constituents stored in sam
        'ss': samplesize,  'sst': samplesize_t, 'nj':nj,                     # tickness of all constituents [in layers] and the total sampledepth
        'dt':dt, 'simlen':simlen,                       # timestep and simulation length [in dt]
        'pdel':pump_delay, 'psig':pump_sigma, 'pp':pp, 'pendep':pendep, 'power_input':pump_fluence, #pump pulse parameters
        'hex':h_ext,  'initemp':initemp,                # external field in magnetization direction and initial temperatures
        'jint':Jints, 'kint': kint, 'kphint': kphint, 'musint':musint,    # interface constants for exch. coupl., el. therm. diff., and spin diff. of length len(sam)-1
        'Jhere':Jhere, 'Jlast': Jlast, 'Jnext':Jnext, 'Jlochere':Jlochere, 'Jloclast':Jloclast, 'Jlocnext':Jlocnext, # automized, do not change
        'ap':alexpump, 'qes':qes, 'qpas': qpas, 'qpos':qpos, 'fpflo':fpflo,
        'kappae_arr': kappae_arr, 'kappap_arr': kappap_arr, 'abs_flu':abs_flu, 'Dtn':D_to_next, 'Dtl':D_to_last, 'dz_arr':dz_arr,
        'ce_arr': ce_arr, 'cp_arr':cp_arr, 'gep_arr': gep_arr}

### Warnings if the interface constants do not match the number of constituents

if len(kint) != len(sam)-1 and len(sam)!=1:
    print('The number of interface thermal conductivities does not match the number of samples (len(kint) != len(sam)-1)')
    
if len(Jint) != len(sam)+1 and len(sam)!=1:
    print('The number of interface exchange coupling constants does not match the number of samples (len(Jint) != len(sam)+1)')

if len(musint) != len(sam)-1 and len(sam)!=1:
    print('The number of interface spin transport coefficients does not match the number of samples (len(musint) != len(sam)-1)')

if len(pendep) !=len(sam) and len(sam)!=1:
    print('The number of optical penetration depths does not match the number of samples (len(pendep) != len(sam))')
    




