import matplotlib.pyplot as plt
import numpy as np
import json
from lmfit import Model

# Configuration
logmagfile = r'C:\Users\Acer\OneDrive\Documents\Phyton\vna_logmag_al1_r0_cd240724.txt'
phasefile = r'C:\Users\Acer\OneDrive\Documents\Phyton\vna_phase_al1_r0_cd240724.txt'

datstart = 0
datend = 20000
prange = np.arange(0, -80, -5)
p0 = -40  # Change this value to the desired power level

def extract_data(filename):
    with open(filename, "r") as file:
        return json.load(file)

def s21_ideal(f, Ql, Qc, fr, phi):
    return 1 - (Ql / np.abs(Qc)) * np.exp(1j * phi) / (1 + 2j * Ql * (f / fr - 1))

def s21_real(f, Ql, Qc, fr, phi, a, alpha, tau):
    return a * np.exp(1j * alpha) * np.exp(-2j * np.pi * f * tau) * s21_ideal(f, Ql, Qc, fr, phi)

def fit_s21(freqr, S21data):
    def model_func(f, Ql, Qc, fr, phi, a, alpha, tau):
        return s21_real(f, Ql, Qc, fr, phi, a, alpha, tau)
    
    model = Model(model_func, independent_vars=['f'])
    params = model.make_params(Ql=1e4, Qc=1e4, fr=np.mean(freqr), phi=0, a=1, alpha=0, tau=0)
    
    result = model.fit(S21data, params, f=freqr)
    return result

def compute_qin_qext(freqr, S21data, fit_result):
    params = fit_result.params
    Ql = params['Ql'].value
    Qc = params['Qc'].value
    fr = params['fr'].value
    alpha = params['alpha'].value
    phi = params['phi'].value
    a = params['a'].value
    tau = params['tau'].value
    
    Qloaded = Ql * (1 + Qc / Ql)
    Qin = Ql
    Qext = Qc
    
    print(f"Qin: {Qin:.2e}")
    print(f"Qloaded: {Qloaded:.2e}")
    print(f"Qext: {Qext:.2e}")
    print(f"Alpha: {alpha:.2f}")
    print(f"Phi: {phi:.2f}")
    print(f"A: {a:.2f}")
    print(f"Tau: {tau:.2f}")

    return Qin, Qext, Qloaded

def plot_complex_plane(S21data, S21fit_data):
    plt.figure(figsize=(8, 6))
    plt.plot(np.real(S21data), np.imag(S21data), 'o', label='S21 Data', markersize=2)
    plt.plot(np.real(S21fit_data), np.imag(S21fit_data), color='orange', linestyle='-', label='Fitted S21')
    plt.xlabel("Re(S21)")
    plt.ylabel("Im(S21)")
    plt.legend()
    plt.grid(True)
    plt.title("Complex S21 Plane")
    plt.show()

def plot_magnitude(freqr, logmagdata, S21fit_data):
    plt.figure(figsize=(8, 6))
    plt.plot(freqr, logmagdata, label='S21 Data', color='blue')
    plt.plot(freqr, 20 * np.log10(np.abs(S21fit_data)), label='Fitted S21', color='orange', linestyle='-')
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("Magnitude [dB]")
    plt.legend()
    plt.grid(True)
    plt.title("Magnitude")
    plt.show()

def plot_phase(freqr, phasedata, S21fit_data):
    plt.figure(figsize=(8, 6))
    plt.plot(freqr, phasedata, label='S21 Data', color='blue')
    plt.plot(freqr, np.angle(S21fit_data, deg=True), label='Fitted S21', color='orange', linestyle='-')
    plt.xlabel("Frequency [GHz]")
    plt.ylabel("Phase [degrees]")
    plt.legend()
    plt.grid(True)
    plt.title("Phase")
    plt.show()

def main():
    # Extract data from JSON files
    extrlogmag = extract_data(logmagfile)
    extrphase = extract_data(phasefile)

    # Extract and process frequency, magnitude, and phase data
    logmagdata = np.array(extrlogmag["{}".format(p0)][1])[datstart:datend]
    phasedata = np.array(extrphase["{}".format(p0)][1])[datstart:datend]
    freqr = np.array(extrlogmag["{}".format(prange[0])][0])[datstart:datend]

    S21data = 10.**(logmagdata/20.)*np.exp(1j*phasedata/180.*np.pi)

    # Fit the S21 data
    S21fit_result = fit_s21(freqr, S21data)

    # Compute and print Qin, Qloaded, and Qext
    Qin, Qext, Qloaded = compute_qin_qext(freqr, S21data, S21fit_result)

    # Plot results
    S21fit_data = S21fit_result.best_fit
    plot_complex_plane(S21data, S21fit_data)
    plot_magnitude(freqr, logmagdata, S21fit_data)
    plot_phase(freqr, phasedata, S21fit_data)

if __name__ == "__main__":
    main()
