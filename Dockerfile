FROM ubuntu:16.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential software-properties-common \
    libboost-dev libboost-serialization-dev libssl-dev \
    cmake vim \
    wget \
    make libbz2-dev libexpat1-dev swig python-dev

# Add PPA and install GDAL libraries
RUN add-apt-repository -y ppa:ubuntugis/ppa && apt-get -q update
RUN apt-get -y install gdal-bin libgdal-dev

# Set up fmm directory and copy code (excluding the Python script at this stage)
RUN mkdir -p /fmm
COPY ./fmm /fmm

# Set work directory and build project
WORKDIR /fmm
RUN rm -rf build
RUN mkdir -p build && \
    cd build && \
    cmake .. && \
    make install

# Copy the Python script after building to ensure it’s in the correct directory
COPY 03_map_matching.py /fmm/
#COPY ext_task3.py /fmm/
#COPY ext_task3-python2.py /fmm/

# Expose port and set default command
EXPOSE 8080
CMD ["python", "03_map_matching.py"]
#CMD ["python", "ext_task3-python2.py"]
#CMD ["python", "ext_task3.py"]
