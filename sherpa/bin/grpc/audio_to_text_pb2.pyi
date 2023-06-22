from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AudioBuffer(_message.Message):
    __slots__ = ["samples"]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedCompositeFieldContainer[Sample]
    def __init__(self, samples: _Optional[_Iterable[_Union[Sample, _Mapping]]] = ...) -> None: ...

class RecognizedTokens(_message.Message):
    __slots__ = ["tokens"]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    tokens: _containers.RepeatedCompositeFieldContainer[Token]
    def __init__(self, tokens: _Optional[_Iterable[_Union[Token, _Mapping]]] = ...) -> None: ...

class Sample(_message.Message):
    __slots__ = ["sample"]
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    sample: float
    def __init__(self, sample: _Optional[float] = ...) -> None: ...

class Token(_message.Message):
    __slots__ = ["likelihood", "token"]
    LIKELIHOOD_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    likelihood: float
    token: str
    def __init__(self, token: _Optional[str] = ..., likelihood: _Optional[float] = ...) -> None: ...
