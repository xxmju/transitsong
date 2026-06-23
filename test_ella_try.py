import sounddevice as sd
import numpy as np

# 1. Configure the properties of the sound
sample_rate = 44100  # Hertz (samples per second)
duration = 2.0       # Seconds
frequency = 440.0    # Pitch frequency (A4 note in Hz)

# 2. Calculate time steps and mathematical sine wave data
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio_signal = 0.5 * np.sin(2 * np.pi * frequency * t)  # 0.5 reduces volume amplitude

# 3. Play the generated NumPy array
sd.play(audio_signal, sample_rate)
sd.wait()

