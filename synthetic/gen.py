import numpy as np
from numpy import random
import matplotlib.pyplot as plt

random.seed(2024)

SD_DIFF_FACTOR = 5e-2
BIAS_FACTOR = 1e-4

def next(mean, std_dev, prev):
  # bias the diff depending on how far we are from the mean.
  norm_diff_mean = BIAS_FACTOR * (prev - mean) / std_dev
  diff = random.normal(-norm_diff_mean, std_dev * SD_DIFF_FACTOR)
  return prev + diff

mean = 700
std_dev = 200
t_max = 1000
current = random.normal(mean, std_dev)
values = []

for t in range(t_max):
  next_val = next(mean, std_dev, current)
  values.append(next_val)
  current = next_val

fig, ax = plt.subplots()
ax.plot(np.arange(t_max), values)
ax.set(xlabel='time (s)', ylabel='value')
ax.grid()

plt.show()
