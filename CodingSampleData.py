import json
import numpy as np
import matplotlib.pyplot as plt


# Define the file path
#file_path = 'C:/Users/Acer/OneDrive/Documents/Phyton/vna_logmag_al1_2_r0_cd240711.txt'
file_path = 'C:/Users/Acer/OneDrive/Documents/Phyton/vna_phase_al1_2_r0_cd240711.txt'


# Read and process the file
x_data = []
y_data = []

with open(file_path, 'r') as file:
    data = json.load(file)

key = "0"
x, y = data[key]
x = np.array(x)
y = np.array(y)

plt.plot(x, y)
plt.show()


