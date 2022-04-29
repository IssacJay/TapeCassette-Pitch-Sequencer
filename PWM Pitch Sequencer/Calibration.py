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
oled = SSD1306_I2C(128, 64, i2c) #Create instance of  OLED-SSD1036 display using the MicroPython OLED-SSD1306 module

# SCREEN SETTINGS
width = 128 #Full width of Screen
height = 64 #Full height of Screen
line = 1 #Current Line
highlight = 1 #Highlight selected line
shift = 0 #Shift menu to reveal new set of lines
list_length = 0 #Length of settings list
total_lines = 2 #Total number of lines

#EXPONENTIAL EQUATION VARIABLES 
constant = 4428 #k value
power = 0.002 # a Value
mainmenu = 'Back to Menu' #String for back to menu
line_offset = [] #how many characters in each line


#ROTARY ENCODER
button_pin = Pin(19, Pin.IN, Pin.PULL_UP) #Button
direction_pin = Pin(17, Pin.IN, Pin.PULL_UP) #Direction
step_pin  = Pin(18, Pin.IN, Pin.PULL_UP) #Step 
previous_value = True 
button_down = False

#READ SETTINGS TEXT FILE
def read_settings():
    global constant, power, line_offset, mainmenu #access global settings variables
    with open('lib/settings.txt', 'r') as settings: #Open the settings text file as 'settings'
        offset = 0 #how many charcters in current line
        for line in settings: #for each line in file
            line_offset.append(offset) #append start length of line 
            offset += len(line) #Add character count of of current line to cumulative offset
        settings.seek(0) #rewind to position zero 

        settings.seek(line_offset[0]) #seek to selected line
        constant = settings.readline() #read the constant variable
        constant = constant.strip() #remove line elements
        settings.seek(line_offset[1]) #seek to selected line
        power = settings.readline() #read the power variable
        power = power.strip() #remove line elements
        
        current_settings = [constant, power] #add settings to array
        current_settings.append(mainmenu) #append 'back to menu' to array
        print('Current Settings are: ' + str(current_settings)) #Print current settings
        settings.close() #CLose text file
          
        return(current_settings) #Return the settings array 
 
#SHOWS MENU ON OLED
def show_calibmenu(calibrationmenu): 
    global line, highlight, shift, list_length  # Menu Variables
    item = 1 
    line = 1
    line_height = 10 

    oled.fill_rect(0,0,width,height,0) #Clears display

    # Shift the list of files so that it shows on the display
    list_length = len(calibrationmenu) #Length of settings list
    short_list = calibrationmenu[shift:shift+total_lines] #Trim to only view the number of total_lines

    for item in short_list: #For each item in the trimmed settings list
        if highlight == line: #Highlight the line
            oled.fill_rect(0,(line-1)*line_height, width,line_height,1) #Add box around text
            oled.text("*",0, (line-1)*line_height,0) #Add a star to selected line
            oled.text(item, 10, (line-1)*line_height,0) #Change text colour
            oled.show() #Refresh display
        else:
            oled.text(item, 10, (line-1)*line_height,1) #Normal text
            oled.show() #Refresh display
        line += 1
    #Static Text below the menu
    oled.text('Constant (k)', 1, 25, 1) 
    oled.text('Power (a)', 1, 35, 1)
    oled.text('PWM Settings', 1, 45, 1)
    oled.show() #refresh the display
    
#CHANGE SELECTED SETTING
def adjust_setting(variable): #String of selected variables is sent to function
    global constant, power,setting_list, previous_value, button_down 
    print('Variable = ' + str(variable)) #Print selected variable
    if variable == constant: #If sleection is 'constant'
        path = "/abstractions/constant.py" #Set path
    elif variable == power: #if selection is 'power'
        path = "/abstractions/power.py" #Set path
    elif variable == mainmenu: #If selection is mainmenu
        path = "/menu.py" #Set path
    print('Path = ' + path) #Print the path
    exec(open(path).read()) #Open the selected path script
    oled.fill(0) #Cleae the screen

#CALL INITIAL FUNCTIONS
setting_list = read_settings() #Read current settings
show_calibmenu(setting_list) #Show the menu on the display

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
                

            show_calibmenu(setting_list) #Refresh the menu
        previous_value = step_pin.value() #Previous value now equals current value
        
    
    if button_pin.value() == False and not button_down: #CHECK FOR BUTTON PRESS
        button_down = True #If button is pressed
        
        print("Launching", setting_list[highlight-1+shift]) #Print that patch is opening selected setting 
        selection = setting_list[highlight-1+shift] #Sleection is current selection
        sleep(1) #Wait 1 second
        print(setting_list) #Print current settings
        print(selection) #Print Current selection
        adjust_setting(selection) #Launch slected path
        break #Break the loop to stop execution
    # Decbounce function
    if button_pin.value() == True and button_down: #Stops button from being called more than once per selection
        button_down = False
