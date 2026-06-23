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
        med_value = np.nanmedian(lc_fluxes)

        lc_normflux = lc_fluxes/med_value

        self.time = lc_times
        self.norm_flux = lc_normflux


    def make_sound_arr(self, max_val=900, min_val=200):

        mapped_flux = (self.norm_flux - np.nanmin(self.norm_flux)) / (np.nanmax(self.norm_flux) - np.nanmin(self.norm_flux)) * (max_val - min_val) + min_val

        self.mapped_flux = mapped_flux

        audio = []
        len_points = []

        samplerate = 44100
        duration = 0.05

        for flux in mapped_flux: 
            frequency = flux 
            t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
            
            audio_signal = np.sin(2*np.pi*frequency*t)
            audio_signal = audio_signal[~np.isnan(audio_signal)]
            len_points.append(len(audio_signal))
            
            audio.extend(audio_signal)

        audio_arr = np.array(audio)
        self.audio_arr = audio_arr

        sd.play(audio_arr, samplerate)
        sd.wait()


    #def make_animation(self):
        

#def play_song(Transit):
    # here is where we do the simultaneous thing?
tic = 124029677 
sector = 33

planet = Transit(tic, sector)
planet.make_sound_arr()

# feature 2 code 
print("i am in feature 2")




