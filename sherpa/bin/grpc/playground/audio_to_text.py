import pyaudio
import numpy as np
import time

p = pyaudio.PyAudio()

CHANNELS = 1
RATE = 44100
FRAMES_PER_BUFFER = 441

def callback(in_data, frame_count, time_info, flag):
    # using Numpy to convert to array for processing
    audio_data = np.fromstring(in_data, dtype=np.float32)
    energy=np.sqrt(np.sum(np.power(audio_data,2)))
    #print(np.sum(np.abs(audio_data)))
    print(energy)
    return None, pyaudio.paContinue # put the in_data instead of None to playback the input (loop)

stream = p.open(format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=RATE,
                output=False, #we are not playing back
                input=True,
                frames_per_buffer=FRAMES_PER_BUFFER,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(20)
    stream.stop_stream()
    print("Stream is stopped")

stream.close()

p.terminate()
