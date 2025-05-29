FROM arm64v8/python
WORKDIR /usr/local/app

#STM32 Programmer prerequisites
#https://freeelectron.ro/installing-st-link-v2-to-flash-stm32-targets-on-linux/
RUN apt-get update && \
    apt-get install git make cmake libusb-1.0.0-dev gcc \
    usbutils build-essential -y
   
RUN mkdir stm32 && cd stm32 && \
    git clone https://github.com/stlink-org/stlink && \
    cd stlink && \
    cmake . && make && cd bin && cp st-* /usr/local/bin && \ 
    cd ../lib cp *.so* /lib && cd /usr/local/app

# Copy in the source code
COPY ./src src 

ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --upgrade pip && pip install src/.

CMD ["sleep", "1000"]
#CMD ["python", "-m", "blower_tester"]
