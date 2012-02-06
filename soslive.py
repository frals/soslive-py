#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
from HTMLParser import HTMLParser

class SimpleParser(HTMLParser):
	def __init__(self):
		self.reset()
		self.dump = []
		self.perma = ""
		self.permafound = False
		self.halt = False
	def handle_starttag(self, tag, attrs):
		if "div" in tag:
			if "perma" in attrs[0]:
				self.permafound = True
	def handle_endtag(self, tag):
		self.permafound = False
		pass
	def handle_data(self, data):
		if self.permafound:
			self.perma = data
		elif "Dela:" in data:
			self.halt = True			
		if not self.halt:
			self.dump.append(data.strip())
	def get_data(self):
		return ' '.join(self.dump), self.perma

class SOSLive:
	def __init__(self):
		self.url = "http://div.dn.se/dn/sos/soslive.php?sid="
		self.opener = urllib2.build_opener()
		self.opener.addheaders = [('User-agent', 'not Mozilla/5.0 actually a bot from frals.se')]

	def parseHTML(self):
		fh = self.opener.open(self.url)
		#print fh.info()
		#data = fh.readlines()
		data = fh.read()
		### super ugly hack to find boundaries of interesting data
		i = data.index("// Read the data from example.xml")
		i += 33
		n = data.index("// ========= If a parameter was passed, open the info window ==========")
		self.parseLine(data[i:n].strip())
		
	def parseLine(self, ln):
		# skip over lines that doesnt include a POI
		if "var ikon" in ln:
			for subln in ln.split("var ikon"):
				lat, lng, freetext, url = None, None, None, None
				for sub in subln.split(";"):
					if "var html" in sub:
						i = subln.find("var html = ")
						n = subln.find("\";var label", i)
						i += 12 # go past "var html = "
						freetext, url = self.cleanHTML(subln[i:n])
					elif "var lat" in sub:
						lat = sub.replace("\"",'').replace("var lat = ",'').strip()
						#print lat
					elif "var lng" in sub:
						lng = sub.replace("\"",'').replace("var lng = ",'').strip()
						#print lng

				if lat != None and lng != None:
					self.createEvent(lat, lng, freetext, url)
					print "-"
		
	def cleanHTML(self, dirty):
		p = SimpleParser()
		p.feed(dirty)
		freetext, url = p.get_data()
		return freetext, url
			
		
	def createEvent(self, lat, lng, freetext, url):
		print lat, lng, freetext, url
		pass
		

if __name__ == '__main__':
	s = SOSLive()
	s.parseHTML()