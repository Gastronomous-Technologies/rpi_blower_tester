FROM arm64v8/python

#STM32 Programmer prerequisites
#As per compiling.md (github.com/stlink-org/stlink/blob/testing/doc/compiling.md)
RUN apt-get update && \
    apt-get install gcc build-essential cmake rpm \
    libusb-1.0.0 libusb-1.0.0-dev libgtk-3-dev pandoc -y

#Install stlink 
RUN git clone https://github.com/stlink-org/stlink.git && cd stlink && \
    make clean && make release && make install && ldconfig 

#Create a non-root user to run the application
RUN useradd app && adduser app dialout

USER app
WORKDIR /home/app

#Copy in the source code
COPY . .

ENV PATH="/home/app/.local/bin:$PATH"
RUN pip install .

CMD ["python", "-m", "blower_tester"]
