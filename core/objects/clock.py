import wx
import numpy as np
from datetime import datetime
from core.support.glob import formatTime, PingServer, FixTime, printf

class Clock(object):
	def __init__(self):
		self.terminate = False  # Remote ping killswitch
		self.last_good_server = 0  # Server number of previous successful ping
		self.remote_time = 'XX:XX:XX XM'  # Default blank remote timestamp
		self.refresh_local_clock()  # Initial time read
		self.refresh_remote_clock()  # Initial remote time read

	def update_times(self, local=False, manual=False, frame=False):
		'''
		Updates the clocks depending on the arguments.
		By default it returns the remote time

		Args:
		local -- Bool. True if returned time is local clock from datetime
				       False if returned time is remote time

		Returns:
		remote -- Passed from remote_clock_fetch on a failure.
		datetime.fromtimestamp(remote.orig_time + remote.offset) -- Remote time
		datetime.now() -- Local time
		'''
		if local: return datetime.now()  # If we're looking also for the local time, at least return that.
		else: remote = self.remote_clock_fetch(manual=manual, frame=frame)  # Get remote timestamp

		if not remote:  # If Nonetype detected, fetch has failed so:
			self.offset = 0
			return remote

		self.offset = remote.offset

		#if manual:  # Why is this here?
		#	self.refresh_remote_clock(manual=True)
		if local:  # If only local clock is (?)requested(?)
			return datetime.now()
		else:  # Looks like it either returns local time or remote time.
			return datetime.fromtimestamp(remote.orig_time + remote.offset)

	def refresh_local_clock(self):
		'''
		Updates the local time, independent of the NTPLib response objects.
		The GUI is an approximation so the counters do not have to be perfectly
		accurate. This also helps keep the local clock display accurate.
		'''
		self.fetch_time = self.update_times(local=True)
		self.local_day, self.local_time = formatTime(self.fetch_time)

		wx.CallLater(1000, self.refresh_local_clock)

	def refresh_remote_clock(self, pause=False, manual=False):
		# If it hasn't been killed (default behaviour) or is manually activated
		if (not self.terminate) or (manual):
			self.remote_time = self.update_times()
			if self.remote_time:
				self.remote_time = formatTime(self.remote_time)[1]
			else:
				self.remote_time = 'XX:XX:XX XM'
			wx.CallLater(1000, self.refresh_remote_clock, pause, False)
		else:  # If killed process and not manually activated
			wx.CallLater(1000, self.refresh_remote_clock, True, False)

	def remote_clock_fetch(self, manual=False, frame=False):
		'''
		Gets the remote time.
		Returns the response variable (ntplib object on a success or
		a string on a PingServer fail) or None on a fail triggered here.
		'''
		if manual:  # Only activatable if frame is open, prints to console.
			frame.refreshConsole(frame.console, '[PINGING ONLINE SERVERS FOR CURRENT TIME]\r\n')

		for i in range(self.last_good_server, 4):  # Sequentially ping servers
			if manual:  # Prints to console if manually activated.
				frame.refreshConsole(frame.console, '>>> Pinging server %s...\r\n' % i)

			response, success = PingServer(i)

			if success:
				if manual:
					frame.refreshConsole(frame.console, '>>> Success on server %s!\r\n\r\n' % i)
				break  # Take first successful value

			elif type(response) is str:  # Error conditions
				if manual:  # Print received condition to terminal
					frame.refreshConsole(frame.console, response)
				self.last_good_server += 1  # Move along
				if self.last_good_server == 4:  # Executed when all servers timeout
					if manual:
						frame.refreshConsole(frame.console, '>>> No response on any server. Connection unsuccessful.\r\n')
					response = None
					break  # Prevents going beyond our fixed server number(?)
			else:
				if manual:
					frame.refreshConsole(frame.console, '>>> %s\r\n' % response)
		else:  # Reset and try again from beginning
			self.last_good_server = 0
			response, success = PingServer(self.last_good_server)
			if success:
				if manual:
					frame.refreshConsole(frame.console, '>>> Pinging server %s...\r\n' % i)
				return response
			else:
				return None

		return response

	def pingserver(self, serverno, frame):
		if serverno == 'all':
			offsets = []
			for servernum in range(4):
				response = self.pingserver(servernum, frame)
				if type(response) is not str:
					offsets.append(response.offset)
			frame.refreshConsole(frame.console, '\r\n      AVERAGE OFFSET: %s%s\r\n\r\n' % (' 'if np.average(offsets) < 0 else ' '*2, np.average(offsets)))
			return None

		servernames = { servernum : serverIP for servernum, serverIP in zip(range(4), ['%s.north-america.pool.ntp.org' % i for i in range(4)])}

		frame.refreshConsole(frame.console, '[DIAGNOSTICS FOR SERVER %s <%s>]\r\n' % (serverno, servernames[serverno]))
		frame.refreshConsole(frame.console, '>>> Pinging server %s...\r\n' % serverno)

		response, success = PingServer(serverno)

		if success:
			success_note = '>>> Success on server %s!' % serverno
			orig_time = '>>> response.orig_time: %s' % response.orig_time
			orig_time_readable = '%s%s' % (' '*(len(orig_time.split(' ')[1])+5), datetime.fromtimestamp(response.orig_time))
			offset = '>>> response.offset: %s%s' % (' '*2 if response.offset < 0 else ' '*3, response.offset)

			frame.refreshConsole(frame.console, '%s\r\n%s\r\n%s\r\n%s\r\n\r\n' % (success_note, orig_time, orig_time_readable, offset))

		else:
			frame.refreshConsole(frame.console, '%s\r\n%s\r\n\r\n' % ('>>> Problem encountered on server %s' % serverno, '>>> Socket returned: %s' % response))

		return response

	def OnSync(self, frame):
		response = self.remote_clock_fetch(manual=True, frame=frame)
		if not response:
			return False

		LocalComputerTime = datetime.fromtimestamp(response.orig_time)
		LocalInternetTime = datetime.fromtimestamp(response.orig_time + \
		                                           response.offset)
		UTCInternetTime = datetime.utcfromtimestamp(response.orig_time + \
		                                            response.offset)

		result, message = FixTime(UTCInternetTime, LocalComputerTime, LocalInternetTime,\
		                 response.offset)

		frame.refreshConsole(frame.console, printf(message, timestamp=True))

		return result