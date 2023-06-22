import numpy as np
import time
import asyncio
import logging
import time
from typing import AsyncIterable, Iterable
import grpc
import sounddevice

import audio_to_text_pb2
import audio_to_text_pb2_grpc


# soundcard setting we want the data read in
CHANNELS = 1
RATE = 16000
FRAMES_PER_BUFFER = 160 # size of the buffer from the sound card


def generate_audio_buffer():
    """
    Debug rutine simulating one buffer. The output of this rutine is one gRPC message. To be deleted later.
    """
    s1 = audio_to_text_pb2.Sample()
    s1.sample = 0.1
    s2 = audio_to_text_pb2.Sample()
    s2.sample = 0.2
    s3 = audio_to_text_pb2.Sample()
    s3.sample = 0.3

    audio_buffer = audio_to_text_pb2.AudioBuffer()
    audio_buffer.samples.extend([s1, s2, s3])

    return audio_buffer

async def generate_audio_stream():
    """
    Debug rutine simulating buffer generator. This generator is used to fill the gRPC stream. To be deleted later.
    """

    audio_stream=[
        generate_audio_buffer(),
        generate_audio_buffer(),
        generate_audio_buffer(),
        generate_audio_buffer(),
        generate_audio_buffer()
    ]
    
    for buffer in audio_stream:
        await asyncio.sleep(1) # simulating some delay between buffers     
        yield buffer


def np_to_audio_buffer(buffer: np.ndarray):
    """
    conversion of numpy array (comming from soundcard) to the AudioBuffer structure we are sending as one message.
    """
    audio_buffer = audio_to_text_pb2.AudioBuffer()        
    for np_sample in np.nditer(buffer):        
        sample = audio_to_text_pb2.Sample()
        sample.sample = float(np_sample)
        audio_buffer.samples.append(sample)    

    return audio_buffer

# partly taken from https://python-sounddevice.readthedocs.io/en/0.4.6/examples.html#creating-an-asyncio-generator-for-audio-blocks
async def input_audio_stream_generator():
    """Audio stream generator that yields buffer and sends them as gRPC messages"""

    # we will use async queue to buffer the audio buffers. We can easilly handle them from soundcard callback to the gRPC sender this way
    input_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    # callback for the soundcard audio input. 
    def callback(data, frames, time_info, status):

        # we run in threadsafe because async queues are not thread safe!
        loop.call_soon_threadsafe(input_queue.put_nowait, np_to_audio_buffer(data)) # work with real audio buffer
        #loop.call_soon_threadsafe(input_queue.put_nowait, generate_audio_buffer()) # for debug.. work with toy data
        
    # initialize audio input stream
    audio_stream = sounddevice.InputStream(callback=callback, channels=CHANNELS, blocksize=FRAMES_PER_BUFFER, samplerate=RATE, dtype=np.dtype(np.float32))

    # open the audio stream = activate microphone recording
    with audio_stream:
        while True:
            indata = await input_queue.get()            
            yield indata # send a buffer as message
            #yield generate_audio_buffer() # for debug, send the toy data


async def main() -> None:

    logging.basicConfig(level=logging.DEBUG)

    # connect to the server
    async with grpc.aio.insecure_channel('localhost:6006') as channel:

        # get the communication class
        stub = audio_to_text_pb2_grpc.Module_ASRCoreStub(channel)

        # send the generated stream of audio buffers while recieve recognized sentences from the server
        async for recognized_tokens in stub.TranscribeBuffer(input_audio_stream_generator()):
            # just print the recognized sentence
            print(f" {time.time()} -> {recognized_tokens}")

if __name__ == '__main__':
    asyncio.run(main())
