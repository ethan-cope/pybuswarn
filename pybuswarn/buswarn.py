#!/usr/bin/python3

from bs4 import BeautifulSoup 
import random 
import time as t
import RPi.GPIO as GPIO
from sevenseg import SevenSeg
import subprocess as sp
import os 

class Route():
	def __init__(self, routenum,  userstop="", timedata = [], mode = "normal" ):
		self.userstop = userstop 
		self.routenum = routenum
		self.timedata = timedata
		self.date = ""
		self.timeindex = 0
		self.mode = mode 
		self.sev = SevenSeg()
		self.location = "/home/pi/buswarn"
		self.logfile = open(self.location+"/log","a")

	def isdebug(self):
		return self.mode == "debug"

	def logout(self, e):
		self.logfile.write("[%s] %s\n" %(t.strftime("%I:%M %p",t.localtime()), e))

	def downloadSchedule(self, tries = 0):
		tries +=1 
		try:
			with open(self.location+"/routes.html","r") as routefile:
				page = routefile.read()

				if page == "\n":
					raise FileNotFoundError("It's empty for some reason. RELOAD!")

				self.loadTable(page)
				col = self.timedata[0].index(self.userstop)
		
				if(t.localtime().tm_mday != self.timedata[1][0].tm_mday):
					#download schedule
					self.logout("The schedule is outdated. Downloading new...\n")
					raise FileNotFoundError("The schedule is outdated. Downloading new...\n")

				current_time = t.mktime(t.localtime()) 
				return "Success!"
				"""
				#this handles if the program is started in the middle of the day for whatever reason
				if self.timeindex == 0:
					self.timeindex = 1
					#print("The thing is %s" % len(self.timedata))
					while t.mktime(self.timedata[self.timeindex][col]) < current_time and self.timeindex < len(self.timedata):
						#print("Index of %s, column of %s" % (self.timeindex, col))
						self.timeindex += 1
						if(self.timeindex == len(self.timedata)):
							self.logout("The day is over, or your schedule is outdated!\n")
							raise FileNotFoundError("The day is over, or your schedule is outdated!")
					#next_time = t.mktime(self.timedata[self.timeindex][col])
				"""

		except FileNotFoundError:
			#wget https://transport.tamu.edu/busroutes/Routes.aspx?r=15 -O /home/pi/buswarn/routes.htmpisnl

			command = "wget https://transport.tamu.edu/busroutes/Routes.aspx?r=%s -O %s/routes.html"%(self.routenum, self.location)
			#for some reason the output isn't decoding
			output = sp.check_output(command.split()).decode()
			self.logout("Downloading from Wget. assuming ok...")
			#print(output)

			if tries < 3:
				return self.downloadSchedule(tries)
			else:
				raise FileNotFoundError("Wget isn't working. check the connection")

	def loadTable(self, page):
		#page = self.downloadSchedule(refresh = True)


		soup = BeautifulSoup(page, "html.parser")
		table_rows = soup.find('table').find_all('tr')
		data = []

		#gets header

		for row in table_rows:
			td = row.find_all('td')
			for item in td:
				if(item.text == "No Service Is Scheduled For This Date"):
					os.remove("./routes.html")
					raise ValueError("No service for buses today: is it a game day?")
					#best way to handle post-gamedays

		for i in range(1,3):
			th = table_rows[i].find_all('th')
			row = [i.text for i in th]
			if row != []:
				data.append(row)

		date = str([i.time for i in table_rows[3].find_all('td')]) 
		self.date = date[date.find('\"')+1:date.find(' ',date.find('\"')+1)] #hardcoded string offset to search behind
	   
		#dumb error messages 
		errormessages = ["Uh oh!", "Stinky!", "Poopies!", "Haha!"]

		for tr in table_rows:
			td = tr.find_all('td')
			 
			#print(td)
			#row = [i.text for i in td]
			try:
				row = [t.strptime(self.date+" "+i.text+"M","%m/%d/%Y %I:%M%p") for i in td]
			except ValueError:
				if self.mode == "dumb":
					print(errormessages[int(random.randrange(0,4))])
				else:
					print("Some unimportant error")

			if row != []:
				data.append(row)

		#print(data)
		self.timedata = data


		#relocation of technicality generateor
		row = []
		curr = t.localtime(t.mktime(t.localtime()) - 60*2)

		for i in self.timedata[0]:
			row.append(curr)
		self.timedata.insert(1,row)


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

		#there needs to be an extremely early time for the timer to latch on to
		self.timeindex = 0
		col = self.timedata[0].index(self.userstop)
		next_time = -1
		prev_time = -1
		current_time = t.mktime(t.localtime()) 
		while(True):
			#secs in day = 86400
			current_time = t.mktime(t.localtime()) 

			#This should be handled on the 
			if(t.localtime().tm_mday != self.timedata[1][0].tm_mday):
				#download schedule
				raise ValueError("The schedule is outdated. did the downloadschedule method work?")

			current_time = t.mktime(t.localtime()) 

			#this handles if the program is started in the middle of the day for whatever reason
			if self.timeindex == 0:
				self.timeindex = 1
				#print("The thing is %s" % len(self.timedata))
				while t.mktime(self.timedata[self.timeindex][col]) < current_time and self.timeindex < len(self.timedata):
					#print("Index of %s, column of %s" % (self.timeindex, col))
					self.timeindex += 1
					if(self.timeindex == len(self.timedata)):
						raise ValueError("The day is over, or your schedule is outdated!")
				next_time = t.mktime(self.timedata[self.timeindex][col])
	
			#elif self.timeindex+1 == len(self.timedata):
				#raise ValueError("End of bus routes today. Bye!")

			if(self.timeindex+1 == len(self.timedata)):
				raise ValueError("The day is over.")

			#if the bus leaves
			if current_time > next_time:
				self.timeindex+=1
				next_time = t.mktime(self.timedata[self.timeindex][col])
				print("Bus left! next bus leaves at [%s]"%t.strftime("%I:%M %p",self.timedata[self.timeindex][col]))
				self.logout("Bus Left")
				self.sev.display([0,0])
				t.sleep(.5)
				self.sev.display([-1,-1])
				t.sleep(.5)
				self.sev.display([0,0])
				t.sleep(.5)
				self.sev.display([-1,-1])

			#handles the minute changing
			#this may have a bug when you start super early
			if (next_time - prev_time)//60 != (next_time - current_time)//60:
				#essentially, if the seconds aren't the same as the last time through the loop
				diff = (next_time - current_time)/60+1
				print("%i" % diff)
				self.logout("%i" % diff)
				self.sev.display([diff//10,diff%10])
				#+1 is the nice way of rounding so the minutes roughly match up.
				#also gives lazy people an extra incentive to go earlier I guess

			#print((next_time - current_time)/60)
			#print("[%s]"%t.strftime("%I:%M %p",self.timedata[self.timeindex][col]))
			prev_time = current_time
			t.sleep(5)
		
	"""
	def downloadSchedule(self,routenum = 15, refresh = False):
		#if schedule isn't already downloaded, downloads it. 
		tries = 0
		while(tries < 30):
			try:
				tries +=1
				if refresh:
					refresh = False
					raise FileNotFoundError("Haha download now fool")
				with open(self.location+"/routes.html", 'r') as routefile:
					page = routefile.read()
					#print(page)
					break

			except FileNotFoundError:
				#wget https://transport.tamu.edu/busroutes/Routes.aspx?r=15 -O /home/pi/buswarn/routes.htmpisnl

				command = "wget https://transport.tamu.edu/busroutes/Routes.aspx?r=%s -O %s/routes.html"%(routenum, self.location)
				output = sp.check_output(command.split())
				self.logout(str(output))
				print(output)

				if tries > 10:
					print("couldn't wget after 10 tries.")
					exit(1)
		return page
	"""


r = Route(15,"Aggie Station", mode = "debug")
try:
	#r.loadTable()
	success = r.downloadSchedule()
	r.logout(str(success))
	print(success)
	print(r)
	r.logfile.write(str(r) + "\n")
	r.findNextStop()
except ValueError as e:
	r.logfile.write("[%s] %s\n" %(t.strftime("%I:%M %p",t.localtime()), e))
	print(e)
finally:
	GPIO.cleanup()
#print(r)

