import numpy as np
import sounddevice as sd 
import lightkurve as lk
import matplotlib.pyplot as plt 

tic = "0001045298"
sector = 4

search_result = lk.search_lightcurve(
        f"TIC {tic}",
        mission="TESS",
        author="SPOC",
        sector =[sector]
    )

lc = search_result.download()

lc_binned = lc.bin(time_bin_size=0.01)

lc_fluxes = lc_binned.flux.value
lc_times = lc_binned.time.value

samplerate = 44100
duration = 0.05

med_value = np.median(lc_fluxes)
lc_normflux = lc_fluxes/med_value

#central_val = 440 # hz 
max_val = 400
min_val = 250

# normalize to frequencies 
mapped_flux = (lc_normflux - np.min(lc_normflux)) / (np.max(lc_normflux) - np.min(lc_normflux)) * (max_val - min_val) + min_val

audio = []
len_points = []

for flux in mapped_flux[:600]: #[:600]:
    frequency = flux 
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    
    audio_signal = np.sin(2*np.pi*frequency*t)
    audio_signal = audio_signal[~np.isnan(audio_signal)]
    len_points.append(len(audio_signal))
    
    audio.extend(audio_signal)

audio_arr = np.array(audio)
    
