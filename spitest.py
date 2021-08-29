import busio
import board
import time 
import digitalio

spi = busio.SPI(board.SCK, MISO=board.MISO, MOSI=board.MOSI)

while not spi.try_lock():
    pass

spi.configure(baudrate=9600, phase=0, polarity=0)

try:
    for i in range(0,4):
        res = bytearray(2)
        print(spi.write_readinto(res,[0x00,0xff]))
        print(res)
finally:
    spi.unlock()
