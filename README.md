# TimeSync

TimeSync is a Windows clock time synchronization program written specifically for use at the Allan I. Carswell Astronomical Observatory. It runs in the background to ensure the local computer time is synchronized to within 0.5 seconds of a [public NTP server](http://www.pool.ntp.org/en/).

## Running the program

Make a copy of this distribution, keeping the directory tree intact. Then use Python 3 to run timesync.py and that should be it! Make sure to have installed the required dependencies.

### Dependencies

[Datetime](https://docs.python.org/2/library/datetime.html) - Used for interacting with the local clock and time formatting

[Numpy](http://www.numpy.org/) - Used to calculate the average offset. Future versions may bypass this and include a local average method

[NTPLib](https://pypi.python.org/pypi/ntplib/) - Module to interact with the NTP servers

[wxPython](https://www.wxpython.org/) - Library for building the GUI


## Authors

* **Richard Bloch** - *Initial work and maintenance*


## Acknowledgments

* The Froods, for making the observatory the place to be!
