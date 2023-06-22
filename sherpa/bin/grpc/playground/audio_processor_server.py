import asyncio
import logging
import math
import time
from typing import AsyncIterable, Iterable
from concurrent import futures
from threading import Thread

import grpc
import playground.audio_to_text_pb2
import playground.audio_to_text_pb2_grpc


def generate_sentence():
    tokens_array=[
        playground.audio_to_text_pb2.Token(token="a", likelihood=0.01),
        playground.audio_to_text_pb2.Token(token="b", likelihood=0.02),
        playground.audio_to_text_pb2.Token(token="c", likelihood=0.03),
        playground.audio_to_text_pb2.Token(token="d", likelihood=0.04),
    ]

    recognized_sentence = playground.audio_to_text_pb2.RecognizedTokens()
    recognized_sentence.tokens.extend(tokens_array)
    return recognized_sentence

class Module_ASRCoreServicer(playground.audio_to_text_pb2_grpc.Module_ASRCoreServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self) -> None:
        self.cnt = 0
        pass

    def TranscribeBuffer(self, request_iterator, context):
        
        print(request_iterator)

        for i in request_iterator:
            print(i)

        sentences_stream=[
            generate_sentence(),
            generate_sentence(),
            generate_sentence(),
            generate_sentence()
        ]
        
        for sentence in sentences_stream:        
            yield sentence
                              

def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))    
    audio_to_text_pb2_grpc.add_Module_ASRCoreServicer_to_server(
        Module_ASRCoreServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()



