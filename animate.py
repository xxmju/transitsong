import matplotlib.pyplot as plt
import numpy as np

def make_animation(mapped_flux, lc_times):
    
    plt.scatter(lc_times[1580:1650], mapped_flux[1580:1650])