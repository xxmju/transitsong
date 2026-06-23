import lightkurve as lk
import matplotlib.pyplot as plt 
import numpy as np
from scipy.io.wavfile import write 
import sounddevice as sd
import matplotlib.animation as animation
from moviepy import *
from moviepy.video.fx import MultiplySpeed


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

        write(f"TIC{self.tic}_S{self.sector}_SONG.wav", samplerate, audio_arr)


    def make_video(self):
        x = self.time
        y = self.mapped_flux

        
        fig, ax = plt.subplots()
        line, = ax.plot([], [], marker='o', linestyle='', color='b') 
        ax.set_xlim(self.time[0], self.time[-1])
        ax.set_ylim(np.nanmin(self.mapped_flux)-20, np.nanmax(self.mapped_flux)+50)

        
        def update(frame):
            
            line.set_data(x[:frame], y[:frame])
            return line,

        
        ani = animation.FuncAnimation(
            fig, update, frames=len(x), interval=50, repeat=True
        )
        ani.save(f"TIC{self.tic}_S{self.sector}_DANCE.mp4", writer='ffmpeg', fps=30)
        #plt.show()

    def combine(self):
        video_clip = VideoFileClip(f"TIC{self.tic}_S{self.sector}_DANCE.mp4", audio=False)
        audio_clip = AudioFileClip(f"TIC{self.tic}_S{self.sector}_SONG.wav")


        video_factor = video_clip.duration / audio_clip.duration

        
        video_clip = video_clip.with_effects([MultiplySpeed(video_factor)])

        
        final_clip = video_clip.with_audio(audio_clip)

        
        final_clip.write_videofile(
            f"TIC{self.tic}_S{self.sector}_FINAL.mp4", 
            codec="libx264", 
            audio_codec="aac", 
            temp_audiofile="temp-audio.m4a",  
            remove_temp=True,                 
        )

       
        video_clip.close()
        audio_clip.close()
        final_clip.close()

#def play_song(Transit):
    # here is where we do the simultaneous thing?
tic = 124029677 
sector = 33

planet = Transit(tic, sector)
planet.make_sound_arr()
planet.make_video()
planet.combine()



