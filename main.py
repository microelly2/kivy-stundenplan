# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- plugin loader
#--
#-- microelly 2015
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import kivy
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import *
from kivy.base import EventLoop

import datetime,re,os

from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '800')

from kivy.support import *
install_android()

class stundenplan(FloatLayout):
	pass

class stundenplanApp(App):

	changed=Property(False)
	pos=Property(-1)
	text=Property(None)
	neutext=Property(None)
	tagrelativ=-99
	filename=None

	def build(self):
		return stundenplan()

	def focus(self,button,pos):
		rc=False
		if self.pos<>-1:
			if self.text <>self.neutext:
				l=len(sap.root.tag.children)
				cpos=l-2*self.pos
				sap.root.tag.children[cpos].text= self.neutext 
				rc=True
		self.pos=pos
		if button:
			self.text=button.text
			self.neutext=button.text
		return rc

	def validate(self,button,pos):
			if self.text <> button.text:
				self.neutext = button.text
				self.changed=True

	def TagOffset(self,n):
		wd=datetime.datetime.today().weekday()
		if  wd+n >4:
			n =n+2
		if  wd+n < 0:
			n=n-2
		return n 

	def leseTagDatei(self,nr):
		nr0=nr
		self.schreibeTagDatei()
		for c in self.root.tagebuts.children:
			c.background_color=(0,0,1,1)
		self.root.tagebuts.children[5].background_color=(1,0,1,1)
		self.root.tagebuts.children[5-nr].background_color=(2,0,0,1)
		nr=self.TagOffset(nr)
		self.tagrelativ=nr

		nr=self.tagrelativ
		tagwort = (datetime.datetime.now() + datetime.timedelta(hours=24*nr)).strftime("%Y-%m-%d")
		fn=tagwort+'.txt'
		self.filename=fn
		self.title = str(tagwort)
		vw=''
		if nr0 == 0:
			vw='Heute '
		elif nr0 == 1:
			vw='Morgen '
		EventLoop.window.title = 'Stundenplanung  '  + vw + (datetime.datetime.now() + datetime.timedelta(hours=24*nr)).strftime(" %d.%m.%Y  (%A)")
		try:
			with open(fn) as f:
				content = f.readlines()
			pos=0
			inhalt=''
			lanz=len(self.root.tag.children)
			for cp in range(12):
				sap.root.tag.children[cp].text=''
			for l in content:
				res = re.search(r"^([^\t].*):\s+\|\n", l)
				if res:
					pos += 1
					cpos=lanz-2*pos
					try:
						sap.root.tag.children[cpos+2].text=inhalt
					except:
						pass
					inhalt=''
					sap.root.tag.children[cpos+1].text=res.group(1)
				else:
					res = re.search(r"^[\t]+(.*)\n", l)
					if res:
						if inhalt:
							inhalt +='\n'
						inhalt += res.group(1)  
					else:
						print "FEHLER"
			pos += 1
			cpos=lanz-2*pos
			sap.root.tag.children[cpos+2].text=inhalt
			self.changed=False
		except:
			print "Datei nicht lesebar"
			print "lese Template" + str(nr0) + str(nr)
			wd=datetime.datetime.today().weekday() + nr
			if wd >=7: wd -= 7
			print "lese " + str(wd)
			fn=str(wd)+'_template.txt'
			with open(fn) as f:
				cc = f.readlines()
			for k in [5,4,3,2,1,0]:
				sap.root.tag.children[2*k].text=''
				if cc[5-k] <>'\n':
					sap.root.tag.children[2*k+1].text=str(6-k) + ". Stunde: " + cc[5-k].rstrip('\n')
				else:
					sap.root.tag.children[2*k+1].text='*'

	def schreibeTagDatei(self):
		if self.tagrelativ == -99 or not self.changed:
			return
		nr=self.tagrelativ
		tagwort = (datetime.datetime.now() + datetime.timedelta(hours=24*nr)).strftime("%Y-%m-%d")
		fn=tagwort+'.txt'
		fn=self.filename
		try:
			os.rename(fn, "tmp/X_"  + fn + '==' +  str(datetime.datetime.now()) + ".txt")
		except:
			print "kann kein Backup machen"
		target = open(fn, 'w')
		lanz=len(self.root.tag.children)
		i=lanz-1
		while 0<i:
			target.write(sap.root.tag.children[i].text)
			target.write(": |\n")
			cmt=sap.root.tag.children[i-1].text.split('\n')
			for ct in cmt:
				target.write("\t" + ct + "\n")
			i -= 2
		self.pos= -1
		self.changed=False

	def on_start(self):
		self.leseTagDatei(0)
		n= - 1
		ll=len(self.root.tagebuts.children)
		tagtab=['Mo','Di','Mi','Do','Fr']
		while n<6: 
			nof=self.TagOffset(n) 
			b=self.root.tagebuts.children[ll-n-2]
			tagwort = (datetime.datetime.now() + datetime.timedelta(hours=24*nof)).strftime("%d.%m.")
			if nof > 4: nof2=nof-7+1
			else: nof2=nof+1
			nof2 += datetime.datetime.today().weekday() -1
			if nof2 > 4: nof2 -= 7 
			b.text= str(nof) + " " + tagtab[nof2] +" " + str(tagwort)
			b.text= tagtab[nof2] +" " + str(tagwort)
			n += 1

	def on_stop(self):
		print "on_stop"
		self.schreibeTagDatei()

if __name__ == '__main__' and True:
	sap=stundenplanApp()
	sap.run()
