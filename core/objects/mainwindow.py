import wx
import core.support.TS_str as ts
from core.support.glob import printf

class MainWindow(wx.Frame):
	def __init__(self, parent, title, clock, logfile, ico):
		wx.Frame.__init__(self, parent, title=title, size=(500,500))
		self.clock = clock
		self.logfile = logfile
		self.ico = ico

		self.FROOD_TIMEOUT = 0  # Iterations of CallLater(local clock refresh) before timing out the Frood sequence
		self.FROOD_ACTIVE = 0  # Flag for if frood mode is active

		self.init_window()  # Panel elements
		self.init_widgets()  # Widgets
		self.init_events()  # Binds panel elements to widgets

		''' Final inits '''
		self.refresh_local_clock()  # Init local clock value
		self.refresh_remote_clock()  # Init remote clock value
		self.refreshConsole()  # Init console

		self.remoteTrack.Check()  # Default remote track state: active
		self.remoteAuto.Check()  # Default remote autosync state: active
		self.OnAutoSync()  # Begin auto sync
		self.remoteRefresh.Enable(False)
		self.remoteUpdate.Enable(False)

		self.init_layout()  # Arrange widgets last

	def init_window(self):
		self.SetBackgroundColour((0,0,0))  # Black background

		# Init labels
		self.dateLabel = wx.StaticText(self)
		self.date = wx.StaticText(self)
		self.localClockLabel = wx.StaticText(self)
		self.localClock = wx.StaticText(self, style=wx.BORDER_STATIC)
		self.remoteClockLabel = wx.StaticText(self)
		self.remoteClock = wx.StaticText(self, style=wx.BORDER_STATIC)
		self.console = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(502,500))

		# Menus
		self.fileMenu = wx.Menu()
		self.editMenu = wx.Menu()
		self.remoteMenu = wx.Menu()
		self.serverSubMenu = wx.Menu()
		self.helpMenu = wx.Menu()

		# Menu commands
		# File menu
		self.fileExit = self.fileMenu.Append(wx.ID_EXIT, 'Clos&e')

		# Edit menu
		self.editClear = self.editMenu.Append(wx.ID_CLEAR, '&Clear console')

		# Remote menu
		# Check server submenu
		self.remotePing0 = self.serverSubMenu.Append(wx.NewId(), 'Server &0')
		self.remotePing1 = self.serverSubMenu.Append(wx.NewId(), 'Server &1')
		self.remotePing2 = self.serverSubMenu.Append(wx.NewId(), 'Server &2')
		self.remotePing3 = self.serverSubMenu.Append(wx.NewId(), 'Server &3')

		self.remoteMenu.Append(wx.NewId(), '&Check server', self.serverSubMenu)
		self.remotePingAll = self.remoteMenu.Append(wx.NewId(), 'Check server&s')
		self.remoteMenu.Append(wx.ID_SEPARATOR)
		self.remoteRefresh = self.remoteMenu.Append(wx.NewId(), '&Refresh remote clock')
		self.remoteUpdate = self.remoteMenu.Append(wx.NewId(), 'Sync &local clock')
		self.remoteMenu.Append(wx.ID_SEPARATOR)
		self.remoteTrack = self.remoteMenu.AppendCheckItem(-1, '&Track remote')
		self.remoteAuto = self.remoteMenu.AppendCheckItem(wx.NewId(), '&Auto sync')

		# Help menu
		self.helpFeatures = self.helpMenu.Append(wx.NewId(), 'Command &descriptions')
		self.helpAbout = self.helpMenu.Append(wx.NewId(), '&About')

		# Create main menu.
		self.menuBar = wx.MenuBar()
		self.menuBar.Append(self.fileMenu,'&File')
		self.menuBar.Append(self.editMenu,'&Edit')
		self.menuBar.Append(self.remoteMenu,'&Remote')
		self.menuBar.Append(self.helpMenu,'&Help')

		self.SetMenuBar(self.menuBar)  # Init main menu



	def init_widgets(self):
		# Font definitions
		font_label = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL)
		font_labelHeader = wx.Font(23, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_BOLD)
		font_labelClock = wx.Font(35, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_BOLD)
		font_console = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL, faceName='Consolas')

		# Assign fonts to labels
		self.console.SetForegroundColour((255,255,255))  # Console text is white
		self.console.SetBackgroundColour((0,0,0))  # Console background is black
		self.console.SetFont(font_console)
		for item in [self.remoteClock, self.localClock, self.date, \
		             self.remoteClockLabel, self.localClockLabel, self.dateLabel]:
			item.SetForegroundColour((255,0,0))  # Default text is red

			# Assign font groups to labels
			if (item is self.remoteClock) or (item is self.localClock):
				item.SetFont(font_labelClock)
			elif (item is self.dateLabel) or (item is self.remoteClockLabel) or \
			     (item is self.localClockLabel):
				item.SetFont(font_label)
			elif item is self.date:
				item.SetFont(font_labelHeader)

		# Assign default label values
		self.remoteClock.SetLabel('XX:XX:XX XM')
		self.remoteClockLabel.SetLabel('Remote Time')
		self.localClockLabel.SetLabel('Local Time')
		self.dateLabel.SetLabel('Today is ')

	def init_layout(self):
		# Date line
		datesizer = wx.BoxSizer(wx.HORIZONTAL)
		datesizer.Add(self.dateLabel, 0, wx.TOP | wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
		datesizer.Add(self.date, 0, wx.TOP | wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

		# Vertical clock section
		timesizer = wx.BoxSizer(wx.VERTICAL)
		timesizer.Add(datesizer, 0, wx.ALL, 5)
		timesizer.Add(self.localClockLabel, 0, wx.TOP | wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_HORIZONTAL, 40)
		timesizer.Add(self.localClock, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)
		timesizer.Add(self.remoteClockLabel, 0, wx.TOP | wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_HORIZONTAL, 60)
		timesizer.Add(self.remoteClock, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 20)

		# Main panel elements, contains other sizers
		panelsizer = wx.BoxSizer(wx.HORIZONTAL)
		panelsizer.Add(self.console, 0, wx.ALL, 20)
		panelsizer.Add(timesizer, 0, wx.ALL, 20)

		# Init layout
		self.SetSizer(panelsizer)
		panelsizer.Fit(self)
		self.Layout()

	def init_events(self):
		# Frame level events
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		# Menu item events
		# File menu
		self.Bind(wx.EVT_MENU, self.OnClose, self.fileExit)

		# Edit menu
		self.Bind(wx.EVT_MENU, lambda cls: self.ClearConsole(), self.editClear)

		# Remote menu
		# Check server submenu
		self.Bind(wx.EVT_MENU, lambda ping: self.clock.pingserver(0, self), self.remotePing0)
		self.Bind(wx.EVT_MENU, lambda ping: self.clock.pingserver(1, self), self.remotePing1)
		self.Bind(wx.EVT_MENU, lambda ping: self.clock.pingserver(2, self), self.remotePing2)
		self.Bind(wx.EVT_MENU, lambda ping: self.clock.pingserver(3, self), self.remotePing3)

		self.Bind(wx.EVT_MENU, lambda ping: self.clock.pingserver('all', self), self.remotePingAll)

		self.Bind(wx.EVT_MENU, lambda refresh: self.update_times(manual=True), self.remoteRefresh)
		self.Bind(wx.EVT_MENU, lambda update: self.OnSync(), self.remoteUpdate)

		self.Bind(wx.EVT_MENU, lambda track: self.OnTrackRemote(), self.remoteTrack)
		self.Bind(wx.EVT_MENU, lambda auto: self.OnAutoSync(), self.remoteAuto)

		# Help menu
		self.Bind(wx.EVT_MENU, lambda describe: self.refreshConsole(self.console, ts.HelpInfo), self.helpFeatures)
		self.Bind(wx.EVT_MENU, self.ico.OnAbout, self.helpAbout)


		self.Show(True)

	def refreshConsole(self, console_str=None, additions=None):
		if (additions is not None) and (type(additions) is int):  # Integer flag for cls
			self.console.Clear()
			self.refreshConsole()
			return None  # Don't continue
		if console_str is None:  # For initializing
			fetch = ts.ConsoleHeader
		elif (type(console_str) is not str) and (additions is not None):
			fetch = console_str.GetLabel()
			fetch += additions

		self.console.AppendText(fetch)

	def OnTrackRemote(self):
		if not self.remoteTrack.IsChecked():  # Just turned off
			self.clock.terminate = True
			self.remoteRefresh.Enable(True)
			self.remoteUpdate.Enable(True)
			self.remoteAuto.Check(False)
			self.remoteAuto.Enable(False)
			self.OnAutoSync()

		else:
			self.clock.terminate = False
			self.remoteRefresh.Enable(False)
			self.remoteUpdate.Enable(False)
			self.remoteAuto.Enable(True)


	def OnAutoSync(self):
		if not self.remoteAuto.IsChecked():  # Just turned off
			pass
		else:
			if abs(self.clock.offset) > 0.5:
				self.ico.IconStatus(warn='OFFSET DETECTED')
				self.refreshConsole(self.console, '[AUTOSYNC OFFSET DETECTION]\r\n')
				self.refreshConsole(self.console, printf('Offset detected: %s seconds\r\n' % round(self.clock.offset, 2), timestamp=True))
				success = self.OnSync(auto=True)
			else: success = True

			if success:
				wx.CallLater(1000, self.OnAutoSync)
			else:
				self.ico.AdminError = True  # If not run as admin
				self.ico.IconStatus(flag=False)
				self.remoteAuto.Check(False)

	def OnClose(self, event):
		self.Hide()

	def update_times(self, local=False, manual=False):
		self.clock.update_times(manual=True, frame=self)


	def refresh_local_clock(self):
		self.localClock.SetLabel(self.clock.local_time)
		self.date.SetLabel(self.clock.local_day)
		self.localClock.GetParent().Layout()
		self.date.GetParent().Layout()


		wx.CallLater(1000, self.refresh_local_clock)

	def refresh_remote_clock(self, pause=False, manual=False):
		if (not self.clock.terminate) and (self.remoteTrack.IsChecked()):
			self.remoteClock.SetLabel(self.clock.remote_time)
			self.remoteClock.GetParent().Layout()
			wx.CallLater(1000, self.refresh_remote_clock, pause, False)
		elif manual:
			self.clock.update_times()
			self.refresh_remote_clock()
		else:
			self.remoteClock.SetLabel(self.clock.remote_time)
			self.remoteClock.GetParent().Layout()
			wx.CallLater(1000, self.refresh_remote_clock, True, False)

	def pingserver(self, serverno):
		self.clock.pingserver(serverno, self)

	def OnSync(self, auto=False):
		result = self.clock.OnSync(self)

		self.ico.IconStatus(flag=result)

		if auto:
			return result  # Pass failure to autosync so it stops trying

		if result:
			self.remoteTrack.Check(True)  # Set desired check condition for OnTrackRemote
			self.OnTrackRemote()

	def ClearConsole(self):
		self.refreshConsole(additions=0)


