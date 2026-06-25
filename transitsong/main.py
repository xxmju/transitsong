import lightkurve as lk
import matplotlib.pyplot as plt 
import numpy as np
from scipy.io.wavfile import write 
import sounddevice as sd
import matplotlib.animation as animation
from moviepy import *
from moviepy.video.fx import MultiplySpeed
import os 
from pathlib import Path

#set matplotlib preferences
plt.style.use(os.getcwd() + '/text.mplstyle')


class Transit:
    """A program that makes an animation with audio for an input TESS lightcurve.

    Attributes:
        tic (int or str): TESS Input Catalog number
        sector (int): TESS sector number
        window (list of length 2): start and end days of sector
    """

    def __init__(self, tic, sector, window = None):
        self.tic = tic
        self.sector = sector
        self.window = window

        try:
            search_result = lk.search_lightcurve(
                f"TIC {tic}",
                mission="TESS",
                author="SPOC",
                sector =[sector] )
            
            lc = search_result.download()
            self.success = True

        except Exception as e:
            self.success = False
            raise ValueError("Failed to load lightcurve for TIC {} in sector {}: {}".format(tic, sector, str(e)))

        print("Successfully loaded lightcurve for TIC {} in sector {}".format(tic, sector))

        lc_binned = lc.bin(time_bin_size=0.01)

        lc_binned = lc_binned.normalize()

        lc_fluxes = lc_binned.flux.value
        lc_times = lc_binned.time.value

        #med_value = np.nanmedian(lc_fluxes)
        
        #lc_normflux = lc_fluxes/med_value

        self.time = lc_times
        self.norm_flux = lc_fluxes


        if window is not None:
            new_times = []
            new_fluxes = []            

            if window[0] < self.time[0] or window[0] > self.time[-1]:
                self.success = False
                raise ValueError(f"Window {window[0]}, {window[1]} is outside the range of lightcurve times {self.time[0]} - {self.time[-1]}")
            
            else:
                for i in range(len(self.time)):
                    if self.time[i] > window[0] and self.time[i] < window[1]:
                        new_times.append(self.time[i])
                        new_fluxes.append(self.norm_flux[i])
                
                
                self.time = np.array(new_times)
                self.norm_flux = np.array(new_fluxes)

    
    def make_sound_arr(self, max_val=900, min_val=200):
        """Sound array

        Make sound array as .wav file, higher pitch corresponds to higher flux. Saves to subdirectory "song."

        Args:
            max_val (int or float): maximum Hz frequency
            min_val (int or float): minimum Hz frequency
        
        Returns:
            Nothing.
        """

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

        song_path = os.getcwd() + "/song/"
        self.song_path = song_path
        if not os.path.isdir(song_path):
            directory = Path(song_path)
            directory.mkdir(parents=True, exist_ok=True)

        write(song_path + f"TIC{self.tic}_S{self.sector}_SONG.wav", samplerate, audio_arr)

        # colors
        # cmap = plt.cm.magma

        # sorted_args = np.argsort(self.norm_flux)

        # values = np.linspace(0, 1, len(self.norm_flux))
        # colors = np.empty((len(self.norm_flux), 4))  # 4 for RGBA
        # colors[sorted_args] = cmap(values)

        # self.colors= colors 

        #sd.play(audio_arr, samplerate)
        #sd.wait()


    def make_video(self):
        """Video file

        Makes animated plot of lightcurve, lighter color corresponds to higher flux. Saves as .mp4 in subdirectory "dance".
        
        Args:
            None.

        Returns:
            Nothing.
        """
        # Original time
        x_raw = self.time
        y_raw = self.norm_flux

        # Removing nans
        y = y_raw[~np.isnan(y_raw)]
        x = x_raw[~np.isnan(y_raw)]

        
        fig, ax = plt.subplots(1, dpi=500, figsize=(7, 4))
        line, = ax.plot([], [], marker='o', linestyle='', color='b') 
        ax.set_xlabel('Time (days)')
        ax.set_ylabel('Normalized Flux')
        ax.set_xlim(self.time[0], self.time[-1])
        ax.set_ylim(np.nanmin(self.norm_flux)-0.005, np.nanmax(self.norm_flux)+0.005)
        ax.set_title(f"TIC {self.tic} - Sector {self.sector}")

        
        def update(i):
            
            # line.set_data(x[:frame], y[:frame])
            # line.set_color(self.colors[frame])

            plt.scatter(x[:i], y[:i], color="#9564b8", edgecolor="k", linewidth=0.5)

           # return line,

        
        ani = animation.FuncAnimation(
            fig, update, frames=len(x), interval=50, repeat=True
        )

        dance_path = os.getcwd() + "/dance/"
        self.dance_path = dance_path
        if not os.path.isdir(dance_path):
            directory = Path(dance_path)
            directory.mkdir(parents=True, exist_ok=True)

        ani.save(dance_path + f"TIC{self.tic}_S{self.sector}_DANCE.mp4", writer='ffmpeg', fps=30)
        #plt.show()

    def combine(self):
        """Combines video and audio

        Makes the final video product with the audio (corresponding to flux) and the animated lightcurve. 
        Saves as .mp4 in subdirectory "song_and_dance".

        Args:
            None.
        
        Returns:
            Nothing.
        """

        video_clip = VideoFileClip(self.dance_path + f"TIC{self.tic}_S{self.sector}_DANCE.mp4", audio=False)
        audio_clip = AudioFileClip(self.song_path + f"TIC{self.tic}_S{self.sector}_SONG.wav")

        video_factor = video_clip.duration / audio_clip.duration

        
        video_clip = video_clip.with_effects([MultiplySpeed(video_factor)])

        
        final_clip = video_clip.with_audio(audio_clip)

        song_and_dance_path = os.getcwd() + "/song_and_dance/"
        self.song_and_dance_path = song_and_dance_path 

        if not os.path.isdir(song_and_dance_path):
            directory = Path(song_and_dance_path)
            directory.mkdir(parents=True, exist_ok=True)

        final_clip.write_videofile(
            song_and_dance_path + f"TIC{self.tic}_S{self.sector}_FINAL.mp4", 
            codec="libx264", 
            audio_codec="aac", 
            temp_audiofile="temp-audio.m4a",  
            remove_temp=True,                 
        )

       
        video_clip.close()
        audio_clip.close()
        final_clip.close()



tic = 124029677 
sector = 33
window = [2217, 2220]
planet = Transit(tic, sector, window=window)
planet.make_sound_arr()
planet.make_video()
planet.combine()


# tic = 55652896
# sector = 63 #originally did 38
# window = [2340, 2341]

# tic = 149601126
# sector = 32 #96
# window = [2196, 2198.5]

# tic = 263930790
# sector = 73
# window = [3293, 3299]




#55652896, 38, 63


