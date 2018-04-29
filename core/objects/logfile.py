import os

class LogFile(object):
	def __init__(self):
		CURRENT_USER_HOME = os.path.expanduser('~')
		self.LOGFILE_NAME = 'TimeSyncLog.csv'		
		self.LOGFILE_PATH = '%s\\%s' % (CURRENT_USER_HOME, 'Documents\\TimeSync')	
		
		self.exists()  # Create file if it doesn't already exist
	
	def exists(self):
		''' Check if logfile already exists '''
	
		if not os.path.exists('%s\\%s' % (self.LOGFILE_PATH, self.LOGFILE_NAME)):  # Logfile doesn't exist
			os.makedirs(self.LOGFILE_PATH, exist_ok=True)  # Make path to dir
			self.create()
		
	def create(self):
		''' Creates logfile if not already in expected directory '''
	
		with open('%s\\%s' % (self.LOGFILE_PATH, self.LOGFILE_NAME), 'w') as LOG:
				LOG.write('%s,%s,%s,%s\n' % ( \
			        'Local computer time', \
			        'Remote server time', \
			        'Offset (seconds)', \
			        'Action taken' ))
		
	def log_write(self):
		''' Log instances of unsynchronized time '''
		pass  # Main write action goes here
	
