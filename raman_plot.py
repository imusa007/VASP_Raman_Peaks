import matplotlib.pyplot as plt
import math
import matplotlib
from matplotlib.ticker import MultipleLocator
import numpy as np

def getRho(filename,nplots,broad):
    hw=np.genfromtxt(filename,dtype=float)
    freq=hw[:,0]
    amp=hw[:,1]
    fmax = np.max(freq)
    fmin = np.min(freq)
    f=np.linspace(0.8*fmin,1.2*fmax,num=nplots)
    rho=[]

    for i in range(nplots):
        r=0.0
        for j in range(len(freq)):
            x=(f[i]-freq[j])/broad
            r=r+amp[j]*delta(x)
            if r<1.0e-20:
                r=0.0
        rho.append(r)
    rho=np.array(rho)
    return f,rho


def delta(x):
    d=np.exp(-1.0*x*x/2.0)
    return d

def normalize_raman(rho):
    rho_min=np.min(rho)
    rho_max=np.max(rho)
    d_rho=rho_max-rho_min
    rho=(rho-rho_min)/d_rho
    return rho

def mdplot(x,y,name):
    fig, ax = plt.subplots(figsize=(12,8))

    Nmajor_yticks=np.abs(np.max(y)-np.min(y))/9
    Nminor_yticks =Nmajor_yticks/5.0
    
    Nmajor_xticks=math.floor(np.abs(np.max(x)-np.min(x))/17)
    Nminor_xticks =Nmajor_xticks/5.0
    
    
    plt.ylabel('Raman Intensity',size=15)
    plt.xlabel('Frequency $cm^{-1}$',size=15)
    
    plt.xlim(np.min(x),np.max(x))
    
    plt.plot(x,y,color='#4b1082', linewidth=4,linestyle='-')
    #Major ticks
    ax.xaxis.set_major_locator(MultipleLocator(Nmajor_xticks))
    ax.yaxis.set_major_locator(MultipleLocator(Nmajor_yticks))
    
    #Minor ticks
    ax.xaxis.set_minor_locator(MultipleLocator(Nminor_xticks))
    ax.yaxis.set_minor_locator(MultipleLocator(Nminor_yticks))
    
    #tick param
    ax.tick_params(which="major",direction="out",length=7,width=3,labelsize=13)
    ax.tick_params(which="minor",direction="out",length=4,width=2,labelsize=13)
    
    plt.savefig(name,bbox_inches='tight')
