FROM arm64v8/python

#Programmer, FTDI and gpio prerequisites
RUN apt-get update && \
    apt-get install gcc build-essential cmake rpm libftdi-dev \
    libusb-1.0.0 libusb-1.0.0-dev libgtk-3-dev pandoc \
    swig unzip wget python3-dev python3-setuptools kmod sudo -y

#Install stlink 
RUN git clone https://github.com/stlink-org/stlink.git && cd stlink && \
    make clean && make release && make install && ldconfig 

#Install stm32flash
RUN git clone https://git.code.sf.net/p/stm32flash/code stm32flash-code && \
    cd stm32flash-code && make install

#Fix RPI 5 issues pertaining to gpiozero and lgpio
#https://pimylifeup.com/raspberry-pi-install-lgpio/
RUN cd ~ && wget https://github.com/joan2937/lg/archive/master.zip && \
    unzip master.zip && cd lg-master && make && make install && \
    cd ../ && rm master.zip && rm -r -f ./lg-master

#Create a non-root user to run the application
RUN useradd app && usermod -aG dialout,plugdev,sudo app && \
    echo '%sudo ALL=(ALL) NOPASSWD: /usr/sbin/modprobe ftdi_sio' >> /etc/sudoers && \
    echo '%sudo ALL=(ALL) NOPASSWD: /usr/sbin/modprobe -r ftdi_sio' >> /etc/sudoers

USER app
WORKDIR /home/app

#Copy in the source code
COPY . .

ENV PATH="/home/app/.local/bin:$PATH"
RUN pip install .

CMD ["python", "-m", "blower_tester"]
