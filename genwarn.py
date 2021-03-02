#!/usr/bin/python3

from bs4 import BeautifulSoup 
import random 
import time as t
import RPi.GPIO as GPIO
from sevenseg import SevenSeg
import subprocess as sp

class Route():
	def __init__(self, userstop="", timedata = [], mode = "pyfollow", routenum = 15):
		self.routenum = routenum
		self.userstop = userstop 
		self.timedata = timedata
		self.date = ""
		self.timeindex = 0
#modes: schedgen, pyfollow
		self.mode = mode 
		self.sev = SevenSeg()
		self.location = "/home/pi/buswarn/pybuswarn"
		self.logfile = open(self.location+"/log","a")

	#deprecated
	def isdebug(self):
		return self.mode == "debug"

	def downloadSchedule(self, tries = 0):
		tries +=1 
		try:
			with open(self.location+"/routes.html","r") as routefile:
				page = routefile.read()
				self.loadTable(page)

				if(t.localtime().tm_mday != self.timedata[1][0].tm_mday):
					raise FileNotFoundError("The schedule is outdated. did the cron job work correctly?")

				current_time = t.mktime(t.localtime()) 

				#this handles if the program is started in the middle of the day for whatever reason
				"""
				if self.timeindex == 0:
					col = self.timedata[0].index(self.userstop)
					self.timeindex = 1
					while t.mktime(self.timedata[self.timeindex][col]) < current_time and self.timeindex < len(self.timedata):
						self.timeindex += 1
						if(self.timeindex == len(self.timedata)):
							raise FileNotFoundError("The day is over, or your schedule is outdated!")
					next_time = t.mktime(self.timedata[self.timeindex][col])
		
				#elif self.timeindex+1 == len(self.timedata):
					#raise ValueError("End of bus routes today. Bye!")			
				"""

		except FileNotFoundError:
			#cut and paste command:
			#wget https://transport.tamu.edu/busroutes/Routes.aspx?r=15 -O /home/pi/buswarn/routes.htmpisnl

			command = "wget https://transport.tamu.edu/busroutes/Routes.aspx?r=%s -O %s/routes.html"%(self.routenum, self.location)
			output = sp.check_output(command.split())
			self.logfile.write(str(output))
			print(output)

			if tries < 3:
				return self.downloadSchedule(tries)
			else:
				raise FileNotFoundError("Wget isn't working. check the connection")

	def loadTable(self, page):

		outfile = open("times.dat","w")
			
		#Note - this throws an error at some point. I don't know what causes it
		soup = BeautifulSoup(page, "html.parser")
		try:
			table_rows = soup.find('table').find_all('tr')
		except AttributeError:
			raise FileNotFoundError("The schedule is corrupted in some way, no table found")

		timestr = ""
		data = []

		#header
		for row in table_rows:
			td = row.find_all('td')
			for item in td:
				if(item.text == "No Service Is Scheduled For This Date"):
					raise ValueError("No service for buses today: is it a game day?")

		for i in range(1,3):
			th = table_rows[i].find_all('th')
			row = [i.text for i in th]
			if row != []:
				data.append(row)
		date = str([i.time for i in table_rows[3].find_all('td')]) 
		self.date = date[date.find('\"')+1:date.find(' ',date.find('\"')+1)] 
	   
		for tr in table_rows:
			td = tr.find_all('td')
			#print(td)
			#row = [i.text for i in td]

			try:
				row = [t.strptime(self.date+" "+i.text+"M","%m/%d/%Y %I:%M%p") for i in td]
			except ValueError:
				print("Some unimportant error")

			if row != []:
				for timeint in row:
					timestr += "%i " % t.mktime(timeint)
				timestr +="\n"
				data.append(row)

		self.timedata = data
		if self.mode == "schedgen":
			print(timestr)
			#-1 for the header
			outfile.write("%s %s\n" % (len(data)-1, len(data[0])))
			outfile.write(timestr)
			outfile.close()

	def __str__(self):
		retstring = ""
		for line in self.timedata:
			for tim in line:
				if type(tim) == type(""):
					retstring += tim + " "
				else:
					retstring += "[%s]"%t.strftime("%I:%M %p", tim)
			retstring += "\n"
		return retstring
			
	def findNextStop(self):
		print(self)
		col = self.timedata[0].index(self.userstop)
		next_time = -1
		prev_time = -1
		current_time = t.mktime(t.localtime()) 
		while(True):

			current_time = t.mktime(t.localtime()) 

			if current_time > next_time:
				self.timeindex+=1
				next_time = t.mktime(self.timedata[self.timeindex][col])
				print("Bus left! next bus leaves at [%s]"%t.strftime("%I:%M %p",self.timedata[self.timeindex][col]))
				self.logfile.write("[%s] %s\n" %(t.strftime("%d.%m.%y% I:%M %p",t.localtime()),"Bus Left"))
				self.sev.display([0,0])
				t.sleep(.5)
				self.sev.display([-1,-1])
				t.sleep(.5)
				self.sev.display([0,0])
				t.sleep(.5)
				self.sev.display([-1,-1])

			#TODO - delete the routes file if it's the end of the day!

			if (next_time - prev_time)//60 != (next_time - current_time)//60:
				diff = ((next_time - current_time)/60+1)%100
				print("%i" % diff)
				if diff > -1:
					self.sev.display([diff//10,diff%10]) 

			#print((next_time - current_time)/60)
			#print("[%s]"%t.strftime("%I:%M %p",self.timedata[self.timeindex][col]))
			prev_time = current_time
			t.sleep(1)

r = Route("Aggie Station", mode = "pyfollow")
try:
	r.downloadSchedule()
	if r.mode == "pyfollow":
		r.findNextStop()
except ValueError as e:
	r.logfile.write("[%s] %s\n" %(t.strftime("%I:%M %p",t.localtime()), e))
	print(e)
finally:
	GPIO.cleanup()
#print(r)

