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



import sys
import urllib
import pycurl
from io import StringIO,BytesIO
import re
import random
import subprocess
from subprocess import check_output
from bs4 import BeautifulSoup
import os.path
from subprocess import check_output
from player_functions import send_notification,ccurl
try:
	import libtorrent as lt
	from stream import ThreadServer,TorrentThread,get_torrent_info,get_torrent_info_magnet
except:
	notify_txt = 'python3 bindings for libtorrent are broken\nTorrent Streaming feature will be disabled'
	send_notification(notify_txt)

from PyQt5 import QtWidgets
import shutil
#from hurry.filesize import size

def naturallysorted(l): 
	convert = lambda text: int(text) if text.isdigit() else text.lower() 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	return sorted(l, key = alphanum_key)



def replace_all(text, di):
	for i, j in di.iteritems():
		text = text.replace(i, j)
	return text





class Torrent():
	def __init__(self,tmp):
		self.hdr = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0'
		self.tmp_dir = tmp
	def getOptions(self):
			criteria = ['Open','History','LocalStreaming']
			return criteria
		
	def getFinalUrl(self,name,epn,local_ip,status,path_folder,session,ui,progress,tmp_dir):
		
		index = int(epn)
		ip_n = local_ip.rsplit(':',1)
		ip = ip_n[0]
		port = int(ip_n[1])
		if status.lower() =='first run':
			thread_server = ThreadServer(ip,port)
			thread_server.start()
			#ses = set_torrent_session()
		path = path_folder
		
		home = os.path.join(os.path.expanduser('~'),'.config','AnimeWatch','History','Torrent')
		torrent_dest = os.path.join(home,name+'.torrent')
		
		#home = os.path.expanduser('~')+'/.config/AnimeWatch/History/Torrent/'
		#torrent_dest = home+name+'.torrent'
		print(torrent_dest,index,path)
		
		
		handle,ses,info,cnt,cnt_limit,file_name = get_torrent_info(torrent_dest,index,path,session,ui,progress,tmp_dir)
		torrent_thread = TorrentThread(handle,cnt,cnt_limit,ses)
		torrent_thread.start()
		
		
		url = 'http://'+ip+':'+str(port)+'/'
		print(url,'-local-ip-url')
		if status.lower() == 'first run':
			return url,thread_server,torrent_thread,ses,handle
		else:
			return url,torrent_thread,ses,handle
		
		
	def search(self,name):
		m = ['Not Available']
		return m
		
	def getCompleteList(self,opt,ui,progress,tmp_dir):
		m = ['Not Able To Open']
		if opt == 'Open':
			MainWindow = QtWidgets.QWidget()
			item, ok = QtWidgets.QInputDialog.getText(MainWindow, 'Input Dialog', 'Enter Torrent Url or Magnet Link or local torrent file path')
			if ok and item:
				if (item.startswith('http') or item.startswith('/')) and item.endswith('.torrent'):
					home = os.path.join(os.path.expanduser('~'),'.config','AnimeWatch','History','Torrent')
					#name1 = item.split('/')[-1].replace('.torrent','')
					name1 = os.path.basename(item).replace('.torrent','')
					#torrent_dest1 = '/tmp/AnimeWatch/'+name1+'.torrent'
					torrent_dest1 = os.path.join(tmp_dir,name1+'.torrent')
					if not os.path.exists(torrent_dest1):
						if item.startswith('http'):
							ccurl(item+'#'+'-o'+'#'+torrent_dest1)
						else:
							shutil.copy(item,torrent_dest1)
					if os.path.exists(torrent_dest1):
						info = lt.torrent_info(torrent_dest1)
						name = info.name()
						torrent_dest = os.path.join(home,name+'.torrent')
						shutil.copy(torrent_dest1,torrent_dest)
					m = [name]
				elif item.startswith('magnet:'):
					
					torrent_handle,stream_session,info = get_torrent_info_magnet(item,tmp_dir,ui,progress,tmp_dir)
					torrent_file = lt.create_torrent(info)
					
					home = os.path.join(os.path.expanduser('~'),'.config','AnimeWatch','History','Torrent')
					name = info.name()
					torrent_dest = os.path.join(home,name+'.torrent')
					
					with open(torrent_dest, "wb") as f:
						f.write(lt.bencode(torrent_file.generate()))
						
					torrent_handle.pause()
					stream_session.pause()
					m = [name]
		return m
	
	def getEpnList(self,name,opt,depth_list,extra_info,siteName,category):
		summary = ""
		#home = os.path.expanduser('~')+'/.config/AnimeWatch/History/Torrent/'
		home = os.path.join(os.path.expanduser('~'),'.config','AnimeWatch','History','Torrent')
		torrent_dest = os.path.join(home,name+'.torrent')
		info = lt.torrent_info(torrent_dest)
		file_arr = []
		for f in info.files():
			file_path = f.path
			#if '/' in f.path:
			#	file_path = file_path.split('/')[-1]
			file_path = os.path.basename(file_path)	
			file_arr.append(file_path)
		
		#file_arr.append('No.jpg')
		#file_arr.append('Summary Not Available')
		#return file_arr
		record_history = True
		return (file_arr,'Summary Not Available','No.jpg',record_history,depth_list)
		
	def getNextPage(self,opt,pgn,genre_num,name):
		m = ['Nothing']
		return m
