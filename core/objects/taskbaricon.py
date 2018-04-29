import wx
import wx.adv as wxa
import core.support.Icons as Icons
import core.support.TS_str as ts
from core.objects.clock import Clock
from core.objects.mainwindow import MainWindow
from core.objects.logfile import LogFile

class TaskBarIcon(wxa.TaskBarIcon):
	def __init__(self):
		if self.SingleInstance():  # Prevent multiple instances from running
			self.Destroy()

		super(TaskBarIcon, self).__init__()

		self.AdminError = False  # If not run as administrator
		self.logfile = LogFile()  # Init log
		self.clock = Clock()  # Init clock
		self.IconStatus()  # Init icon
		self.frame = MainWindow(None, "TimeSync", self.clock, self.logfile, self)

		self.frame.SetIcons(wx.IconBundle(Icons.PyEmbeddedImage.GetIcon(Icons.TS_LOGO)))
		self.CheckHealth()  # Begin internal diagnostic loop

		self.Bind(wxa.EVT_TASKBAR_LEFT_DCLICK, self.OnWindow)




	def SingleInstance(self):
		self.name = 'TimeSync-%s' % wx.GetUserId()
		self.instance = wx.SingleInstanceChecker(self.name)

		if self.instance.IsAnotherRunning():
			wx.MessageBox('TimeSync is already running!', 'TimeSync already running')
			return True



	def CreatePopupMenu(self):
		menu = wx.Menu()

		self.menuAbout = menu.Append(wx.NewId(), 'About')
		menu.Append(wx.ID_SEPARATOR)
		self.menuShow = menu.AppendCheckItem(wx.NewId(), 'Show Window')
		self.menuFix = menu.Append(wx.NewId(), 'Auto fix')
		self.menuTools = menu.Append(wx.NewId(), 'devtools')
		menu.Append(wx.ID_SEPARATOR)
		self.menuExit = menu.Append(wx.NewId(), 'Exit Program')

		if self.frame.IsShown():
			self.menuShow.Check()
		if self.BanAutoFix: self.menuFix.Enable(False)
		else: self.menuFix.Enable(True)


		self.Bind(wx.EVT_MENU, self.OnAbout, self.menuAbout)
		self.Bind(wx.EVT_MENU, self.OnWindow, self.menuShow)
		self.Bind(wx.EVT_MENU, self.AutoFix, self.menuFix)
		self.Bind(wx.EVT_MENU, self.OnTools, self.menuTools)
		self.Bind(wx.EVT_MENU, self.OnExit, self.menuExit)

		return menu

	def CheckHealth(self, fixinfo=False):
		if isinstance(self.clock.offset, int):  # Happens when clock can't fetch
			fail = 1
		elif self.AdminError:
			fail = 1
		elif (not self.frame.remoteTrack.IsChecked()) or (self.clock.terminate):
			fail = 'NOT TRACKING'
		elif not self.frame.remoteAuto.IsChecked():
			fail = 'NOT AUTOSYNCING'
		else:
			fail = 0

		if fixinfo:
			return fail

		if fail:
			if isinstance(fail, int):
				self.IconStatus(flag=False)
				self.BanAutoFix = True
			else:
				self.IconStatus(warn=fail)
				self.BanAutoFix = False
		else:
			self.BanAutoFix = True
			self.IconStatus()

		wx.CallLater(500, self.CheckHealth)

	def AutoFix(self, event=None):
		diagnostic = self.CheckHealth(fixinfo=True)
		if diagnostic == 1:  # Ideally this shouldn't be triggered
			self.BanAutoFix = True

		if diagnostic == 'NOT TRACKING':
			self.frame.remoteTrack.Check()
			self.frame.OnTrackRemote()
			diagnostic = self.CheckHealth(fixinfo=True)
			if (diagnostic == 'NOT TRACKING') or (diagnostic == 1):
				self.BanAutoFix = True
			self.AutoFix()

		if diagnostic == 'NOT AUTOSYNCING':
			self.frame.remoteAuto.Check()
			self.frame.OnAutoSync()
			diagnostic = self.CheckHealth(fixinfo=True)
			if (diagnostic == 'NOT AUTOSYNCING') or (diagnostic == 1):
				self.BanAutoFix = True
			self.AutoFix()




	def IconStatus(self, flag=True, warn=False):
		# Flag is True if icon is to switch to green, else False for red
		# This is called from MainWindow.OnSync to switch colour on a fail sync
		# Warn is called whenever the program can't be sure the clocks are synced
		# and is a string for the icon tooltip to point at the issue
		if warn:
			self.TRAY_ICON = Icons.PyEmbeddedImage.GetIcon(Icons.TICON_WARN)
			self.TRAY_TOOLTIP = 'TimeSync (%s)' % warn
		elif flag:
			self.TRAY_ICON = Icons.PyEmbeddedImage.GetIcon(Icons.TICON_OK)
			self.TRAY_TOOLTIP = 'TimeSync (SYNCED)'
		else:
			self.TRAY_ICON = Icons.PyEmbeddedImage.GetIcon(Icons.TICON_ERR)
			self.TRAY_TOOLTIP = 'TimeSync (CANNOT SYNC)'

		self.SetIcon(self.TRAY_ICON, self.TRAY_TOOLTIP)

	def OnWindow(self, event):
		ACTIVATE_BY_DCLICK = 10299
		CLOSE_BY_MENU = 10018
		if not self.frame.IsShown():
			self.frame.Show()
			self.frame.Restore()
		else:
			self.frame.Hide()



	def OnTools(self, event):
		pass  # For later expansion

	def OnAbout(self, event):
		dlg = wx.MessageDialog(self.frame, ts.AboutWindow, "About TimeSync", wx.OK)
		dlg.ShowModal()
		dlg.Destroy()

	def OnExit(self, event):
		wx.CallAfter(self.frame.Destroy)
		wx.CallAfter(self.Destroy)