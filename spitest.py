#!/usr/bin/python
import busio
import board
import time 
import digitalio

spi = busio.SPI(board.SCK, MISO=board.MISO, MOSI=board.MOSI)

while not spi.try_lock():
    pass

#ok, so it is locked
spi.configure(baudrate=5000000, phase=0, polarity=0)

try:
    for i in range(0,4):
        res = bytearray(2)
        spi.write([0x00,0xff])
        spi.readinto(res)
        print(res)
finally:
    spi.unlock()

