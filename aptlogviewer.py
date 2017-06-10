#!/usr/bin/env python3

from re import search, findall
from os import listdir, linesep
from os.path import join, splitext
from datetime import datetime
from fileinput import input

APT_LOG_PATH = "/var/log/apt"

log_entries = []
installed_packages = []
upgraded_packages = []
removed_packages = []
purged_packages = []

# https://stackoverflow.com/questions/40731705/python-3-fileinput-both-compressed-and-endcoded-filehooks
def hook_compressed_encoded(encoding):
	def hook_compressed(filename, mode):
		# need to override mode because fileinput doesn't support rt
		mode = 'rt'

		ext = splitext(filename)[1]
		if ext == '.gz':
			import gzip
			return gzip.open(filename, mode, encoding=encoding)
		# apt logs are .gz but just for the sake of completeness
		elif ext == '.bz2':
			import bz2
			return bz2.open(filename, mode, encoding=encoding)
		else:
			return open(filename, mode, encoding=encoding)
	return hook_compressed

class LogEntry:

	ACTION_INSTALL = 1
	ACTION_UPGRADE = 2
	ACTION_REMOVE = 3
	ACTION_PURGE = 4

	def __init__(self):
		pass
		
	def set_start_date(self, date):
		self.start_date = date
		
	def get_start_date(date):
		return self.start_date
	
	def set_commandline(self, commandline):
		self.commandline = commandline
	
	def get_commandline(commandline):
		return self.commandline
		
	def set_action(self, action):
		self.action = action
		
	def get_action(action):
		return self.action
	
	def set_end_date(self, date):
		self.end_date = date
		
	def get_end_date(date):
		return self.end_date
			
log_files = [join(APT_LOG_PATH, x) for x in listdir(APT_LOG_PATH) if x.startswith("history.log")]
print(log_files)
with input(files=log_files, openhook=hook_compressed_encoded('UTF-8')) as log_content:
	entry = None
	for line in log_content:
	
		if line == linesep and entry is not None:
			start_date = datetime.strptime(
				search("Start-Date: .+", entry).group(0), "Start-Date: %Y-%m-%d  %H:%M:%S")
			end_date = datetime.strptime(
				search("End-Date: .+", entry).group(0), "End-Date: %Y-%m-%d  %H:%M:%S")
				
			commandline = search("Commandline: (.+)", entry)
			if commandline is None:
				# sometimes there are weird entries that contain no information
				continue
				
			install = search("Install: (.+)", entry)
			if install is not None:
				packages = findall(" ?(.+?):(.+?) \(([a-zA-Z0-9.+~-]+)(, automatic)?\),?", install.group(1))
				for name, arch, version, automatic in packages:
					if_automatic = True if automatic == ", automatic" else False
					pass
			
			upgrade = search("Upgrade: (.+)", entry)
			if upgrade is not None:
				packages = findall(" ?(.+?):(.+?) \(([a-zA-Z0-9.+~-]+), ([a-zA-Z0-9.+~-]+)\),?", upgrade.group(1))
				for name, arch, from_version, to_version in packages:
					pass
			
			remove = search("Remove: (.+)", entry)
			if remove is not None:
				packages = findall(" ?(.+?):(.+?) \(([0-9.+~-]*)\),?", remove.group(1))
				for name, arch, version in packages:
					pass
				
			entry = None
		
		else:
			if entry is None: entry = str()
			entry += line
