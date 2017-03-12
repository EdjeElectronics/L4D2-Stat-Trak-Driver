# L4D2-Stat-Trak-Driver
Python 3 driver for Raspberry Pi-powered Left 4 Dead 2 Stat Tracker. Downloads Left 4 Dead 2 stats from a Steam profile page and displays them on an LCD. See my project video at https://www.youtube.com/watch?v=8G3mvy-2taM!

## Dependencies
Non-standard Python libraries that must be installed for Python 3 on your Raspberry Pi:

Beautiful Soup 4 (https://www.crummy.com/software/BeautifulSoup/) 

```
pip3 install beautifulsoup4
```
GPIO and gpiozero (should already be installed on Pi)

```
sudo apt-get python3-gpiozero
sudo pip3 install RPi.GPIO
```

Adafruit_Python_CharacterLCD (https://github.com/adafruit/Adafruit_Python_CharLCD)

```
cd ~
git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
cd Adafruit_Python_CharLCD
sudo python3 setup.py install
```

## Usage
Download or copy the StatTrakDriverRev0_2.py file into your home directory. Replace the URL string 'http://steamcommunity.com/id/e_van13/stats/L4D2' with the URL to your desired profile page.

To configure this script to run on Pi power-up, add it to the rc.local file for your user account on Raspbian:

```
sudo nano /etc/rc.local
```

After the comments, add a command to run the StatTrakDriverRev0_2.py script, and then save and exit:

```
python3 ~/StatTrakDriverRev0_2.py
```
Note: If you don't have buttons installed, make sure you some other way to exit the infinite while loop if you configure it to run at start-up. If you don't have a way to exit it, your Pi will be forever stuck in startup and you'll have to put your SD card in another Linux machine to go in and edit the rc.local file and comment out the command to run the StatTrak script.


