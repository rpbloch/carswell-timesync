def makeHeaderLine(content, fill=False):
	# To make console header lines
	# content: Words to be fit inside
	# fill: a line of repeated strings

	if (not fill) and (len(content) > 56):  # Make fit into console width
		content = content[:56]

	spacers = 56 - len(content)
	left_spacer = (spacers // 2) + (spacers % 2)
	right_spacer = spacers // 2

	if fill:
		if content == '=':
			line = '+%s+\r\n' % ('='*56)
		else:
			line = '|%s|\r\n' % (content*56)
	else:
		line = '|%s%s%s|\r\n' % (' '*left_spacer, content, ' '*right_spacer)

	return line


def makeHeader(lines):
	# To make console headers
	header = []
	bookend = makeHeaderLine('=', fill=True)
	separator = makeHeaderLine(' ', fill=True)

	for i, line in enumerate(lines):
		lines[i] = makeHeaderLine(line)

	spaced_lines = [item for sublist in \
	                [(line, separator) for line in lines] \
	                for item in sublist][:-1]

	header.append(bookend)
	header.extend(spaced_lines)
	header.append(bookend)

	return header




# GUI STUFF
# About window text
AboutWindow = \
    """TimeSync 2.0 (2018)

A custom time synchronization tool for the Allan I. Carswell Observatory.

It automatically synchronizes the local computer clock to a remote
server via NTP. The application can run in the system tray, but a
window can be opened for inspection and troubleshooting.

Tray icon colour codes:
GREEN: Everything is running normally
ORANGE: The application is not running normally
RED: The application can not synchronize at all"""

# Console printouts
# Normal header
CH1 = 'ALLAN I. CARSWELL ASTRONOMICAL OBSERVATORY'
CH2 = 'COMPUTER TIME SYNCHRONIZATION TOOL'
CH3 = 'Richard Bloch, 2018 (v2.0 2018)'
ConsoleHeader = '%s\r\n' % ''.join(makeHeader([CH1, CH2, CH3]))





# About functions
# Feature description text
HelpInfo = \
    """[PROGRAM WINDOW COMMANDS]

CHECK SERVER:
Checks specified server status. Healthy output should
display a ping, success, (local) ping timestamp, and clock
offset.
The latter two are given in seconds, though the timestamp
is also presented in a readable format.

On a failed ping, a specific socket error will display.


CHECK SERVERS:
Checks server status as in \'Check server\', but for all
servers. An average response.offset value is given at the
end.


REFRESH REMOTE CLOCK:
Manually refresh the remote clock value once only. Enabled
when \'Track remote\' is unchecked.


SYNC LOCAL CLOCK:
Manually sync the local computer time to the server time
once only. Enabled when \'Track remote\' is unchecked.


TRACK REMOTE:
When checked, the program clock tracks both the remote
server time and the local time. When unchecked, the
program clock tracks only the local time. Must be checked
to run \'Auto sync\'.

When unchecked, the manual track and sync features will
still fetch the server time.


AUTO SYNC:
When checked, the program will attempt to sync the clocks
whenever they disagree by more than 0.5 seconds.
This check is run every second.

"""

