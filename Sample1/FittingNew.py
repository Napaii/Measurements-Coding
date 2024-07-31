import matplotlib.pyplot as plt
import numpy as np
import json
import matplotlib as mpl
import S11fit
from scipy.optimize import curve_fit
from scipy.interpolate import make_interp_spline, PchipInterpolator, Akima1DInterpolator
import sys
import os

mpl.rcParams['figure.dpi'] = 100

def Qfun(x, Gi, Gp, nc, alpha):
    return Gi + Gp / (1 + (x / nc))**alpha

def Qfunl(x, Gi, Gp, nc, alpha):
    return np.log(Gi + Gp / (1 + (x / nc))**alpha)

def extract_data(filename):
    with open(filename, "r") as r:
        r = r.read()
        raw = json.loads(r)
    return raw

def smooth_curve(x, y):
    """Smooths the curve using spline interpolation."""
    if len(x) == 0 or len(y) == 0:
        return x, y
    x_smooth = np.linspace(min(x), max(x), 500)
    spline = make_interp_spline(x, y, k=3)
    y_smooth = spline(x_smooth)
    return x_smooth, y_smooth

# Directory to save plots
save_dir = 'C:/Users/Acer/OneDrive/Pictures/Sample1'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Redirect standard output to a text file
original_stdout = sys.stdout
with open(os.path.join(save_dir, 'outputFittingNew.txt'), 'w') as f:
    sys.stdout = f

    #File can be change
    #File path
    logmagfile = 'C:/Users/Acer/OneDrive/Documents/Phyton/vna_logmag_al1_2_r0_cd240711.txt'
    phasefile = 'C:/Users/Acer/OneDrive/Documents/Phyton/vna_phase_al1_2_r0_cd240711.txt'

    datstart = 0
    datend = 20000

    extrlogmag = extract_data(logmagfile)
    extrphase = extract_data(phasefile)

    prange = np.arange(0, -80, -5)

    freqr = np.array(extrlogmag["{}".format(prange[0])][0])[datstart:datend]

    inputatt = -67  # Estimate of attenuation of input line

    p0 = -75
    logmagdata = np.array(extrlogmag["{}".format(p0)][1])[datstart:datend]
    phasedata = np.array(extrphase["{}".format(p0)][1])[datstart:datend]
    S21data = 10.**(logmagdata / 20.) * np.exp(1j * phasedata / 180. * np.pi)

    try:
        pars0 = S11fit.fit(freqr, S21data, ftype='B', doplots=False, trimwidth=25)
        S11fun = S11fit.S11full(pars0[1], pars0[0], ftype='B')
        print(f"Fitting parameters: {pars0}")
    except Exception as e:
        print(f"Error during fitting: {e}")
        pars0 = [None, None]
        S11fun = None

    # Plotting the Real Part of S21 and Fit
    if pars0[1] is not None and S11fun is not None:
        fig1, ax1 = plt.subplots(figsize=(8, 5))  # Smaller figure size
        ax1.plot(freqr, np.real(S21data), label='Real S21data')
        ax1.plot(pars0[1], np.real(S11fun), label='Fitted S11')
        ax1.set_title("Real Part of S21 and Fitted S11")
        ax1.set_xlabel("Frequency (GHz)")
        ax1.set_ylabel("Real Part")
        ax1.legend()
        fig1.savefig(os.path.join(save_dir, 'Real_S21_Fit.png'))  # Save plot

        # Plotting the Imaginary Part of S21 and Fit
        fig2, ax2 = plt.subplots(figsize=(8, 5))  # Smaller figure size
        ax2.plot(freqr, np.imag(S21data), label='Imag S21data')
        ax2.plot(pars0[1], np.imag(S11fun), label='Fitted S11')
        ax2.set_title("Imaginary Part of S21 and Fitted S11")
        ax2.set_xlabel("Frequency (GHz)")
        ax2.set_ylabel("Imaginary Part")
        ax2.legend()
        fig2.savefig(os.path.join(save_dir, 'Imag_S21_Fit.png'))  # Save plot

        # Display all plots at the same time
        plt.show(block=False)
        plt.pause(1)  # Pause to allow plots to render

        # Close plots after rendering
        plt.close(fig1)
        plt.close(fig2)

    else:
        print("Error: S11fit did not return valid results.")

    # Restore standard output
    sys.stdout = original_stdout
