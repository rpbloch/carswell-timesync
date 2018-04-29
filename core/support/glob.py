import os
import win32api
import ntplib
from datetime import datetime

def PingServer(ServerNo):
	'''
    Ping internet time server. There are four servers:
    0.north-america.pool.ntp.org
    1.north-america.pool.ntp.org
    2.north-america.pool.ntp.org
    3.north-america.pool.ntp.org
    '''
	c = ntplib.NTPClient()
	
	try:
		# Timeout is set to 0.5 seconds to avoid a network delay
		# causing a false detection of unsynchronized time
		response = c.request('%s.north-america.pool.ntp.org' % \
		                     ServerNo, version=3, timeout=0.5)
	except (ntplib.NTPException, ntplib.socket.timeout):
		# This error can be raised if the server cannot be contacted
		# and/or if the designated socket timeout has been reached
		return 'No response on server %s.\r\n' % ServerNo, False
	except ntplib.socket.gaierror:
		# This error is raised if the socket is closed. This will
		# only really happen if the internet is disconnected
		return 'Socket error. Check internet connection and try again.\r\n', False
	else:
		return response, True

def FixTime(UTCInternetTime, LocalComputerTime, LocalInternetTime, offset):
	'''
	This function is called when a discrepancy of more than 0.5 seconds
	is detected between the internet time and the system time.
	This function sets the system time to the internet time.
	repeat -> Bool (default: False), prevent the TimeSync_Runlog from
	being written to if this function is called to double-check a successful
	time fix
	'''
	DaysOfWeek = {'Mon' : 0, 'Tue' : 1, 'Wed' : 2, 'Thu' : 3, 'Fri' : 4, \
	              'Sat' : 5, 'Sun' : 6}  # Needed for system time
	corrYear = UTCInternetTime.year
	corrMonth = UTCInternetTime.month
	corrDay = UTCInternetTime.day
	corrHour = UTCInternetTime.hour
	corrMinute = UTCInternetTime.minute
	corrSecond = UTCInternetTime.second
	corrMillisecond = UTCInternetTime.microsecond // 1000  # Millisecond accuracy

	dayOfWeek = DaysOfWeek[UTCInternetTime.strftime('%a')]

	try:
		win32api.SetSystemTime(corrYear, corrMonth, dayOfWeek, corrDay, \
		                       corrHour, corrMinute, corrSecond, \
		                        corrMillisecond)  # Set system time
	except win32api.error:
		# In testing, this error only occurs when the program
		# does not have administrator privileges.
		return False, 'Synchronization failed. Please run as administrator.\r\n'
		#LogFile(LocalComputerTime, LocalUTCInternetTime, offset, \
		#        'NO')  # Log unsuccessful attempt
		#Exit()
	else:
		return True, 'Synchronization success!\r\n'
		#LogFile(LocalComputerTime, LocalUTCInternetTime, offset, \
		#        'YES', repeat=repeat)  # Log successful attempt

def formatTime(now):
	weekday = { 0 : 'Monday', 1 : 'Tuesday', 2 : 'Wednesday', 3 : 'Thursday', \
            4 : 'Friday', 5 : 'Saturday', 6 : 'Sunday' }
	month = { 1 : 'Jan', 2 : 'Feb', 3 : 'Mar', 4 : 'Apr', 5 : 'May', 6 : 'Jun', \
          7 : 'Jul', 8 : 'Aug', 9 : 'Sep', 10 : 'Oct', 11 : 'Nov', 12 : 'Dec' }

	if now.hour > 12:
		hour = now.hour - 12
		meridian = 'PM'
	elif now.hour == 12:
		hour = now.hour
		meridian = 'PM'
	elif now.hour == 0:
		hour = 12
		meridian = 'AM'
	else:
		hour = now.hour
		meridian = 'AM'

	dateinfo = '%s %s %d, %4d' % (weekday[now.weekday()], month[now.month], \
	                               now.day, now.year)
	timeinfo = '%2d:%02d:%02d %s' % (hour, now.minute, now.second, meridian)

	return dateinfo, timeinfo

def printf(string, timestamp=False):
	if timestamp:
		timestamp = str(datetime.now())  # Total string
		timestamp = timestamp.split('.')[0]  # Ignore milliseconds
		return '%s\n>>> %s\r\n' % (timestamp, string)
	else:
		return '>>> %s\r\n' % string