FROM arm64v8/python

#STM32 Programmer prerequisites
#https://freeelectron.ro/installing-st-link-v2-to-flash-stm32-targets-on-linux/
RUN apt-get update && \
    apt-get install git make cmake libusb-1.0.0-dev gcc \
    usbutils build-essential -y

#Create a non-root user to run the application
RUN useradd app
USER app
WORKDIR /home/app

#Install stlink 
RUN mkdir stm32 && cd stm32 && \
    git clone https://github.com/stlink-org/stlink && \
    cd stlink && cmake . && make 

USER root
WORKDIR /home/app/stm32/stlink

RUN cd bin && cp st-* /usr/local/bin && \ 
    cd ../lib && cp *.so* /lib

USER app
WORKDIR /home/app

#Copy in the source code
COPY . .

ENV PATH="/home/app/.local/bin:$PATH"
RUN pip install .

CMD ["python", "-m", "blower_tester"]
