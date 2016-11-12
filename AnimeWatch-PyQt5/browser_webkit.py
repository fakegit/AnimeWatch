"""
Copyright (C) 2016 kanishka-linux kanishka.linux@gmail.com

This file is part of AnimeWatch.

AnimeWatch is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

AnimeWatch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with AnimeWatch.  If not, see <http://www.gnu.org/licenses/>.



"""


from PyQt5 import QtCore, QtGui,QtNetwork,QtWidgets
import sys
import urllib
import urllib3
import pycurl
from io import StringIO,BytesIO
import re
import subprocess
import os.path
from subprocess import check_output
from bs4 import BeautifulSoup
from functools import partial
from PyQt5 import QtWebKitWidgets
from PyQt5.QtWebKitWidgets import QWebView,QWebPage
	
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtCore import QUrl

from adb_webkit import NetWorkManager

import time
from yt import get_yt_url,get_yt_sub
from PyQt5.QtCore import (QCoreApplication, QObject, Q_CLASSINFO, pyqtSlot,pyqtSignal,
                          pyqtProperty)

def getContentUnicode(content):
	if isinstance(content,bytes):
		print("I'm byte")
		try:
			content = str((content).decode('utf-8'))
		except:
			content = str(content)
	else:
		print(type(content))
		content = str(content)
		print("I'm unicode")
	return content

def ccurl(url):
	global hdr
	hdr = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0'
	print(url)
	c = pycurl.Curl()
	curl_opt = ''
	picn_op = ''
	rfr = ''
	nUrl = url
	cookie_file = ''
	postfield = ''
	if '#' in url:
		curl_opt = nUrl.split('#')[1]
		url = nUrl.split('#')[0]
		if curl_opt == '-o':
			picn_op = nUrl.split('#')[2]
		elif curl_opt == '-Ie' or curl_opt == '-e':
			rfr = nUrl.split('#')[2]
		elif curl_opt == '-Icb' or curl_opt == '-bc':
			cookie_file = nUrl.split('#')[2]
		if curl_opt == '-d':
			post = nUrl.split('#')[2]
			post = re.sub('"','',post)
			post = re.sub("'","",post)
			post1 = post.split('=')[0]
			post2 = post.split('=')[1]
			post_data = {post1:post2}
			postfield = urllib.parse.urlencode(post_data)
	url = str(url)
	#c.setopt(c.URL, url)
	try:
		c.setopt(c.URL, url)
	except UnicodeEncodeError:
		c.setopt(c.URL, url.encode('utf-8'))
	storage = BytesIO()
	if curl_opt == '-o':
		c.setopt(c.FOLLOWLOCATION, True)
		c.setopt(c.USERAGENT, hdr)
		f = open(picn_op,'wb')
		c.setopt(c.WRITEDATA, f)
		c.perform()
		c.close()
		f.close()
	else:
		if curl_opt == '-I':
			c.setopt(c.FOLLOWLOCATION, True)
			c.setopt(c.USERAGENT, hdr)
			c.setopt(c.NOBODY, 1)
			c.setopt(c.HEADERFUNCTION, storage.write)
		elif curl_opt == '-Ie':
			c.setopt(c.FOLLOWLOCATION, True)
			c.setopt(c.USERAGENT, hdr)
			c.setopt(pycurl.REFERER, rfr)
			c.setopt(c.NOBODY, 1)
			c.setopt(c.HEADERFUNCTION, storage.write)
		elif curl_opt == '-e':
			c.setopt(c.FOLLOWLOCATION, True)
			c.setopt(c.USERAGENT, hdr)
			c.setopt(pycurl.REFERER, rfr)
			c.setopt(c.NOBODY, 1)
			c.setopt(c.HEADERFUNCTION, storage.write)
		elif curl_opt == '-IA':
			c.setopt(c.FOLLOWLOCATION, True)
			c.setopt(c.NOBODY, 1)
			c.setopt(c.HEADERFUNCTION, storage.write)
		elif curl_opt == '-Icb':
			c.setopt(c.FOLLOWLOCATION, True)
			c.setopt(c.USERAGENT, hdr)
			c.setopt(c.NOBODY, 1)
			c.setopt(c.HEADERFUNCTION, storage.write)
			if os.path.exists(cookie_file):
				os.remove(cookie_file)
			c.setopt(c.COOKIEJAR,cookie_file)
			c.setopt(c.COOKIEFILE,cookie_file)
		elif curl_opt == '-bc':
			c.setopt(c.FOLLOWLOCATION, True)
			c.setopt(c.USERAGENT, hdr)
			c.setopt(c.WRITEDATA, storage)
			c.setopt(c.COOKIEJAR,cookie_file)
			c.setopt(c.COOKIEFILE,cookie_file)
		elif curl_opt == '-L':
			c.setopt(c.USERAGENT, hdr)
			c.setopt(c.WRITEDATA, storage)
		elif curl_opt == '-d':
			c.setopt(c.USERAGENT, hdr)
			c.setopt(c.WRITEDATA, storage)
			c.setopt(c.POSTFIELDS,postfield)
		else:
			c.setopt(c.FOLLOWLOCATION, True)
			c.setopt(c.USERAGENT, hdr)
			c.setopt(c.WRITEDATA, storage)
		c.perform()
		c.close()
		content = storage.getvalue()
		content = getContentUnicode(content)
		return content


class downloadThread(QtCore.QThread):
    
	def __init__(self,url,ui,file_path):
		QtCore.QThread.__init__(self)
	
		self.url = url
		self.interval = 1
		self.ui = ui
		self.file_path = file_path
	def __del__(self):
		self.wait()                        
	
	def run(self):
		content = ccurl(self.url)
		soup = BeautifulSoup(content,'lxml')
		title = soup.title.text.strip().replace('/','-')
		self.ui.gotHtmlSignal.emit(title,self.url,self.file_path)

class BrowserPage(QWebPage):  
	def __init__(self):
		super(BrowserPage, self).__init__()
		
	def acceptNavigationRequest(self,frame,req,nav_type):
		print(req.url().toString(),nav_type,self.currentFrame().url().toString(),'--print--nav--type--')
		
		if nav_type == 0:
			print('clicked inside nav-type--',req.url().toString())
			#self.parent.urlSignal.emit(url.url())
		
		return super(BrowserPage, self).acceptNavigationRequest(frame,req,nav_type)
		
	def userAgentForUrl(self, url):
		#return self.hdr
		if 'youtube' in url.toString():
			return 'Mozilla/5.0 (Linux; Android 4.4.4; SM-G928X Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36'
		else:
			return 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0'

class Browser(QtWebKitWidgets.QWebView):
	gotHtmlSignal = pyqtSignal(str,str,str)
	def __init__(self,ui,home,screen_width,quality,site,epnArrList):
		super(Browser, self).__init__()
		self.setPage(BrowserPage())
		#self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		self.hdr = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0'
		self.img_url = ''
		self.ui = ui
		self.quality = quality
		self.site = site
		self.home = home
		self.epnArrList = epnArrList
		self.wait_player = False
		self.urlChanged.connect(self.url_changed)
		self.hoveredLink = ''
		self.media_url = ''
		self.epn_name_in_list = ''
		#self.loadFinished.connect(self._load_finished)
		#self.loadStarted.connect(self._load_started)
		self.titleChanged.connect(self.title_changed)
		self.loadProgress.connect(self.load_progress)
		self.current_link = ''
		self.title_page = ''
		#ui.tab_2.showMaximized()
		self.ui.tab_2.setMaximumWidth(screen_width)
		self.url_arr = []
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.player_wait)
		self.timer.setSingleShot(True)
		#self.linkClicked.connect(self.link_clicked)
		self.hit_link =''
		self.playlist_dict = {}
		self.get_playlist = False
		self.playlist_name = ''
		self.gotHtmlSignal.connect(self.got_curl_html)
		self.yt_sub_folder = os.path.join(home,'External-Subtitle')
		if not os.path.exists(self.yt_sub_folder):
			os.makedirs(self.yt_sub_folder)
			
	def link_clicked(self,link):
		print('--link--clicked--')
		self.current_link = link.toString()
		print('--link--clicked--',self.current_link)
		m = []
		if '/watch?' in link.toString():
			a = link.toString().split('?')[-1]
			b = a.split('&')
			if b:
				for i in b:
					j = i.split('=')
					k = (j[0],j[1])
					m.append(k)
			else:
				j = a.split('=')
				k = (j[0],j[1])
				m.append(k)
			d = dict(m)
			print(d,'----dict--arguments---generated---')
			try:
				self.current_link = 'https://m.youtube.com/watch?v='+d['v']
			except:
				pass
		if (self.current_link.startswith("https://m.youtube.com/watch?v=") or self.current_link.startswith("https://www.youtube.com/watch?v=")) and not self.wait_player:
			#self.page().mainFrame().evaluateJavaScript("var element = document.getElementById('player');element.innerHtml='';")
			self.page().mainFrame().evaluateJavaScript("var element = document.getElementById('player');element.parentNode.removeChild(element);")
			self.wait_player = True
			#self.clicked_link(self.current_link)
			QtCore.QTimer.singleShot(1, partial(self.clicked_link,self.current_link))
			self.timer.start(1000)
	
	def player_wait(self):
		#global wait_player
		self.wait_player = False
		self.page().mainFrame().evaluateJavaScript("location.reload();")
		
	def get_html(self,var):
		print('--got--html--',self.url().toString())
		if 'youtube' in self.url().toString():
			self.playlist_dict = {}
			x = urllib.parse.unquote(var)
			
			x = x.replace('\\\\u0026','&')
			
			
			
			l = re.findall('url=https[^"]*',x)
			
			for i in l:
				if self.ui.quality_val == 'sd': 
					if 'itag=18' in i:
						final_url = re.sub('url=','',i)
						
					
			soup = BeautifulSoup(var,'lxml')
			m = soup.find('div',{'id':'player'})
			
			if m:
				print('removing')
				#self.page().mainFrame().evaluateJavaScript("var element = document.getElementById('player');element.parentNode.removeChild(element);")
				self.page().mainFrame().evaluateJavaScript("var element = document.getElementById('player');element.innerHtml='';")
			title = soup.find('title')
			if title:
				if self.current_link.startswith("https://m.youtube.com/watch?v=") or self.current_link.startswith("https://www.youtube.com/watch?v="):
					self.epn_name_in_list = title.text
					self.ui.epn_name_in_list = title.text
					#url = soup.find('meta',{'property':'og:url'})
					print(title.text,self.url().toString(),'--changed-title--')
					
			if 'list=' in self.url().toString() and 'www.youtube.com' in self.url().toString():
				
				ut = soup.findAll('li',{'class':"yt-uix-scroller-scroll-unit "})
				if not ut:
					ut = soup.findAll('li',{'class':"yt-uix-scroller-scroll-unit "})
				print(ut)
				arr = []
				for i in ut:
					try:
						j1 = i['data-video-id']+'#'+i['data-video-title']
						print(j1)
						j = i['data-video-id']
						k = i['data-video-title']
						l = (j,k)
						arr.append(l)
					except:
						pass
				d = dict(arr)
				print(d)
				print(arr)
				if d:
					self.playlist_dict = d
			elif 'list=' in self.url().toString():
				o = soup.find('div',{'id':'content-container'})
				if  o:
					m = o.findAll('img')
				else:
					m = []
				n = []
				d = {}
				for i in m:
					#print(i['src'])
					try:
						g = i.find_next('h4')
						yt_id = i['src'].split('/')[-2]
						n.append((yt_id,g.text))
					except:
						pass
				if n:
					d = dict(n)
				print(d)
				if d:
					self.playlist_dict = d
				
				
			
	def load_progress(self,var):
		#self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		#print(var,self.url().toString())
		if var == 100 and 'youtube.com' in self.url().toString():
			print(self.url().toString(),self.title(),'--load--progress--')
			frame = self.page().mainFrame().toHtml()
			self.get_html(frame)
	def title_changed(self,title):
		#self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		a = 0
		print(title,self.url().toString(),'--title--change--')
		#self.page().mainFrame().evaluateJavaScript("location.reload();")
		self.ui.epn_name_in_list = title
		
	def url_changed(self,link):
		#self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
		print('\n--url_changed--\n',link.url(),'\n--url_changed--\n')
		
		
		if not self.url_arr:
			self.url_arr.append(link.url())
			prev_url = ''
		else:
			prev_url = self.url_arr[-1]
			self.url_arr.append(link.url())
			
		if prev_url != link.url() and 'youtube' in link.url():
			self.current_link = link.url()
			m = []
			if '/watch?' in link.url():
				a = link.url().split('?')[-1]
				b = a.split('&')
				if b:
					for i in b:
						j = i.split('=')
						k = (j[0],j[1])
						m.append(k)
				else:
					j = a.split('=')
					k = (j[0],j[1])
					m.append(k)
				d = dict(m)
				print(d,'----dict--arguments---generated---')
				try:
					self.current_link = 'https://m.youtube.com/watch?v='+d['v']
				except:
					pass
			if (self.current_link.startswith("https://m.youtube.com/watch?v=") or self.current_link.startswith("https://www.youtube.com/watch?v=")) and not self.wait_player:
				#self.page().mainFrame().evaluateJavaScript("var element = document.getElementById('player');element.innerHtml='';")
				self.page().mainFrame().evaluateJavaScript("var element = document.getElementById('player');element.parentNode.removeChild(element);")
				self.wait_player = True
				#self.clicked_link(self.current_link)
				QtCore.QTimer.singleShot(1, partial(self.clicked_link,self.current_link))
				self.timer.start(1000)
				
				
		print(self.url_arr)
	
	def clicked_link(self,link):
		
		final_url = ''
		url = link
		self.epn_name_in_list = self.title()
		print(url,'clicked_link')
		if 'youtube.com/watch?v=' in url:
			if self.ui.mpvplayer_val.processId() > 0:
				self.ui.mpvplayer_val.kill()
			final_url = get_yt_url(url,self.ui.quality_val)
			if final_url:
				print(final_url,'--youtube--')
				self.ui.watchDirectly(final_url,self.epn_name_in_list,'no')
				self.ui.tab_5.show()
				self.ui.frame1.show()
				self.ui.tab_2.setMaximumWidth(400)
				
	def custom_links(self,q_url):
		url = q_url
		self.hoveredLink = url
		
	def keyPressEvent(self, event):
		
		if event.modifiers() == QtCore.Qt.AltModifier and event.key() == QtCore.Qt.Key_Left:
			self.back()
		elif event.modifiers() == QtCore.Qt.AltModifier and event.key() == QtCore.Qt.Key_Right:
			self.forward()
		super(Browser, self).keyPressEvent(event)
		
	@pyqtSlot(str,str,str)
	def got_curl_html(self,title,url,value):
		file_path = os.path.join(self.home,'Playlists',str(value))
		if '/' in title:
			title = title.replace('/','-')
		t = title + '	'+url+'	'+'NONE'
		if os.stat(file_path).st_size == 0:
			f = open(file_path,'w')
		else:
			f = open(file_path,'a')
			t = '\n'+t
		try:
			f.write(str(t))
		except:
			f.write(t)
		f.close()
		self.ui.update_playlist(file_path)
		
	def add_playlist(self,value):
		value = value.replace('/','-')
		value = value.replace('#','')
		if value.startswith('.'):
			value = value[1:]
		file_path = os.path.join(self.home,'Playlists',str(value))
		new_pl = False
		if not os.path.exists(file_path):
			f = open(file_path,'w')
			new_pl = True
		else:
			f = open(file_path,'a')
		j = 0
		for i in self.playlist_dict:
			yt_id = i
			title = self.playlist_dict[yt_id]
			title = title.replace('/','-')
			title = title.replace('#','')
			if title.startswith('.'):
				title = title[1:]
			n_url = 'https://m.youtube.com/watch?v='+yt_id
			w = title+'	'+n_url+'	'+'NONE'
			if new_pl and j==0:
				f.write(w)
			else:
				f.write('\n'+w)
			j = j+1
		f.close()
		self.get_playlist = False
		
	def triggerPlaylist(self,value,url,title):
		print ('Menu Clicked')
		print (value)
		file_path = os.path.join(self.home,'Playlists',str(value))
		if 'ytimg.com' in url:
			try:
				print(self.playlist_dict)
				yt_id = url.split('/')[-2]
				url = 'https://m.youtube.com/watch?v='+yt_id
				title = self.playlist_dict[yt_id]
			except:
				pass
		if '/' in title:
			title = title.replace('/','-')
		if '#' in title:
			title = title.replace('#','')
		if title.startswith('.'):
			title = title[1:]
		if 'list=' in url:
			title = title + '-Playlist'
		img_u = ''
		if self.img_url:
			img_u = self.img_url.toString() 
		if 'playlist?list=' in url and img_u:
			try:
				yt_id = img_u.split('/')[-2]
				o_url = r'https://m.youtube.com/playlist?list='
				n_url = 'https://m.youtube.com/watch?v='+yt_id+'&index=1&list='
				url = url.replace(o_url,n_url)
				print(url,o_url,n_url)
			except:
				pass
		print(title,url,file_path)
		t = title + '	'+url+'	'+'NONE'
		if os.stat(file_path).st_size == 0:
			f = open(file_path,'w')
		else:
			f = open(file_path,'a')
			t = '\n'+t
		try:
			f.write(str(t))
		except:
			f.write(t)
		f.close()
		self.ui.update_playlist(file_path)
		
	def contextMenuEvent(self, event):
		self.img_url = ''
		menu = self.page().createStandardContextMenu()
		hit = self.page().currentFrame().hitTestContent(event.pos())
		hit_m = self.page().mainFrame()
		hit_n = hit_m.hitTestContent(event.pos())
		url = hit.linkUrl()
		arr = ['Download As Fanart','Download As Cover']
		arr_extra_tvdb = ['Series Link','Season Episode Link']
		arr_last = ['Artist Link']
		action = []
		self.img_url = hit.imageUrl()
		self.title_page = hit.linkText()
		yt = False
		try:
			if self.title_page:
				print('self.title_page=',self.title_page)
				#self.title_page = self.title_page.strip()
				if 'youtube.com' in self.url().toString(): 
					self.title_page = hit_n.linkElement().toPlainText()
				if not self.title_page:
					self.title_page = hit.linkText()
				self.title_page = self.title_page.strip()
				tmp = self.title_page.replace('\n','#')
				print(tmp)
				tmp1 = re.search('#[^#]*',tmp)
				print(tmp1)
				self.title_page = tmp1.group()
				self.title_page = self.title_page.replace('#','')
				
			else:
				self.title_page = hit.title()
		except:
			self.title_page = hit.title()
			
			
		print('url--info\n',self.img_url.toString(),'=img_url\n',url,'=url',hit.title(),'=title\n',hit.linkText(),'=linktext\n',hit_m.title(),'--p_title--',hit_n.linkElement().toPlainText(),'--link-element')
		if (url.isEmpty() or not url.toString().startswith('http')) and self.img_url:
			url = self.img_url
		if url.isEmpty():
			url = self.url()
			print('--next--url=',self.url().toString())
			self.title_page = hit_m.title()
			if 'reload' in self.url().toString():
				print('reload # in url')
				url = self.url().toString()
				n_url = re.sub('\?reload[^\/]*\/|&mode=NORMAL|&params[^&]*','',url)
				url = QUrl(n_url)
			print('--next--url=',url.toString())
		if not url.isEmpty() or self.img_url:
			if 'tvdb' in url.toString():
				arr = arr + arr_extra_tvdb
			if 'last.fm' in url.toString():
				arr = arr + arr_last
			if 'youtube.com' in url.toString() or 'ytimg.com' in url.toString():
				yt = True
				arr[:]=[]
				arr.append('Play with AnimeWatch')
				arr.append('Download')
				arr.append('Get Subtitle (If Available)')
				if 'ytimg.com' in url.toString():
						print(self.playlist_dict)
						yt_id = url.toString().split('/')[-2]
						url = QUrl('https://m.youtube.com/watch?v='+yt_id)
						print('url=',url)
						try:
							self.title_page = self.playlist_dict[yt_id]
						except:
							self.title_page = ''
						arr.append('Add as Local Playlist')
						self.playlist_name = self.epn_name_in_list
				
				menu.addSeparator()
				submenuR = QtWidgets.QMenu(menu)
				submenuR.setTitle("Add To Playlist")
				menu.addMenu(submenuR)
				pls = os.listdir(os.path.join(self.home,'Playlists'))
				home1 = os.path.join(self.home,'Playlists')
				pls = sorted(pls,key = lambda x:os.path.getmtime(os.path.join(home1,x)),reverse=True)
				item_m = []
				for i in pls:
					item_m.append(submenuR.addAction(i))
				
				submenuR.addSeparator()
				new_pls = submenuR.addAction("Create New Playlist")
				
			for i in range(len(arr)):
				action.append(menu.addAction(arr[i]))
				
			act = menu.exec_(event.globalPos())
			for i in range(len(action)):
				if act == action[i]:
					self.download(url,arr[i])
			if yt:
				for i in range(len(item_m)):
					#print(hit.title(),self.title_page)
					if act == item_m[i]:
						if 'views' in self.title_page:
							#content = ccurl(url.toString())
							#soup = BeautifulSoup(content)
							self.title_page = re.sub('[0-9][^ ]* ','',self.title_page,1)
							self.title_page = re.sub('[0-9][^ ]* views','',self.title_page,1)
							self.title_page = self.title_page.replace('/','-')
							print('self.title_page=',self.title_page)
						if not self.title_page:
							content = ccurl(url.toString())
							soup = BeautifulSoup(content,'lxml')
							self.title_page = soup.title.text.strip().replace('/','-')
							##self.title_page = hit_m.title().strip().replace('/','-')
							##print(hit.title(),self.title_page)
							#thr = downloadThread(url.toString(),self,pls[i])
							#thr.start()
						self.triggerPlaylist(pls[i],url.toString(),self.title_page)
				
				
				if act == new_pls:
					print ("creating")
					MainWindow = QtWidgets.QWidget()
					item, ok = QtWidgets.QInputDialog.getText(MainWindow, 'Input Dialog', 'Enter Playlist Name')
					if ok and item:
						file_path = os.path.join(self.home,'Playlists',item)
						if not os.path.exists(file_path):
							f = open(file_path,'w')
							f.close()
		
		super(Browser, self).contextMenuEvent(event)
	def getContentUnicode(self,content):
		if isinstance(content,bytes):
			print("I'm byte")
			try:
				content = str((content).decode('utf-8'))
			except:
				content = str(content)
		else:
			print(type(content))
			content = str(content)
			print("I'm unicode")
		return content
	def ccurlT(self,url,rfr):
		hdr = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0'
		content = ccurl(url)
		return content
	def download(self, url,option):
		if option.lower() == 'play with animewatch':
			final_url = ''
			self.ui.epn_name_in_list = self.title_page
			print(self.ui.epn_name_in_list)
			if self.ui.mpvplayer_val.processId() > 0:
				self.ui.mpvplayer_val.kill()
			final_url = get_yt_url(url.toString(),self.ui.quality_val)
			if final_url:
				self.ui.watchDirectly(final_url,self.ui.epn_name_in_list,'no')
				self.ui.tab_5.show()
				self.ui.frame1.show()
				self.ui.tab_2.setMaximumWidth(400)
		elif option.lower() == 'add as local playlist':
			self.get_playlist = True
			if self.playlist_dict:
				print(self.get_playlist,'=get_playlist')
				self.add_playlist(self.playlist_name)
		elif option.lower() == 'download':
			if self.ui.quality_val == 'sd480p':
				txt = "Video can't be saved in 480p, Saving in either HD or SD"
				subprocess.Popen(['notify-send',txt])
				quality = 'hd'
			else:
				quality = self.ui.quality_val
			finalUrl = get_yt_url(url.toString(),quality)
			finalUrl = finalUrl.replace('\n','')
			title = self.title_page+'.mp4'
			title = title.replace('"','')
			title = title.replace('/','-')
			if os.path.exists(self.ui.default_download_location):
				title = os.path.join(self.ui.default_download_location,title)
			else:
				title = os.path.join(self.ui.tmp_download_folder,title)
				#title = '/tmp/AnimeWatch/'+title
			command = "wget -c --user-agent="+'"'+self.hdr+'" '+'"'+finalUrl+'"'+" -O "+'"'+title+'"'
			print (command)		
			self.ui.infoWget(command,0)
			
		elif option.lower() == 'get subtitle (if available)':
			self.ui.epn_name_in_list = self.title_page
			print(self.ui.epn_name_in_list)
			get_yt_sub(url.toString(),self.ui.epn_name_in_list,self.yt_sub_folder,self.ui.tmp_download_folder)
			
		elif option.lower() == 'season episode link':
			if self.site != "Music" and self.site != "PlayLists":
				self.ui.getTvdbEpnInfo(url.toString())
				
		elif option.lower() == 'artist link' or option.lower() == 'series link':
			self.ui.posterfound(url.toString())
			self.ui.copyImg()
			self.ui.copySummary()
		else:
			print ("Hello")
			hdr = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0'
			url1 = str(url.toString())
			print (url1)
			url_artist = url1
			found = ""
			url1Code = url1.split('/')[-1]
			
			final_found = False
			
			t_content = ccurl(url1+'#'+'-I')
			if 'image/jpeg' in t_content and not 'Location:' in t_content:
				final_found = True
			elif 'image/jpeg' in t_content and 'Location:' in t_content:
				m = re.findall('Location: [^\n]*',t_content)
				found = re.sub('Location: |\r','',m[0])
				url1 = found
				final_found = True
			elif not self.img_url.isEmpty():
				url1 = self.img_url.toString()
				final_found = True
			if self.site == "Music":
				if (self.ui.list3.currentItem().text())=="Artist":
					name = str(self.ui.list1.currentItem().text())
				else:
					r = self.ui.list2.currentRow()
					name = self.epnArrList[r].split('	')[2]
			else:
				name = str(self.ui.list1.currentItem().text())
				
			if '/' in name:
					name = name.replace('/','-')
					
			if (url1.endswith('.jpg') or final_found) and (self.site!='Music'):
				final = url1
				if self.site == "Local":
					if name.startswith('@'):
						name1 = name.split('@')[-1]
					else:
						name1 = name
					thumb = os.path.join(self.ui.tmp_download_folder,name1+'.jpg')
					#thumb = '/tmp/AnimeWatch/'+name1+'.jpg'
				else:
					thumb = os.path.join(self.ui.tmp_download_folder,name+'.jpg')
					#thumb = '/tmp/AnimeWatch/'+name+'.jpg'
				ccurl(final+'#'+'-o'+'#'+thumb)
			else:
				if self.site == "Music" and (option == "Download As Fanart" or option == "Download As Cover"):
					if 'last.fm' in url1:
						print(url1,'--artist-link---')
						#content = self.ccurl(url1,'')
						content = ccurl(url1)
						soup = BeautifulSoup(content,'lxml')
						link = soup.findAll('img')
						
						for i in link:
							if 'src' in str(i):
								j = i['src']
								k = j.split('/')[-1]
								if url1Code == k:
									found = j
									break
						print (str(found))
						u1 = found.rsplit('/',2)[0]
						u2 = found.split('/')[-1]
						final = u1 + '/770x0/'+u2
						print (final)
					elif final_found:
						final = url1
					else:
						final = ''
						
					if '/' in name:
						name = name.replace('/','-')
					thumb = os.path.join(self.ui.tmp_download_folder,name+'.jpg')
					#thumb = '/tmp/AnimeWatch/'+name+'.jpg'
					try:
						if final.startswith('http'):
							ccurl(final+'#'+'-o'+'#'+thumb)
					except:
						pass
			print (option)
			if str(option) == "Download As Fanart":
				self.ui.copyFanart()
			elif str(option) == "Download As Cover":
				self.ui.copyImg()
			
	
	def finishedDownload(self):
		self.ui.copyImg()
