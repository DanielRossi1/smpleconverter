# OS SETTINGS
# Here you can choose the OS and the CUDA version you want to mount 

FROM nvidia/cuda:11.8.0-devel-ubuntu18.04

# other examples:
# FROM nvidia/cuda:11.4.0-cudnn8-devel-ubuntu18.04
# FROM nvidia/cuda:11.7.1-base-ubuntu22.04
# FROM nvidia/cuda:11.3.1-base-ubuntu20.04 # supports python 3.8 - 3.9
# FROM nvidia/cuda:11.8.0-base-ubuntu18.04 # supports python 3.6 - 3.7
# FROM nvidia/cuda:11.1.1-devel-ubuntu20.04 # supports python 3.8 - 3.9
# FROM nvidia/cuda:11.8.0-devel-ubuntu18.04 # supports python 3.6 - 3.7

# you can find more versions here:
# https://hub.docker.com/r/nvidia/cuda/
# https://hub.docker.com/r/nvidia/cuda/tags?page=1&name=base-ubuntu


# -----------------------------------------------------------------------------------------------------------------------------------------------------
# ENVIRONMENT SETTINGS
# In this section we want to specify which softwares we want to pre-install within the docker

# to be sure we set non interactive bash also here
ENV DEBIAN_FRONTEND=noninteractive

# configuration for x11 forwarding
LABEL com.nvidia.volues.needed="nvidia-docker"
ENV PATH /usr/local/nvidia/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH}
RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install -y -q \
    x11-apps mesa-utils && rm -rf /var/lib/apt/lists/*

# remove all the packages within Debian base configuration (not wasting time installing things that will not be used)
RUN rm -f /etc/apt/sources.list.d/*.list

# install Ubuntu Software needed for the development (DEBIAN_FRONTEND="noninteractive" needed to avoid human interaction in the process)
RUN apt-get update && DEBIAN_FRONTEND="noninteractive" && apt-get install -y -q \
    sudo \
    git \
    curl \
    wget \
    vim \
    bash \
    bash-completion \
    build-essential \
    libgl1-mesa-dev  \
    libglu1-mesa-dev \
    freeglut3-dev \
    libosmesa6-dev \
    libboost-dev \
    ffmpeg \
    unzip \
    python3.7 \
    python3.7-dev \
    python3-pip \
    python3-tk \
    python3-venv \
&& rm -rf /var/lib/apt/lists/*

# set python update alternatives - the highest is the preferred one
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
RUN update-alternatives --config python3

# remove python2
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# -----------------------------------------------------------------------------------------------------------------------------------------------------
# USER SETTINGS

# the docker's user will be 'user' and its home will be '/user/home'
ARG UID=1000
ARG GID=1000
ARG USER_NAME=user
ARG USER_HOME=/home/$USER_NAME

# create a new user within the Docker container
RUN groupadd -g $GID -o $USER_NAME \
    && useradd -m -u $UID -g $GID -o -s /bin/bash $USER_NAME \
    && echo "$USER_NAME:Docker!" | chpasswd \
    && mkdir -p /src && chown -R $USER_NAME:$USER_NAME /src \
    && mkdir -p /etc/sudoers.d \
    && usermod -aG video $USER_NAME \
    && echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME


# -----------------------------------------------------------------------------------------------------------------------------------------------------
# FINAL SETUPS

# upgrade python pip
RUN python -m pip install --upgrade pip

# install python packages in requirements directory
# project/
# |-- ai-base-docker/
# |   |   |-- build.sh
# |   |   |-- Dockerfile
# |   |   |-- run.sh
# |-- src/
# |   |   |-- model/
# |   |   |-- utils/
# |   |   |-- requirements/
# |   |       |-- base.txt
# |   |       |-- devel.txt

RUN mkdir -p ./tmp
COPY ./src/requirements/* ./tmp/

RUN for file in ./tmp/*; do \
        python3 -m pip install -r $file; \
    done

RUN python -m pip download --only-binary :all: --dest . --no-cache https://download.pytorch.org/whl/cu100/torch-1.1.0-cp37-cp37m-linux_x86_64.whl


WORKDIR ${USER_HOME}/src
RUN mkdir -p dependencies

# INSTALL CUDA SAMPLES
WORKDIR ${USER_HOME}/src/dependencies
RUN wget https://github.com/NVIDIA/cuda-samples/archive/refs/tags/v11.8.zip
RUN unzip v11.8.zip
WORKDIR ${USER_HOME}/src/dependencies/cuda-samples-11.8
RUN make 

WORKDIR ${USER_HOME}
ENV CUDA_SAMPLES_INC=${USER_HOME}/src/dependencies/cuda-samples-11.8/Common/

# INSTALL TORCH TRUST NCG
WORKDIR ${USER_HOME}/src/dependencies
RUN git clone https://github.com/vchoutas/torch-trust-ncg.git
WORKDIR ${USER_HOME}/src/dependencies/torch-trust-ncg
RUN python setup.py install 

# INSTALL PSBODY FOR MESH
WORKDIR ${USER_HOME}/src/dependencies
RUN git clone --recursive https://github.com/DanielRossi1/mesh.git
RUN mv mesh psbody
WORKDIR ${USER_HOME}/src/dependencies/psbody
RUN BOOST_INCLUDE_DIRS=$(whereis boost)/include make all

RUN pip install loguru
RUN pip install open3d
RUN pip install omegaconf

# remove all the created/copied/moved file by the docker
RUN rm -rf *

USER $USER_NAME
WORKDIR $USER_HOME

# when the container is launched it will start a bash session
CMD ["/bin/bash"]
