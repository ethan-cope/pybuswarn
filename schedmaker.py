from bs4 import BeautifulSoup
import random
import subprocess
import time as t

#TODO: we can have this run until like 12 am? then restart 5 min after the website is downloaded?

class Route():
    def __init__(self, flocation = "/home/ethan/Projects/buswarn", userstop="", routenum=0, timedata = []):
        self.flocation = flocation
        self.userstop = userstop 
        self.routenum = routenum
        self.timedata = timedata
        self.date = ""
        self.timeindex = 0

    #def stampify(self, tstamp):

    def downloadSchedule(self, tries = 0):
        tries +=1 
        try:
            with open(self.flocation+"/routes.html","r") as routefile:
                page = routefile.read()

                if page == "\n":
                    raise FileNotFoundError("It's empty for some reason. RELOAD!")

                self.loadTable(page)

                if(t.localtime().tm_mday != t.localtime(self.timedata[1][0]).tm_mday):
                    #download schedule
                    #self.logout("The schedule is outdated. Downloading new...\n"
                    raise FileNotFoundError("The schedule is outdated. Downloading new...\n")

                return "Success!"

        except FileNotFoundError as e:
            #command: wget https://transport.tamu.edu/busroutes/Routes.aspx?r=15 -O /home/pi/buswarn/routes.htmpisnl
            print(e)

            command = "wget https://transport.tamu.edu/busroutes/Routes.aspx?r=%s -O %s/routes.html"%(self.routenum, self.flocation)

            output = subprocess.run(command.split())
            print(command)
            print(output)
            if tries < 3:
                return self.downloadSchedule(tries)
            else:
                raise FileNotFoundError("Wget isn't working. check the connection")

    def loadTable(self, page):

        outfile = open("times.dat", "w")
        soup = BeautifulSoup(page, "html.parser")
        table_rows = soup.find('table').find_all('tr')
        timestr = ""
        data = []

        #gets header
        #it's a loop because it wants to be 
        #from 2 to 3? always seem to get an empty array the first time around. but also, it's probably better to catch those errors now

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
        self.date = date[date.find('\"')+1:date.find(' ',date.find('\"')+1)] #hardcoded string offset to search behind
       
        #dumb error messages 
        errormessages = ["Uh oh!", "Stinky!", "Poopies!", "Haha!"]

        for tr in table_rows:
            td = tr.find_all('td')
             
            #stamp-ize method here?
            #print(td)
            #row = [i.text for i in td]
            try:
                row = [t.mktime(t.strptime(self.date+" "+i.text+"M","%m/%d/%Y %I:%M%p")) for i in td]
            except ValueError:
                print("Some unimportant error")
            
            if row != []:
                data.append(row)
                for timeint in row:
                    timestr += "%i " % timeint
                timestr +="\n"



        self.timedata = data
        print(timestr)
        #-1 for the header
        outfile.write("%s %s\n" % (len(data)-1, len(data[0])))
        outfile.write(timestr)

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
           

r = Route(userstop = "Aggie Station", routenum = 15)
try:
    r.downloadSchedule()
except ValueError as e:
    print(e)
#print(r)

