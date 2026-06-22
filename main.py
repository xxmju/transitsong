import lightkurve as lk
import matplotlib.pyplot as plt 
import numpy as np
import sounddevice as sd


class Transit:
    def __init__(self, tic, sector):
        self.tic = tic
        self.sector = sector


        search_result = lk.search_lightcurve(
            f"TIC {tic}",
            mission="TESS",
            author="SPOC",
            sector =[sector] )

        lc = search_result.download()

        lc_binned = lc.bin(time_bin_size=0.01)

        lc_fluxes = lc_binned.flux.value
        lc_times = lc_binned.time.value

        lc_normflux = lc_fluxes/med_value

        self.time = lc_times
        self.norm_flux = lc_normflux

    


    def make_sound(self, max_val=900, min_val=200):

        mapped_flux = (lc_normflux - np.nanmin(lc_normflux)) / (np.nanmax(lc_normflux) - np.nanmin(lc_normflux)) * (max_val - min_val) + min_val

        self.mapped_flux = mapped_flux

    def make_animation(self):
        





