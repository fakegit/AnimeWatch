import os
import shutil
from tempfile import mkstemp,mkdtemp
import urllib
import pycurl
from io import StringIO,BytesIO
import subprocess
import re
from get_functions import wget_string,get_ca_certificate
		
def send_notification(txt):
	if os.name == 'posix':
		try:
			subprocess.Popen(['notify-send',txt])
		except Exception as e:
			print(e)
			
def open_files(file_path,lines_read=True):
	if os.path.exists(file_path):
		if lines_read:
			lines = ''
			try:
				f = open(file_path,'r')
				lines = f.readlines()
				f.close()
			except UnicodeDecodeError as e:
				try:
					print(e)
					f = open(file_path,encoding='utf-8',mode='r')
					lines = f.readlines()
					f.close()
				except UnicodeDecodeError as e:
					print(e)
					f = open(file_path,encoding='ISO-8859-1',mode='r')
					lines = f.readlines()
					f.close()
			except Exception as e:
				print(e)
				print("Can't Decode")
		else:
			lines = ''
			try:
				f = open(file_path,'r')
				lines = f.read()
				f.close()
			except UnicodeDecodeError as e:
				try:
					print(e)
					f = open(file_path,encoding='utf-8',mode='r')
					lines = f.read()
					f.close()
				except UnicodeDecodeError as e:
					print(e)
					f = open(file_path,encoding='ISO-8859-1',mode='r')
					lines = f.read()
					f.close()
			except Exception as e:
				print(e)
				lines = "Can't Decode"
	else:
		if lines_read:
			lines = []
		else:
			lines = 'Not Available'
	return lines

def get_config_options(file_name,value_field):
	req_val = ''
	if os.path.exists(file_name):
		lines = open_files(file_name,True)
		for i in lines:
			try:
				i,j = i.split('=')
			except Exception as e:
				print(e,'wrong values in config file')
				return req_val
			j = j.strip()
			if str(i.lower()) == str(value_field.lower()):
				req_val = j
				break
	return req_val


def naturallysorted(l): 
	convert = lambda text: int(text) if text.isdigit() else text.lower() 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	return sorted(l, key = alphanum_key)

def replace_all(text, di):
	for i, j in di.iteritems():
		text = text.replace(i, j)
	return text

def get_tmp_dir():
	TMPDIR = ''
	try:
		option_file = os.path.join(os.path.expanduser('~'),'.config','AnimeWatch','other_options.txt')
		tmp_option = get_config_options(option_file,'TMP_REMOVE')
		if tmp_option:
			if tmp_option.lower() == 'no':
				TMPDIR = os.path.join(os.path.expanduser('~'),'.config','AnimeWatch','tmp')
			else:
				TMPDIR = mkdtemp(suffix=None,prefix='AnimeWatch_')
			
		else:
			TMPDIR = os.path.join(os.path.expanduser('~'),'.config','AnimeWatch','tmp')
	except:
		TMPDIR = os.path.join(os.path.expanduser('~'),'.config','AnimeWatch','tmp')
	return TMPDIR
		
		


def write_files(file_name,content,line_by_line):
	if os.name == 'nt':
		tmp_new_file = os.path.join(os.path.expanduser('~'),'.config','AnimeWatch','tmp','tmp_write.txt')
	else:
		fh, tmp_new_file = mkstemp()
	file_exists = False
	write_operation = True
	if os.path.exists(file_name):
		file_exists = True
		shutil.copy(file_name,tmp_new_file)
		print('copying ',file_name,' to ',tmp_new_file)
	try:
		if type(content) is list:
			bin_mode = False
			f = open(file_name,'w')
			j = 0
			for i in range(len(content)):
				fname = content[i].strip()
				if j == 0:
					try:
						f.write(fname)
					except UnicodeEncodeError as e:
						print(e,file_name+' will be written in binary mode')
						bin_mode = True
						f.close()
						break
				else:
					try:
						f.write('\n'+fname)
					except UnicodeEncodeError as e:
						print(e,file_name+' will be written in binary mode')
						bin_mode = True
						f.close()
						break
				j = j+1
			if not bin_mode:
				f.close()
			else:
				f = open(file_name,'wb')
				j = 0
				for i in range(len(content)):
					fname = content[i].strip()
					if j == 0:
						f.write(fname.encode('utf-8'))
					else:
						f.write(('\n'+fname).encode('utf-8'))
					j = j+1
				f.close()
		else:
			if line_by_line:
				content = content.strip()
				if not os.path.exists(file_name) or (os.stat(file_name).st_size == 0):
					f = open(file_name,'w')
					bin_mode = False
					try:
						f.write(content)
					except UnicodeEncodeError as e:
						print(e,file_name+' will be written in binary mode')
						f.close()
						bin_mode = True
						
					if bin_mode:
						f = open(file_name,'wb')
						f.write(content.encode('utf-8'))
						f.close()
				else:
					f = open(file_name,'a')
					bin_mode = False
					try:
						f.write('\n'+content)
					except UnicodeEncodeError as e:
						print(e,file_name+' will be written in binary mode')
						f.close()
						bin_mode = True
						
					if bin_mode:
						f = open(file_name,'ab')
						f.write(('\n'+content).encode('utf-8'))
						f.close()
					
					
			else:
				f = open(file_name, 'w')
				bin_mode = False
				try:
					f.write(content)
				except UnicodeEncodeError as e:
					print(e,file_name+' will be written in binary mode')
					f.close()
					bin_mode = True
				if bin_mode:
					f = open(file_name,'wb')
					f.write(content.encode('utf-8'))
					f.close()
	except Exception as e:
		write_operation = False
		print(e,'error in handling file, hence restoring original')
		if file_exists:
			shutil.copy(tmp_new_file,file_name)
			print('copying ',tmp_new_file,' to ',file_name)
	if os.path.exists(tmp_new_file):
		try:
			os.remove(tmp_new_file)
			if write_operation:
				print('write operation on: '+file_name+' successful and successfully removed temp file: '+tmp_new_file)
			else:
				print('write operation on: '+file_name+' failed hence restored original and successfully removed temp file: '+tmp_new_file)
		except Exception as e:
			if write_operation:
				print(e,' : write operation on '+file_name+' successful but remove '+tmp_new_file+' manually')
			else:
				print(e,' : write operation on '+file_name+' failed hence original restored, but remove '+tmp_new_file+' manually')


get_lib = get_config_options(os.path.join(os.path.expanduser('~'),'.config','AnimeWatch','other_options.txt'),'GET_LIBRARY')

if get_lib.lower() == 'pycurl':
	from get_functions import ccurl
	print('--using pycurl--')
elif get_lib.lower() == 'curl':
	from get_functions import ccurlCmd as ccurl
	print('--using curl--')
elif get_lib.lower() == 'wget':
	from get_functions import ccurlWget as ccurl
	print('--using wget--')
else:
	from get_functions import ccurl
	print('--using default pycurl--')

		
		
		