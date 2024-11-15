FROM fmm:0.1.0

#RUN apt-get update && apt-get install -y python-pip python3-pip

COPY ./requirements.txt /
RUN wget https://raw.githubusercontent.com/pypa/get-pip/refs/heads/main/public/2.7/get-pip.py -O get-pip.py
RUN python get-pip.py

RUN python -m pip install pandas shapely
