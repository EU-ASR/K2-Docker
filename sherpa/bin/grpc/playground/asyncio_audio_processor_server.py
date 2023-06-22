import asyncio
import logging
import time
import random
from typing import AsyncIterable, Iterable
from concurrent import futures
from threading import Thread
import numpy as np

import grpc
import audio_to_text_pb2
import audio_to_text_pb2_grpc


def generate_sentence():
    """
    Debug rutine simulating one sentence. The output of this rutine is one gRPC message. To be deleted later.
    """
    tokens_array=[
        audio_to_text_pb2.Token(token="a", likelihood=0.01),
        audio_to_text_pb2.Token(token="b", likelihood=0.02),
        audio_to_text_pb2.Token(token="c", likelihood=0.03),
        audio_to_text_pb2.Token(token="d", likelihood=0.04),
    ]

    recognized_sentence = audio_to_text_pb2.RecognizedTokens()
    recognized_sentence.tokens.extend(tokens_array)
    return recognized_sentence

def generate_recognized_sentences():
    """
    Debug rutine simulating sentence generator. This generator is used to fill the gRPC stream. To be deleted later.
    """
    sentences_stream=[
        generate_sentence(),
        generate_sentence(),
        generate_sentence(),
        generate_sentence()
    ]
    
    for sentence in sentences_stream:        
        yield sentence


def create_recognized_sentence(**kwargs): #energy, min, max
    """
    Create a sentence from the function arguments. We expect arguments to be floats!.
    """     
    recognized_sentence = audio_to_text_pb2.RecognizedTokens()
    for arg in kwargs:
        recognized_sentence.tokens.append(audio_to_text_pb2.Token(token=arg, likelihood=float(kwargs[arg])))

    return recognized_sentence

def buffer_to_np (buffer: audio_to_text_pb2.AudioBuffer) -> np.ndarray:    
    """
    Helper to convert buffer recieved by gRPC into numpy array.
    """     

    np_buffer = np.empty((len(buffer.samples)))
    for index, sample in enumerate(buffer.samples):
        np_buffer[index] = sample.sample
    return np_buffer

def process_buffer(buffer: audio_to_text_pb2.AudioBuffer):
    """
    Simulator of lowlevel ASR. Takes buffer and produces some statistics
    """     

    np_array = buffer_to_np(buffer)
    energy = np.sqrt(np.sum(np.power(np_array,2)))
    min = np.min(np_array)
    max = np.max(np_array)
    return energy, min, max



async def ASR (buffer_queue: asyncio.Queue, sentence_queue: asyncio.Queue):    
    """
    High level ASR. It takes audio buffers from the input queue and writes recognized sentences into output queue.
    """     
    
    while True:
        try:
            # read the queue and do not wait for some data if it is empty.
            buffer = buffer_queue.get_nowait()

            # if there was a audio buffer, process it
            energy, min, max = process_buffer(buffer)
            
            # check for stop the ASR
            if buffer is None:
                break

            # simulation of some asynchronicity. We transcribe just random buffers.
            if (random.random() > 0.9):
                # write the recognized sentence to the output queue
                await sentence_queue.put(create_recognized_sentence(energy=energy, min=min, max=max))

        # Empty queue .. just wait a bit a try again
        except asyncio.QueueEmpty:
            print('ASR: input buffer_queue is empty...')            
            await asyncio.sleep(0.1)
                        

    # all done
    print('ASR: Done')
    
    # Indicate that we transcribed all the input buffers. There is no more sentences to be produced.
    await sentence_queue.put(None)        


class Module_ASRCoreServicer(audio_to_text_pb2_grpc.Module_ASRCoreServicer):
    """
    Provides methods that implement functionality of the ASRCore module.
    This module ingests stream of audio buffers and produces stream of sentences
    """

    def __init__(self, input_queue: asyncio.Queue, output_queue: asyncio.Queue) -> None:
        # we need input/output queues for the ASR
        self.input_queue = input_queue
        self.output_queue = output_queue
        
    async def TranscribeBuffer(self, request_iterator: AsyncIterable[audio_to_text_pb2.AudioBuffer], 
        context) -> AsyncIterable[audio_to_text_pb2.RecognizedTokens]:
        """
        The core ... handling the streams
        """

        # read input buffers
        async for buffer in request_iterator:

            # put them into the input queue (from where the ASR takes them)
            await self.input_queue.put(buffer)
            print(f"{time.time()} buffer recieved.")

            # check the output queue and send all sentences
            while True:
                
                try:
                    sentence = self.output_queue.get_nowait()

                # no more sentences to send
                except asyncio.QueueEmpty:
                    break

                # ignor the stopping indication. It is not valid message.
                # send the sentences to the client
                if sentence is not None:
                    yield sentence

        # No more input buffers from the client. Indicate it to the ASR
        await self.input_queue.put(None)    

        # Flush the sentence output queue and send them to client
        while True:            
            sentence = await self.output_queue.get()
            if sentence is None:
                break
            yield sentence
              

async def serve() -> None:
    # create the queues
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()

    # create and spawn the ASR as extra task
    asyncio.create_task(ASR(input_queue, output_queue))
    
    # create gRPC server
    server = grpc.aio.server()    
    audio_to_text_pb2_grpc.add_Module_ASRCoreServicer_to_server(
        Module_ASRCoreServicer(input_queue, output_queue), server)
    server.add_insecure_port('[::]:50051')    
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.get_event_loop().run_until_complete(serve()) # TODO deprecation warning here
