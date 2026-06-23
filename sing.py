import sounddevice as sd
import numpy as np

def make_sound(mapped_flux):
    freq_maps = ()

    samplerate = 44100
    duration = 0.05


    for flux in mapped_flux[1580:1650]:
        frequency = flux 
        t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
        
        audio_signal = 0.5 * np.sin(2*np.pi*frequency*t)

        sd.play(audio_signal, samplerate)
        sd.wait()