# MAIN MENU
from machine import Pin, I2C
from os import listdir
from ssd1306 import SSD1306_I2C
from time import sleep
from rotary import Rotary

#REFERENCES
#Code modified from rotary_display.py script by Kevin McAleer
#Available at https://github.com/kevinmcaleer/rotarydisplay/blob/main/rotary_display.py
#Accessed 18/02/22

#OLED
i2c=I2C(1,sda=Pin(6), scl=Pin(7), freq=400000) #Initiate paramers for the OLED-SSD1036 display
oled = SSD1306_I2C(128, 64, i2c) #Create instance of  OLED-SSD1036 display using the MicroPython OLED-SSD1306 module#OLED

# SCREEN SETTINGS
width = 128 #Full width of Screen
height = 64 #Full height of Screen
line = 1 #Current Line
highlight = 1 #Highlight selected line
shift = 0 #Shift menu to reveal new set of lines
list_length = 0 #Length of settings list
total_lines = 2 #Total number of lines# SCREEN SETTINGS

#ROTARY ENCODER
button_pin = Pin(19, Pin.IN, Pin.PULL_UP) #Button
direction_pin = Pin(17, Pin.IN, Pin.PULL_UP) #Direction
step_pin  = Pin(18, Pin.IN, Pin.PULL_UP) #Step 
previous_value = True 
button_down = False#ROTARY ENCODER

#ACCESS FILES DIRECTORY
def get_files(): 

    # files = listdir() #Get current list of files  #NOT USED BECAUSE MENU IS FIXED WITH THREE FILES LISTED BELOW
    menu = ["Calibration.py", "Pitch Mod.py", "8 Step.py"] #The three used files. 

    return(menu) #Return file names as list

#SHOW THE MENU
def show_menu(menu):
    global line, highlight, shift, list_length #Global variables
    # Menu Variables
    item = 1
    line = 1
    line_height = 10
    
    oled.fill_rect(0,0,width,height,0) #Clear display

    # Shift the list of files so that it shows on the display
    list_length = len(menu) #Length of menu list
    short_list = menu[shift:shift+total_lines] #Trim to only view the number of total_lines
    
    for item in short_list: #For each item in the trimmed menu list
        if highlight == line: #If item is selected
            oled.text("*",0, (line-1)*line_height,1) #Add star to selection
            oled.text(item, 10, (line-1)*line_height,1) #Write selection text
            oled.show() # Refresh display
        else:
            oled.text(item, 10, (line-1)*line_height,1) #Normal text
            oled.show() #refresh display
        line += 1 
    oled.text('Main Menu', 0, 50) #Add main menu text to bottom of display  
    oled.show() #Refresh display

#OPEN SELCTED FILE
def launch(filename): #Pass through file name
    global file_list
    oled.fill_rect(0,0,width,64,0) # clear the screen
    oled.text("Opening", 1, 10) #Adds opening text
    oled.text(filename,1, 20) #With name of opening file
    oled.show() #Shows the text
    sleep(1.5) #Sleeps for 1.5 seconds
    exec(open(filename).read()) #Opens the new file
    oled.fill(0) #Clears display when opened file is closed
    show_menu(file_list) #Reshow menu
    print(file_list) #Print list of files


oled.fill(0) #Clear display
file_list = get_files() # Get the list of Python files 
show_menu(file_list) #Displays the menu

#LOOP
while True:
    if previous_value != step_pin.value(): #If previous rotary encoder value does not equal the last value (debouncing)
        if step_pin.value() == False:
            if direction_pin.value() == False: #Turned Clockwise
                if highlight < total_lines: #If highlighted selection is less than the total displayed lines
                    highlight += 1 #Highlight nect line
                else: 
                    if shift+total_lines < list_length: #If shift is less than total number of lines
                        shift += 1 #Shift the menu down
            else: #Turned Anti-clockwise
                if highlight > 1: #If hightlighted line is greater than first line
                    highlight -= 1  #Highlight previous line
                else:
                    if shift > 0: 
                        shift -= 1 #Shift menu up

            show_menu(file_list) #Show menu function
        previous_value = step_pin.value() #Previous value now equals current value   
        
    if button_pin.value() == False and not button_down: #CHECK FOR BUTTON PRESS
        button_down = True #If button is pressed
        
        print("Launching", file_list[highlight-1+shift]) #Print name of launched file
        launch(file_list[(highlight-1) + shift]) #Launch selected file
        

    # Decbounce button
    if button_pin.value() == True and button_down:
        button_down = False