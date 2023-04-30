# Dockerfile

# Build container
FROM condaforge/mambaforge:4.9.2-5 as conda

# Install build dependencies
RUN export DEBIAN_FRONTEND="noninteractive" TZ="Europe/Prague" \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      cmake make gcc g++ libc6-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY conda-linux-64.lock /locks/conda-linux-64.lock
RUN mamba create -p /opt/env --copy --file /locks/conda-linux-64.lock \
    && conda clean -afy

WORKDIR /workspace

# TODO: What is icefall for?
# # TODO: Refactor this to not clone the repository
# RUN git clone --depth 1 https://github.com/k2-fsa/icefall.git
# ENV PYTHONPATH "${PYTHONPATH}:/workspace/icefall"
# # https://github.com/k2-fsa/icefall/issues/674
# ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION "python"

COPY . ./sherpa
WORKDIR /workspace/sherpa
RUN export CC=gcc && export CXX=g++ \
    && conda run -p /opt/env python setup.py bdist_wheel \
    && conda run -p /opt/env python -m pip install --no-deps ./dist/k2_sherpa-*.whl --force

# Clean up
RUN find /opt/env -name '*.a' -delete && \
    rm -rf /opt/env/conda-meta && \
    rm -rf /opt/env/include && \
    find /opt/env -name '__pycache__' -type d -exec rm -rf '{}' '+' && \
    rm -rf /env/lib/python3.8/site-packages/pip /env/lib/python3.8/idlelib /env/lib/python3.8/ensurepip \
      /opt/env/bin/x86_64-conda-linux-gnu-ld \
      /opt/env/bin/x86_64-conda_cos6-linux-gnu-ld \
      /opt/env/share/terminfo && \
    find /opt/env/lib/python3.8/distutils/ -name 'tests' -type d -exec rm -rf '{}' '+' && \
    find /opt/env/lib/python3.8/site-packages/numpy -name 'tests' -type d -exec rm -rf '{}' '+' && \
    find /opt/env/lib/python3.8/site-packages -name '*.pyx' -delete && \
    rm -rf /opt/env/lib/python3.8/site-packages/uvloop/loop.c

# Primary container
# Distroless version
# FROM gcr.io/distroless/base-debian10
# Debug version
FROM debian:stable-slim

# Install build dependencies
RUN export DEBIAN_FRONTEND="noninteractive" TZ="Europe/Prague" \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
      git git-lfs  \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/sherpa
COPY LICENSE /app
COPY ./sherpa/bin/web/ /app/sherpa/web/
COPY --from=conda /opt/env /opt/env
COPY --from=conda /workspace/sherpa/build/sherpa/bin /app/sherpa/bin

# Adding sherpa binaries to PATH
ENV PATH=$PATH:/opt/env/bin:/app/sherpa/bin
# ENV PYTHONPATH "${PYTHONPATH}:/workspace/icefall"
# https://github.com/k2-fsa/icefall/issues/674
# ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION "python"

# Put debug tools in bash_history for quick access
RUN echo \
  "apt-get update && apt-get install -y net-tools netcat iputils-ping vifm vim" \
  >> ~/.bash_history

# Defualt for http or websocket server. TODO: There might be more ports!
EXPOSE 6006

CMD ["sherpa-version"]
