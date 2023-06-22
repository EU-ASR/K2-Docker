import pyaudio
import numpy as np
import time
import asyncio
import logging
import math
import time
from typing import AsyncIterable, Iterable

import grpc
import audio_to_text_pb2
import audio_to_text_pb2_grpc


#p = pyaudio.PyAudio()

CHANNELS = 1
RATE = 44100
FRAMES_PER_BUFFER = 441
REC_LENGTH = 20



#def callback(in_data, frame_count, time_info, flag):
#    # using Numpy to convert to array for processing
#    audio_data = np.fromstring(in_data, dtype=np.float32)
#    energy=np.sqrt(np.sum(np.power(audio_data,2)))
#    #print(np.sum(np.abs(audio_data)))
#    print(energy)
#    return None, pyaudio.paContinue # put the in_data instead of None to playback the input (loop)



# Performs a bidi-streaming call
#async def send_microphone_buffers(stub: audio_to_text_pb2_grpc.RouteGuideStub) -> None:
#    # gRPC AsyncIO bidi-streaming RPC API accepts both synchronous iterables
#    # and async iterables.
#    call = stub.RouteChat(get_audio_buffer())
#    async for response in call:
#        print(f"Received message {response.message} at {response.location}")



#async def main() -> None:
#    async with grpc.aio.insecure_channel('localhost:50051') as channel:
#        stub = audio_to_text_pb2_grpc.Module_ASRCoreStub(channel)
#        await send_microphone_buffers(stub)

def generate_audio_buffer():
    s1 = audio_to_text_pb2.Sample()
    s1.sample = 0.1
    s2 = audio_to_text_pb2.Sample()
    s2.sample = 0.2
    s3 = audio_to_text_pb2.Sample()
    s3.sample = 0.3

    audio_buffer = audio_to_text_pb2.AudioBuffer()
    audio_buffer.samples.extend([s1, s2, s3])
    return audio_buffer

def generate_audio_stream():
    audio_stream=[
        generate_audio_buffer(),
        generate_audio_buffer(),
        generate_audio_buffer(),
        generate_audio_buffer(),
        generate_audio_buffer()
    ]
    
    for buffer in audio_stream:        
        yield buffer
    
def main() -> None:

    logging.basicConfig(level=logging.INFO)

    #asyncio.get_event_loop().run_until_complete(main())

#    stream = p.open(format=pyaudio.paFloat32,
#                    channels=CHANNELS,
#                    rate=RATE,
#                    output=False, #we are not playing back
#                    input=True,
#                    frames_per_buffer=FRAMES_PER_BUFFER,
#                    stream_callback=None) #callback


    with grpc.insecure_channel('localhost:50051') as channel:
        stub = audio_to_text_pb2_grpc.Module_ASRCoreStub(channel)

        #for i in range(0, int(RATE / FRAMES_PER_BUFFER * REC_LENGTH)):
#            audio_data = np.fromstring(stream.read(FRAMES_PER_BUFFER), dtype=np.float32)
            
        response = stub.TranscribeBuffer(generate_audio_stream())
        for i in response:
            print(i)

            #async for recognized_tokens in stub.TranscribeBuffer(audio_buffer):
            #    print(recognized_tokens)
            #for token in recognized_tokens.tokens :
            #    print(f"Received token {token.token} with likelihood {token.likelihood}")



    # if I use callback
    # stream.start_stream()
    # while stream.is_active():
    #    time.sleep(20)
    #    stream.stop_stream()
    #    print("Stream is stopped")


#    stream.stop_stream()
#    stream.close()

#    p.terminate()

if __name__ == '__main__':
    main()
