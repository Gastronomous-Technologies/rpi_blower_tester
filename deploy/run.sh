#!/bin/bash 

#See section 1.2.1
#https://www.st.com/resource/en/user_manual/um2237-stm32cubeprogrammer-software-description-stmicroelectronics.pdf
docker run -it -v /dev:/dev --device /dev:/dev --net=host -it blower_app
