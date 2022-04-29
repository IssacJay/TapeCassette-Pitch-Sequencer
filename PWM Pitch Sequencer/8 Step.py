#8 Step Sequencer
import machine
from machine import Pin
from machine import ADC
from machine import UART
import time
import math
import _thread
import ustruct
from rotary import Rotary
from machine import Pin, I2C 
from ssd1306 import SSD1306_I2C 


#SET UP VARIABLES
#VOLUME 
vol = machine.PWM(machine.Pin(14)) #Volume PWM
vol.freq(1000) #Frequency of PWM

#PWM
motor = machine.PWM(machine.Pin(15)) #Motor Speed PWM
motor.freq(1000) #Frequency of PWM

#OLED
i2c=I2C(1,sda=Pin(6), scl=Pin(7), freq=400000) #Initiate paramers for the OLED-SSD1036 display
oled = SSD1306_I2C(128, 64, i2c) #Create instance of  OLED-SSD1036 display using the MicroPython OLED-SSD1036 module

#ROTARY ENCODER
rotary = Rotary(18,17,19) #DT (Direction), CK(Clock),SW(Switch)
switch = Pin(19, mode=Pin.IN, pull = Pin.PULL_UP) # Inbuilt switch on the rotary encoder
val = 60 #Starting value for the Pitch
freq = pow(2, ((val-69)/12)) * 440 #Convert from MIDI to frequency
rotStep = 1 #Each step of the rotary encoder +- 1

#MOTOR PWM SETTINGS 
K = 4427.6 #PWM Motor Power Law Constant 
a = 0.002 #PWM Motor Power Law Exponent 
line_offset = [] #how many characters in each line

#8 Step Settings
notes = [61,62,63,64,65,66,67,68] #8 Step MIDI Notes
gate = [1,1,0,1,1,0,1,1] #Volume Gate Values
noteline_offset = [] #Array used to determine start position of each line in 8 step text file
tempo = 120 #Current Tempo

# SCREEN SETTINGS
width = 128 #Full width of Screen
height = 64 #Full height of Screen
stepsel = 1 #Position of selected parameter
selected = False #Bool to see if a parameter has been selected 
endtask8 = False #Bool used to terminate the scipt


def read_settings(): #Read Constant and Power Values from Settings File
    global K, a #access power law settings variables
    with open('lib/settings.txt', 'r') as settings:
        offset = 0 #how many charcters in current line
        for line in settings: #for each line in file
            line_offset.append(offset) #append start length of line 
            offset += len(line) #Add character count of of current line to cumulative offset
        settings.seek(0) #rewind to position zero 

        settings.seek(line_offset[0]) #seek to selected line
        constant = settings.readline() #read the constant variable
        K = constant.strip() #Remove String components
        K = float(K) #Convert to float
        settings.seek(line_offset[1]) #seek to selected line
        power = settings.readline() #read the power variable
        a = power.strip() #Remove String Components
        a = float(a) #Convert to float
        current_settings = [constant, power] #Add settings into array
        print('Current Settings are: ' + str(current_settings)) #Print current settings
        settings.close() #Close the settings .txt file

        return(current_settings) #Return the settings array
    
def read_8step(): #Read Text File with Initial Values 
    global notes, noteline_offset, tempo, gate
    with open('lib/8 Step.txt', 'r') as sequencer:
        offset = 0 #how many charcters in current line
        for line in sequencer: #for each line in file
            noteline_offset.append(offset) #append start length of line 
            offset += len(line) #Add character count of of current line to cumulative offset
        sequencer.seek(0) #rewind to position zero
        
        oled.fill_rect(0,15,(14*8),30,1) #Create white filled box before initialising the paramter bars
        for i in range(0,8): #Loop through values of notes and gate (volume)
            sequencer.seek(noteline_offset[i]) #seek to selected line
            notes[i] = int(sequencer.readline()) #Add the saved midi notes in 8 Step.txt to notes array
            oled.fill_rect((i * 14),15,14,int((30-(notes[i]*0.33))),0) #Clear the selection section of the display #X Pos, Y Pos, Width of rect, Hight of Rect, Colour
            
            if gate[i] == 1: #If Volume value is on
                oled.fill_rect((i*14), 55, 14, 5, 1) #Fill Box beneath step
            elif gate[i] == 0: #If step volume is off
                oled.rect((i*14), 55, 14, 5, 1) #Create empty box
                
            oled.show()#shows the sequencer step
         
        
        sequencer.seek(noteline_offset[8]) #Seek to the tempo value in the text file
        tempo = int(sequencer.readline()) #Read the tempo
        oled.fill_rect(118,15,10,30,1) #Create white box for tempo paramter
        oled.fill_rect(118,15,10,int((30-(tempo*0.07))),0) #Change size of Tempo bar to match value of tempo
        print('Starting tempo is: ' + str(tempo))
            
        
    
def rotary_changed(change): #If rotary encoder detects a change
    global stepsel, K, a, selected, tempo, notes, endtask8
    if selected == False: #If a parameter has not been selected
        oled.fill_rect(90, 0, 38, 10, 0) #Clear section of screen used to display selected paramter value
        print(stepsel) 
        if change == Rotary.ROT_CW: #If rotation is clockwise
            if stepsel >= 0 and stepsel < 8: #If selection is a note parameter
                stepsel = stepsel + 1 #Move to next paramter
                oled.fill_rect(0,50,128,5,0) #Clear bottom selection row (area used for selection bar) 
                oled.fill_rect(0,12,128,2,0) #Clear top selection row of the display 
                oled.fill_rect((stepsel * 14),12,14,2,1) #Create bar indicating current selection (on top line)
                oled.show()#shows the sequencer step
            elif stepsel >= 8 and stepsel < 17: #If selection is a Gate checkbox paramter
                stepsel = stepsel + 1 #Move to next paramter
                oled.fill_rect(0,50,128,5,0) #Clear bottom selection row (area used for selection bar) 
                oled.fill_rect(0,12,128,2,0) #Clear top selection row of the display 
                oled.fill_rect(((stepsel - 9) * 14),50,14,2,1) #Create bar indicating current selection (on bottom line)
                oled.show()#shows the sequencer step
                
        elif change == Rotary.ROT_CCW: #If rotation is counter-clockwise
            if stepsel > 0 and stepsel <= 9: #If selection is note or tempo
                stepsel = stepsel - 1 #Move to the left
                oled.fill_rect(0,50,128,5,0) #Clear bottom selection row 
                oled.fill_rect(0,12,128,2,0) #Clear top selection row of the display 
                oled.fill_rect((stepsel * 14),12,14,2,1) #Clears display
                oled.show()#shows the sequencer step
            elif stepsel > 9: #If selection is gate or menu value
                stepsel = stepsel - 1 #Move to the left
                oled.fill_rect(0,50,128,5,0) #Clear bottom selection row 
                oled.fill_rect(0,12,128,2,0) #Clear top selection row of the display 
                oled.fill_rect(((stepsel - 9) * 14),50,14,2,1) #Clears display
                oled.show()#shows the sequencer step
                
        elif change == Rotary.SW_PRESS: #If rotary button is pressed
            if stepsel <= 8: #If selected paramter is a note value
                selected = True #Selection is True (allows paramter to be adjusted)
            elif stepsel > 8 and stepsel < 17: #If paramter is volume gate value
                i = stepsel - 9 #For index of gate array
                if gate[i] == 1: #If gate is currently on
                    gate[i] = 0 #Turn gate off
                    oled.fill_rect((i*14), 55, 14, 5, 0) #Fill Box beneath step
                    oled.rect((i*14), 55, 14, 5, 1) #Create empty box
                    oled.show()
                elif gate[i] == 0: #If gate is currently off
                    gate[i] = 1; #Turn on
                    oled.fill_rect((i*14), 55, 14, 5, 1) #Fill Box beneath step
                    oled.show()
            elif stepsel == 17: #If return to menu is selected
                endtask8 = True #End task = True
                print('Closing 8 Step')
                
        elif change == Rotary.SW_RELEASE: #If button is released
            print("Button Released") #No use case for button release
        
    elif selected == True: #If a note/tempo parameter has been selected to be changed
        if stepsel < 8: #Change selected note
            if change == Rotary.ROT_CW: #If roation is clockwise
                if notes[stepsel] < 88: #If current value is less than 88
                    notes[stepsel] = notes[stepsel] + 1 #Add 1
                elif notes[stepsel] == 88: #If value = 88
                    notes[stepsel] = 1 #Cycle to 1
            elif change == Rotary.ROT_CCW: #If roation is counter-clockwise
                if notes[stepsel] > 1: #And current value is greater than 1
                    notes[stepsel] = notes[stepsel] - 1 #Minus 1
                elif notes[stepsel] == 1: #If current value = 1
                    notes[stepsel] = 88 #New value = 88
            elif change == Rotary.SW_PRESS: #If button is pressed again, the value is saved and the rotary will return to selection mode
                selected = False #Paramter no longer selected
                
            oled.fill_rect((stepsel * 14),15,14,30,1) #Creates a white box over current selected value
            oled.fill_rect((stepsel * 14),15,14,int((30-(notes[stepsel]*0.33))),0) #Adjusts the slected value box to the right height
            oled.fill_rect(90, 0, 38, 10, 0) #The selected value text area is cleared
            oled.text(str(notes[stepsel]), 105, 0) #The value of the selected paramter is shown
            oled.show()#shows the sequencer step
            
        elif stepsel == 8: #Change Tempo  
            if change == Rotary.ROT_CW: #If rotation is clockwise
                if tempo < 300: #If current tempo is less than 300
                    tempo = tempo + 1 #Add 1 to tempo
                    oled.fill_rect(100,0,38,10,0) #Clear text
                    oled.text(str(tempo), 100, 0) #Add text of tempo value
                    oled.fill_rect(118,15,10,30,1) #Refill tempo box
                    oled.fill_rect(118,15,10,int((30-(tempo*0.07))),0) #Change size of Tempo line
            elif change == Rotary.ROT_CCW: #If rotation is anti-clockwise
                if tempo > 50: #If tempo is above 50
                    tempo = tempo - 1 #Take 1 from tempo
                    oled.fill_rect(100,0,38,10,0) #Clear text
                    oled.text(str(tempo), 100, 0) # Add text of tempo value
                    oled.fill_rect(118,15,10,30,1) #Refill tempo box
                    oled.fill_rect(118,15,10,int((30-(tempo*0.07))),0) #Change size of Tempo line
            elif change == Rotary.SW_PRESS: #Confirm change in paramter
                selected = False #Deselect paramter
                
            oled.show() #Refresh screen
        
        
def motor_Speed(): #Changing the PWM signal to the Motor 
    global val, K, a, tempo, notes, gate, endtask8 #Access global variables
    
    while True: #Loop
        if endtask8 == True: #If patch has been quit
            break #Break the while loop to stop execution 
        for i in range(0,8): #For loop between 0 and 8 
            oled.fill_rect(0,46,128,2,0) #Clear the bottom section of the display
            oled.fill_rect((i * 14),46,14,2,1) #step sequencer position bar
            oled.show()#shows the sequencer step

            note = notes[i] #Get current note value
            freq = pow(2, ((note-69)/12)) * 440 #Calculate the frequency from the midi note
            duty = K * math.exp(a * freq) #convert the frequency to the duty cycle using the power law equation (Set in Calibration)
            
        
            if gate[i] == 1: #If current gate value in array = 1
                 volduty = 65535 #Set duty cycle to 100%
            elif gate[i] == 0: #If current gate value in array = 0
                volduty = 0 #Set duty cycle to 0%
            
            #Send PWM
            motor.duty_u16(int(duty)) #set duty cycle for the motor circuit
            vol.duty_u16(volduty) #Set duty cycle for the volume gate
            timeinterval = (60/tempo) #calculate the time interval between each step
            time.sleep(timeinterval) #Sleep for the length of 1 step

#Initial set up functions
read_settings() #Read settings to get k and a
read_8step() #Read 8 step to get initial note and tmepo values


oled.text('8 STEP SEQ',1,1) #Display title
oled.text('<<', 114,55) #Display back to menu button
oled.show()

rotary.add_handler(rotary_changed) #Interupt function for rotary encoder

while True: 
    motor_Speed() #Call motor speed function
    
    if endtask8 == True: #If returned to menu selected
        print('Break') #Print break loop
        break #Break loop (finish execution)

   




