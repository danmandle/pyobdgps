#! /usr/bin/python

import os
from gps import *
from time import *
import time
import threading
import sqlite3 as sqlite
import sys
import math

con = sqlite.connect('data.db')

gpsd = None #gotta set the global variable

os.system('clear') #clear the terminal

class GpsPoller(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		global gpsd #bring it in scope
		gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
		self.current_value = None
		self.running = True #setting the thread running to true

	def run(self):
		global gpsd
		while gpsp.running:
			gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

if __name__ == '__main__':
	gpsp = GpsPoller() # create the thread
	try:
		gpsp.start() # start it up
		while True:
			#It may take a second or two to get good data
			#print gpsd.fix.latitude,', ',gpsd.fix.longitude,'	Time: ',gpsd.utc
			
			os.system('clear')
			
			if((math.fabs(gpsd.fix.latitude) > 0) and (math.fabs(gpsd.fix.longitude) > 0)):
				fromDB = {}
				fromGPS = {"lat": gpsd.fix.latitude, "lon": gpsd.fix.longitude, "time": gpsd.utc, "elev": gpsd.fix.altitude, "speed": gpsd.fix.speed, "track": gpsd.fix.track}
				
				with con:
					con.row_factory = sqlite.Row
					cur = con.cursor()
					#cur.execute("CREATE TABLE gpsdata(time NUMERIC PRIMARY KEY, lat REAL, lon REAL, speed REAL, elev REAL, track REAL)")
					
					cur.execute("select * from gpsdata where oid = (select max(oid) from gpsdata)")
					fromDB = cur.fetchone()
					
					if((math.fabs(math.fabs(fromDB['lat'])-math.fabs(fromGPS['lat'])) > 0) and (math.fabs(math.fabs(fromDB['lon'])-math.fabs(fromGPS['lon'])) > 0)):
						print "Delta distance is > 0"
					else:
						print "Distance is too damn short"
					
					cur.execute("INSERT INTO gpsdata(lat,lon,time,speed,elev,track) VALUES (?,?,?,?,?,?);",(fromGPS['lat'],fromGPS['lon'],fromGPS['time'],fromGPS['speed'],fromGPS['elev'],fromGPS['track']))
					
					con.commit()
					print "Number of rows updated: %d" % cur.rowcount
			
				print
				print ' GPS reading'
				print '----------------------------------------'
				print 'time utc    ' , fromGPS['time']
				print 'latitude    ' , fromGPS['lat'] ,		'Diff: ', (fromGPS['lat']-fromDB['lat'])
				print 'longitude   ' , fromGPS['lon'] ,		'Diff: ', (fromGPS['lon']-fromDB['lon'])
				print 'altitude (m)' , fromGPS['elev'] ,		'Diff: ', (fromGPS['elev']-fromDB['elev'])
				print 'speed (m/s) ' , fromGPS['speed'] ,		'Diff: ', (fromGPS['speed']-fromDB['speed'])
				print 'track       ' , fromGPS['track'] ,		'Diff: ', (fromGPS['track']-fromDB['track'])

			else:
				print "Trying to get real info from the GPS..."

			time.sleep(5) #set to whatever

	except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
		print "\nKilling Thread..."
		#gpsd = gps(mode=WATCH_DISABLE)
		gpsp.running = False
		gpsp.join() # wait for the thread to finish what it's doing
	print "Done.\nExiting."