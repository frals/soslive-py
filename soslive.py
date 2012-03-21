#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import re
from HTMLParser import HTMLParser

class SimpleParser(HTMLParser):
	def __init__(self):
		self.reset()
		self.dump = []
		self.perma = ""
		self.permafound = False
		self.halt = False
	def handle_starttag(self, tag, attrs):
		#if "div" in tag:
		if "br" in tag:
			self.dump.append("<p/>")
		if "a" in tag:
			#if "perma" in attrs[0]:
			if "href" in attrs[0]:
				self.permafound = True
	def handle_endtag(self, tag):
		self.permafound = False
		pass
	def handle_data(self, data):
		if self.permafound:
			self.perma = data
			self.halt = True
		elif "Dela:" in data:
			self.halt = True			
		if not self.halt:
			self.dump.append(data.strip())
	def get_data(self):
		return ' '.join(self.dump), self.perma

class SOSLive:
	def __init__(self):
		self.url = "http://div.dn.se/dn/sos/soslive.php?id=p://www.dn.se/nyheter/soslive" 
		self.opener = urllib2.build_opener()
		self.opener.addheaders = [('User-agent', 'not Mozilla/5.0 actually a bot from frals.se'),
					('Referer', 'http://www.dn.se/nyheter/soslive')]

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
				lat, lng, freetext, url, ikon = None, None, None, None, None
				for sub in subln.split(";"):
					if "var html" in sub:
						i = subln.find("var html = ")
						n = subln.find("\";var label", i)
						i += 12 # go past "var html = "
						(freetext, url) = self.cleanHTML(subln[i:n])
					elif "var lat" in sub:
						lat = sub.replace("\"",'').replace("var lat = ",'').strip()
						#print lat
					elif "var lng" in sub:
						lng = sub.replace("\"",'').replace("var lng = ",'').strip()
						#print lng
					elif ".png\"" in sub:
						ikon = sub.replace("\"",'').replace(" = ",'').strip()

				if lat != None and lng != None:
					self.createEvent(lat, lng, freetext, url, ikon)
		
	def cleanHTML(self, dirty):
		p = SimpleParser()
		p.feed(dirty)
		freetext, url = p.get_data()
		return (freetext, url)
			
	def takeParts(self, freetext):
		tid = re.search("(Tid:(.*?)<p/>)", freetext)
		if tid:
			tid = tid.group().replace("<p/>", "").replace("Tid: ", "")
		else:
			tid = "Okänd tid"
		handelse = re.search("(Händelse:(.*?)<p/>)", freetext)
		if handelse:
			handelse = handelse.group().replace("<p/>", "").replace("Händelse: ", "")
		else:
			handelse = "Okänd händelse"
		plats = re.search("(Plats:(.*?<p/>))", freetext)
		if plats:
			plats = plats.group().replace("<p/>", "").replace("Plats: ", "")
		else:
			plats = "Okänd plats"
		larmcentral = re.search("(SOS-larmcentral:(.*?<p/>))", freetext)
		if larmcentral:
			larmcentral = larmcentral.group().replace("<p/>", "").replace("SOS-larmcentral: ", "")
		else:
			larmcentral = "Okänd larmcentral"
		prio = re.search("(Uttryckningsprioritet:(.*))", freetext)
		if prio:
			prio = prio.group().replace("<", "").replace("Uttryckningsprioritet: ", "")
		else:
			prio = "Okänd prio"
		return tid, handelse, plats, larmcentral, prio
		
		
	def createEvent(self, lat, lng, freetext, url, icon):
		#print lat, lng, freetext, url
		icon = unicode(icon, "utf-8")
		freetext = freetext.replace("<p/> <p/>", "")
		fr = freetext.decode("iso-8859-1")
		time, event, loc, central, prio = self.takeParts(fr.encode('utf-8'))
		print "<event icon=\"%s\" lat=\"%s\" lng=\"%s\" url=\"%s\">" % (icon, lat, lng, url)
		print "<time>%s</time><ev>%s</ev><loc>%s</loc>" % (time.strip(), event.strip(), loc.strip())
		print "<central>%s</central><prio>%s</prio>" % (central.strip(), prio.strip())
#		print "<freetext>%s</freetext>" % (
		print "</event>"
		pass
		

if __name__ == '__main__':
	s = SOSLive()
	print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
	print "<live>"
	s.parseHTML()
	print "</live>"
