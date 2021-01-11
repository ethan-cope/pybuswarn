from bs4 import BeautifulSoup 
import random 
import time as t

#TODO: we can have this run until like 12 am? then restart 5 min after the website is downloaded?

class Route():
    def __init__(self, userstop="", timedata = [], dumbmode = False ):
        self.userstop = userstop 
        self.timedata = timedata
        self.date = ""
        self.timeindex = 0
        self.dumbmode = dumbmode 

    #def stampify(self, tstamp):


    def loadTable(self):
        try:
            #TODO: add multiple file types here
            with open("routes.html", 'r') as routefile:
                page = routefile.read()
                #print(page)
                outfile = open("times.dat","w")
        except FileNotFoundError:
            print("file not found: did you rename it correctly with wget?")
            exit(1)

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
                if self.dumbmode:
                    print(errormessages[int(random.randrange(0,4))])
                else:
                    print("Some unimportant error")
            
            if row != []:
                data.append(row)
                for timeint in row:
                    timestr += "%i " % timeint
                timestr +="\n"



        self.timedata = data
        print(timestr)
        outfile.write("%i %i\n" % (len(data)-1, len(data[0])))
        #-1 for the header
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
           

r = Route("Aggie Station", dumbmode = True)
try:
    r.loadTable()
except ValueError as e:
    print(e)
#print(r)

