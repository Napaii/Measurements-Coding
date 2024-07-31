import matplotlib.pyplot as plt
import numpy as np
import json
import matplotlib as mpl
import S11fit
import sys
import os
from scipy.optimize import curve_fit

mpl.rcParams['figure.dpi'] = 100

def Qfun(x, Gi, Gp, nc, alpha):
    return (Gi + Gp / (1 + (x / nc)**alpha)**0.5)

def Qfunl(x, Gi, Gp, nc, alpha):
    return np.log(Gi + Gp / (1 + (x / nc)**alpha)**0.5)

def extract_data(filename):
    try:
        with open(filename, "r") as r:
            return json.load(r)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return {}

Qin, Qex, fr, nphot = [], [], [], []
hPlanck = 6.626e-34
save_dir = 'C:/Users/Acer/OneDrive/Pictures/Sample1/'  # Define save_dir

# Redirect standard output to a text file
original_stdout = sys.stdout
with open(os.path.join(save_dir, 'OutputForPowerFitting.txt'), 'w') as f:
    sys.stdout = f

    #File can be change
    # File paths
    logmagfile = 'C:/Users/Acer/OneDrive/Documents/Phyton/vna_logmag_al1_r0_cd240724.txt'
    phasefile = 'C:/Users/Acer/OneDrive/Documents/Phyton/vna_phase_al1_r0_cd240724.txt'

    indstart = 0
    indend = 15
    datstart = 0
    datend = 20000

    extrlogmag = extract_data(logmagfile)
    extrphase = extract_data(phasefile)

    prange = np.arange(0, -80, -5)
    inputatt = -82  # Estimate of attenuation of input line
    p0 = -75

    # Define frequency range based on data
    try:
        freqr = np.array(extrlogmag[str(prange[0])][0])[datstart:datend]
        print(f"Frequency data loaded: {freqr[:5]} ...")
    except KeyError:
        print("Error: Missing frequency data in the logmag file.")
        freqr = np.array([])

    for cpow in prange[indstart:indend]:
        print(f"Processing power: {cpow} dBm")
        
        try:
            logmagdata = np.array(extrlogmag[str(cpow)][1])[datstart:datend]
            phasedata = np.array(extrphase[str(cpow)][1])[datstart:datend]
        except KeyError as e:
            print(f"Error extracting data for power {cpow}: {e}")
            continue
        
        S21data = 10.**(logmagdata / 20.) * np.exp(1j * phasedata / 180. * np.pi)
        
        if len(freqr) == 0:
            print(f"Error: Frequency data is not defined for power {cpow}.")
            continue

        try:
            pars = S11fit.fit(freqr, S21data, ftype='B', trimwidth=25)
            curQin = pars[0]['Qint'].value
            curQex = pars[0]['Qext'].value
            curfr = pars[0]['f0'].value
            
            Qin.append(curQin)
            Qex.append(curQex)
            fr.append(curfr)
            
            PowindB = cpow + inputatt
            Powin = 1e-3 * 10**(PowindB / 10)
            curnph = Powin / hPlanck / curfr**2 * curQin**2 * curQex / np.pi / (curQin + curQex)**2
            
            nphot.append(curnph)
        except Exception as e:
            print(f"Error during fitting for power {cpow}: {e}")

    Qin = np.array(Qin)
    Qex = np.array(Qex)
    fr = np.array(fr)
    nphot = np.array(nphot)

    if len(nphot) > 0 and len(Qin) > 0:
        pf = nphot[np.arange(indstart, indend, 1)]
        Gf = np.log(1 / Qin[np.arange(indstart, indend, 1)])

        try:
            fpars, _ = curve_fit(Qfunl, pf, Gf, p0=[1e-7, 3e-6, 1e3, 0.5], bounds=[0, np.inf], ftol=1e-10, gtol=1e-10, maxfev=10000)
            print(f"Fitted parameters: {fpars}")
        except Exception as e:
            print(f"Error during curve fitting: {e}")
            fpars = [np.nan, np.nan, np.nan, np.nan]

        xx = np.arange(0, 9, 0.1)
        gi = np.arange(indstart, indend, 1)

        figures = []

        try:
            fig1, ax1 = plt.subplots()
            ax1.loglog(nphot[gi], 1 / Qin[gi], label='Data')
            ax1.loglog(10**xx, np.exp(Qfunl(10**xx, *fpars)), label='Fit')
            ax1.set_xlabel('Photon number', fontsize=16)
            ax1.set_ylabel('1/Qi', fontsize=16)
            ax1.legend()
            figures.append(fig1)

            fig2, ax2 = plt.subplots()
            ax2.semilogy(prange[gi], Qin[gi], label='Qin')
            ax2.set_xlabel('Power', fontsize=16)
            ax2.set_ylabel('Qi', fontsize=16)
            ax2.legend()
            figures.append(fig2)

            fig3, ax3 = plt.subplots()
            ax3.plot(prange[gi], Qex[gi], label='Qex')
            ax3.set_xlabel('Power', fontsize=16)
            ax3.set_ylabel('Qe', fontsize=16)
            ax3.legend()
            figures.append(fig3)

            fig4, ax4 = plt.subplots()
            ax4.plot(prange[gi], fr[gi] / 1e9, label='fr')
            ax4.set_xlabel('Power', fontsize=16)
            ax4.set_ylabel('fr (GHz)', fontsize=16)
            ax4.legend()
            figures.append(fig4)

            # Show and save each figure
            for i, fig in enumerate(figures, 1):
                plt.show(block=False)  # Show the plot without blocking
                fig.savefig(f"{save_dir}plot{i}.png")  # Save the plot
                plt.pause(5)  # Pause for 5 seconds to view the plot
                plt.close(fig)  # Close the plot window

        except Exception as e:
            print(f"Error during plotting: {e}")
    else:
        print("Error: No valid data for fitting and plotting.")

# Restore standard output
sys.stdout = original_stdout
