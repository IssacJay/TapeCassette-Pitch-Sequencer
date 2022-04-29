from machine import Pin, I2C
from os import listdir
from ssd1306 import SSD1306_I2C
from time import sleep

#REFERENCES
#Code modified from rotary_display.py script by Kevin McAleer
#Available at https://github.com/kevinmcaleer/rotarydisplay/blob/main/rotary_display.py
#Accessed 18/02/22

#OLED
i2c=I2C(1,sda=Pin(6), scl=Pin(7), freq=400000) #Initiate paramers for the OLED-SSD1036 display
oled = SSD1306_I2C(128, 64, i2c) #Create instance of  OLED-SSD1036 display using the MicroPython OLED-SSD1036 module

# SCREEN VARIABLES
width = 128
height = 64
line_offset = [] #Array for starting character index of each line

#SETTING
power = 0.002 #New constant value
oldpower = 0.002 #Old constant value

#ROTARY ENCODER
button_pin = Pin(19, Pin.IN, Pin.PULL_UP) #Button
direction_pin = Pin(17, Pin.IN, Pin.PULL_UP) #Direction
step_pin  = Pin(18, Pin.IN, Pin.PULL_UP) #Step 
previous_value = True 
button_down = False

#READ SETTINGS FILE
def read_power():
    global power, oldpower
    with open('lib/settings.txt', 'r') as settings: #Open settings file in read more
        offset = 0 #how many charcters in current line
        for line in settings: #for each line in file
            line_offset.append(offset) #append start length of line 
            offset += len(line) #Add character count of of current line to cumulative offset
        settings.seek(0) #rewind to position zero 

        settings.seek(line_offset[1]) #seek to selected line
        power = settings.readline() #read the constant variable
        power= power.strip()
        power = float(power) #COnvert to float
        oldpower = float(power)
        settings.close() #Close Settings file
        
        oled.fill(0) #Clear screen
        oled.text(str(power),1,1) #Display power value
        oled.text('Constant (k)', 1, 25, 1) #Display info text
        oled.text('Adjustment', 1, 35, 1) #Display info text
        oled.show() #Refresh display
    return(power) #Return power value

#REWRITE POWER IN TEXT FILE
def write_power():
    global power, oldpower
    replaced_content = ""
    with open('lib/settings.txt', 'r+') as settings: #Open settings in read and write mode
        for line in settings: #for each line in file
            line = line.strip()
            new_line = line.replace(str(oldpower), str(power)) #replacing the texts
            replaced_content = replaced_content + new_line + "\n" #concatenate the new string and add an end-line break
        settings.seek(0) #Rewind to start of file
        settings.write(replaced_content) #Replace old content with content
        print(replaced_content) #Print new file          
        settings.close() #Clsoe settings
        
#CALL INITIAL FUNCTION   
read_power() #read settings

# LOOP
while True:
    if previous_value != step_pin.value():
        if step_pin.value() == False:
            if direction_pin.value() == False: #If rotation is clockwise
                if power < 10.0:
                    power += 0.001 #Add 0.001 to power value
                    power = float("{0:.3f}".format(power)) #Convert to 3dp float
                    oled.fill_rect(0,0, 128,10,0) #Clear display
                    oled.text(str(power), 1,1) #Display power
                    oled.show() #Refresh display
            else: #If rotation is anti-clockwise
                if power > 0.000001: 
                    power -= 0.001 #Reduce power value by 0.001
                    power = float("{0:.3f}".format(power)) #Convert to 3dp. float
                    oled.fill_rect(0,0, 128,10,0) #Clear display
                    oled.text(str(power), 1, 1) #Display power
                    oled.show() #Refresh display

        previous_value = step_pin.value()   
        
    # Check for button pressed
    if button_pin.value() == False and not button_down: #if button pressed
        button_down = True 
        write_power() #Rewrite text file with new value
        sleep(0.5) #Sleep for 0.5 seconds
        break #Stop execution and return to menu

    # Decbounce button
    if button_pin.value() == True and button_down:
        button_down = False




