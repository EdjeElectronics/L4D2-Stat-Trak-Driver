# Author: Evan Juras
# Date: 2/7/17
# Description: Python script to control Left 4 Dead 2 Stat Tracker.

#!/usr/bin/python
import urllib.request
from time import sleep
import gpiozero
from bs4 import BeautifulSoup
import Adafruit_CharLCD as LCD

# Define function to retrieve stats from Steam profile page
def Get_stats(Stats):
    "Load profile stats page and retrieve stats."
    
    # Load Steam profile L4D2 stats page
    website = urllib.request.urlopen('http://steamcommunity.com/id/e_van13/stats/L4D2') # Replace with URL to desired user page
    htmlText = website.read()
    soup = BeautifulSoup(htmlText, "html.parser")

    # Parse out 'Infected Killed' stat
    k = soup.find_all('div', class_='blueBoxThird')
    killed = k[2].get_text()
    Stats.str_killed = killed[15:]
    Stats.num_killed = int(Stats.str_killed.replace(',',''))

    # Parse out 'Games played' stat
    temp = k[0].get_text()
    games = temp[13:]
    Stats.str_games = games.replace('\t','')
    Stats.num_games = int(Stats.str_games)

    # Parse out 'Finales survived' stat
    temp = k[1].get_text()
    finales = temp[16:19]    #This will only work if finales survived is 1, 2, or 3 digits
    Stats.str_finales = finales.replace('(','')
    Stats.str_finales = Stats.str_finales.replace(' ','')
    Stats.num_finales = int(Stats.str_finales)

    # Parse out 'Average kills per hour' stat
    k = soup.find_all('div', class_='greyBox')
    temp = k[0].get_text()
    kph = temp[41:]
    Stats.str_kph = kph.replace('\t','')
    Stats.num_kph = float(Stats.str_kph)

    # Parse out 'Most Used Level 2 Weapon' stat
    # Well, I want to do this eventually, but it will require special manipulation of the
    # string to just get the weapon title and not the (XX# of kills) text. Also, 'military
    # sniper rifle' won't fit on LCD, have to make a special case for that.
    
    return

# Define function to print stats to LCD
def Print_stats(lcd, message):
    "Print stats to LCD."

    lcd.clear()
    lcd.message(message)

    return

#Define MyStats class to act as a data structure to hold all stats

class MyStats():
    """Data structure to hold all stats. I store some stats as a number and
as a string, so I don't have to convert to string when displaying to LCD. I could just use
strings but I want to have the numbers available just in case."""
    
    def __init__(self):
        "Initialize variables in data structure"
        self.num_killed = 0              #Infected killed
        self.str_killed = 'filler'       #Infected killed (string)
        self.num_kph = 0                 #Average kills per hour
        self.str_kph = 'filler'          #Average kills per hour (string)
        self.num_games = 0               #Total games played
        self.str_games = 'filler'        #Total games played (string)
        self.num_finales = 0             #Finales survived
        self.str_finales = 'filler'      #Finales survived (string)
        #self.str_fav_weap = 'filler'    #Favorite Level 2 weapon (string)
        #self.num_weap_kills = 0         #Kills with favorite weapon


# Now start the actual program. First, initialize the LCD display and instantiate the
# MysStats structure. Also assign top and bottom buttons.

# Raspberry Pi configuration. Values correspond to Pi's GPIO pins.
lcd_rs = 16
lcd_en = 12
lcd_d4 = 6
lcd_d5 = 5
lcd_d6 = 25
lcd_d7 = 24
lcd_red   = 23
lcd_green = 22
lcd_blue  = 27

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

# The Adafruit lcd code doesn't drive R/W low, so I have to do it manually.
# In my config, GPIO 13 is tied to the RCD R/W pin. I use the LED function
# from the gpiozero library to turn GPIO 13 into an "LED output" and turn
# it off, which holds the output low.
lcd_rw = gpiozero.LED(13)
lcd_rw.off()

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                              lcd_columns, lcd_rows, lcd_red, lcd_green, lcd_blue)

# Set red background color.
lcd.set_color(1.0, 0.0, 0.0)
lcd.clear()
lcd.message('Grabbing stats')

# Initialize data structure that holds the stats.
Stats = MyStats()

top_button = gpiozero.Button(17)
bot_button = gpiozero.Button(4)

sleep(2) # Sleep for 2 seconds: this is needed to give the
         # WiFi connection time to fully establish itself

# Do initial function call to grab stats from Steam profile page.
Get_stats(Stats)

# Now enter loop to retrieve website stats and update LCD every minute
# while polling for button presses.


ii = 1  # Variable that tells script which stat to display

debounce = 0 # Variable to control button "debounce"

end = 0 # While end == 0, the script will loop forever. end is set to 1
        # when the top and buttons are pressed simultaneously, and that
        # ends the program
        
refresh_count = 0 # Counter to automatically refresh stats. Counts up once
                  # per hour, and resets to 0 when 24 hours have passed
                  # (and causes Grab_stats function to be called)

# Begin infinite loop
while end == 0:

# First, print stats to the LCD.
# ii is used in this if-else statement to controls which stat is
# displayed on the LCD (via the 'message' variable)
    if ii == 1 :
        message = 'Taxi-guy\'s \nL4D2 stats' #Replace 'Taxi-guy' with your username

    elif ii == 2 :
        message = 'Infected killed:\n' + Stats.str_killed

    elif ii == 3 :
        message = 'Average kills \nper hour: ' + Stats.str_kph

    elif ii == 4 :
        message = 'Games played:\n' + Stats.str_games

    elif ii == 5 :
        message = 'Finales \nsurvived: ' + Stats.str_finales

    else :
        message = 'You done goofed' # The if-else statement should never enter
                                    # this branch

    Print_stats(lcd,message) # Prints message to the LCD


# Refresh stats once every 24 hours. refresh_count is incremented once a minute,
# and when it reaches 1440 (i.e. 24 hours), the Get_stats function is called
# to refresh the stats, and refresh_count is reset back to 0.
    refresh_count = refresh_count + 1

    if refresh_count >= 1440 :
        Get_stats(Stats)
        refresh_count = 0

# The following while loop waits one minute before incrementing ii to
# cycle the display to next stat. It also polls for button presses every
# 0.1 seconds.

    k = 0    # k holds the program in a while loop until a minute has passed
    b = 0    # b will override k if a button is pressed

# k starts at 0 and is incremented once every 0.1 seconds. When k reaches
# 600 (i.e. 60 seconds), ii is incremented so the next stat is displayed.
    while (k < 600) and (b == 0):
        sleep(0.1)
        k = k + 1

        if top_button.is_pressed and bot_button.is_pressed :
            # End program if both buttons are pressed. This allows the Pi
            # to not be stuck forever in startup mode if I want to use it
            # for something besides the Stat Tracker.
            end = 1
            break

        
        if top_button.is_pressed :
            # If the top button is pressed, call the Get_stats function to
            # refresh the stats, and reset the 24-hour refresh counter to 0.
            Get_stats(Stats)

            ii = 2 # Reset displayed message to 'Infected killed: ###'
            
            refresh_count = 0 # Reset automatic 24-hour refresh counter to zero,
                              # since we just refreshed
                              
            b = 1 # Setting b to 1 overrides the one-minute counter k and
                  # breaks out of the while loop, so the LCD is immediately
                  # updated with the refreshed stat.


        if bot_button.is_pressed and debounce == 0 :
            # If the bottom betton is pressed, increment ii and set b = 1
            # so the one-minute while loop is exited and the LCD display is
            # cycled to the next stat. Also set debounce = 1.
            ii = ii + 1
            if ii >= 6 :
                ii = 1
            b = 1
            debounce = 1

        # The following if statement is used to make it so the bottom button
        # has to be released before the previous if statement can be entered
        # again. In other words, the stat displayed on the LCD will only be
        # cycled once per button press. This "debounce" feature is used to
        # prevent the display from cycling through two or more stats on a
        # single button press.
        if (bot_button.is_pressed == 0) and debounce == 1 :
            debounce = 0
        
            
    #End of 1 minute sleep / button poll loop
            
    if b == 0 : # If no buttons were pressed during the one-minute while loop,
                # automatically increment ii before returning to the top of
                # the infinite while loop
        ii = ii + 1
        if ii >= 6 :
            ii = 1

#End of infinite while loop

