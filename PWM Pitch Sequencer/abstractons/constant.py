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
constant = 4428 #New constant value
oldconstant = 4428 #Old constant value

#ROTARY ENCODER
button_pin = Pin(19, Pin.IN, Pin.PULL_UP) #Button
direction_pin = Pin(17, Pin.IN, Pin.PULL_UP) #Direction
step_pin  = Pin(18, Pin.IN, Pin.PULL_UP) #Step 
previous_value = True 
button_down = False

#READ SETTINGS FILE
def read_constant():
    global constant, oldconstant
    with open('lib/settings.txt', 'r') as settings: #Open settings text file
        offset = 0 #how many charcters in current line
        for line in settings: #for each line in file
            line_offset.append(offset) #append start length of line 
            offset += len(line) #Add character count of of current line to cumulative offset
        settings.seek(0) #rewind to position zero 

        settings.seek(line_offset[0]) #seek to selected line
        constant = settings.readline() #read the constant variable
        constant = constant.strip()
        constant = int(constant) #Convert constant value to Int
        oldconstant = int(constant) #Update old constant
        settings.close() #Close text file
        
        oled.fill(0) #Clear screen
        oled.text(str(constant),1,1) #Display value
        oled.text('Constant (k)', 1, 25, 1) #add info text at bottom of display
        oled.text('Adjustment', 1, 35, 1) #Add text at bottom of display
        oled.show() #Refresh Display
    return(constant) #return constant value

#REWRITE TEXT FILE
def write_constant():
    global constant, oldconstant
    replaced_content = "" 
    with open('lib/settings.txt', 'r+') as settings: #Open settings in read and write mode
        for line in settings: #for each line in file
            line = line.strip()
            new_line = line.replace(str(oldconstant), str(constant)) #replacing the old constant with the new constant
            replaced_content = replaced_content + new_line + "\n" #concatenate the new string and add an end-line break
        settings.seek(0) #Seek to start 
        settings.write(replaced_content) #Rewrite the text file with new values
        print(replaced_content) #Print new text file       
        settings.close() #Close text file
        
            

#CALL INITIAL FUCTIONS    
read_constant() #Read settings 

# LOOP
while True:
    if previous_value != step_pin.value():
        if step_pin.value() == False: 
            if direction_pin.value() == False: #If Turned Clockwise
                if constant < 10000: #If constant < 10000
                    constant += 1 #Add 1 to constant
                    oled.fill_rect(0,0, 128,10,0) #Clear display
                    oled.text(str(constant), 1,1) #Display constant
                    oled.show() #Refresh display
            else: #If turned Anti-clockwise
                if constant > 1: #If constant > 1
                    constant -= 1 #Reduce constant by 1
                    oled.fill_rect(0,0, 128,10,0) #Clear display
                    oled.text(str(constant), 1, 1) #Display constant
                    oled.show() #Refresh display

        previous_value = step_pin.value() #Set current reotary encoder value to previous value
        
    # Check for button pressed
    if button_pin.value() == False and not button_down:
        button_down = True #If button is pressed
        write_constant() #Call write constant function
        sleep(0.5) #Sleep for 0.5 seconds
        break #End execution and return to menu

    # Decbounce button
    if button_pin.value() == True and button_down:
        button_down = False



