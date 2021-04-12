import RPi.GPIO as GPIO
import time

"""
GPIO.setmode(GPIO.BCM)

GPIO.setup(16, GPIO.OUT)

for i in range(0, 4):
	GPIO.output(16,12, GPIO.LOW)
	print("on")
	time.sleep(1)
	GPIO.output(16,12, GPIO.HIGH)
	print("off")
	time.sleep(1)
"""

class SevenSeg():

	def __init__(self):
		GPIO.setmode(GPIO.BCM)

		#format array
		# ABCDEF
		# 000000
		self.decode  = {0 : "1111110",
						1 : "0110000",
						2 : "1101101",
						3 : "1111001",
						4 : "0110011",
						5 : "1011011",
						6 : "1011111",
						7 : "1110000",
						8 : "1111111",
						9 : "1111011",
						-1: "0000000",
						}

		self.pinnums = [[24,
						 25,
						 6,
						 5,
						 22,
						 23,
						 18],
		
						[20,
						 21,
						 26,
						 19,
						 13,
						 16,
						 12]]

#sets up each gpio pin for output
		for i in range(0,len(self.pinnums)):
#this should always be 7 
			for j in range(0,7):
				pinno = self.pinnums[i][j] 
				GPIO.setup(pinno, GPIO.OUT)


	def display(self,digits = [0,0]):
		try:
			for i in range(0,len(digits)):
				code = self.decode[int(digits[i])]
#should always be 7 as well
				for j in range(0,7):
					pinno = self.pinnums[i][j] 
					#print(self.pinnums[i][j])

					if(code[j] == "1"):
						GPIO.output(pinno, GPIO.LOW)
					elif(code[j] == "0"):
						GPIO.output(pinno, GPIO.HIGH)
					else:
						raise ValueError("Incorrect decode value!")

		except ValueError as e:
			print(e)
			#print("you need to send over ints!")


"""
sev = SevenSeg()
sev.display([6,9])
time.sleep(6)
GPIO.cleanup()
"""
"""
try:
	for i in range(99, 0, -1):
		sev.display([i//10, i%10])
		time.sleep(.25)
finally:
	GPIO.cleanup()
"""
