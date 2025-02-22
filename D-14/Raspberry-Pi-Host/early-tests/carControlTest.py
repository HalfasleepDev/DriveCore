#TODO: DISECT

import RPi.GPIO as IO
import time
import os, sys
import picam
import pygame
from pygame.locals import *

pygame.init() #no
screen = pygame.display.set_mode((240, 240)) #no
pygame.display.set_caption('Pi Car') #no

IO.setwarnings(False)
IO.setmode(IO.BCM)
IO.setup(19,IO.OUT)
IO.setup(26,IO.OUT)

print("w/s: acceleration")
print("a/d: steering")
print("UP/DOWN: tilt") #no
print("LEFT/RIGHT: pan") #no
print("esc: exit") #change

#hostname="google.com"
#response=os.system("ping -c 1 " + hostname)
p=picam.PiPan() #no
t=IO.PWM(19,100)
s=IO.PWM(26,100)
w=pygame.key.get_pressed()[pygame.K_w]
throttle=14
steer=14.5
pan=166  #no
tilt=122  #no
p.neutral_pan()  #no
p.neutral_tilt()  #no
t.start(throttle)
s.start(steer)
stop = False
count=0

while (True):
    count=count+1
	#if count == 50:
	#	response=os.system("ping -c 1 " + hostname)
	#	if response == 0:
	#		print 'is up'
	#	else:
	#		print 'I died'
	#		break

	#	count=0
    time.sleep(.02)
    if stop == True:
        break
    for event in pygame.event.get():
		#key pressed
        if event.type == pygame.KEYDOWN:
            if event.key == K_w:
                throttle=14.8
			
            elif event.key == K_s:
			    throttle=13.2
				
            elif event.key == K_a:
				steer=11
				
			elif event.key == K_d:
				steer=18
			elif event.key == K_UP: #no
				tilt=tilt-5
			elif event.key == K_DOWN: #no
				tilt=tilt+5
			elif event.key == K_LEFT: #no
				pan=pan+10
			elif event.key == K_RIGHT: #no
				pan=pan-10
			elif event.key == K_RETURN: #no
				p.neutral_pan() #no
				p.neutral_tilt() #no
				pan=166 #no
				tilt=122 #no
            elif event.key == K_ESCAPE:
                stop = True
			t.ChangeDutyCycle(throttle)
			s.ChangeDutyCycle(steer)
			p.do_tilt(tilt)  #no
			p.do_pan(pan)  #no
		#key released
        elif event.type == pygame.KEYUP:
			if((pygame.key.get_pressed()[pygame.K_w] != 0 and pygame.key.get_pressed()[pygame.K_a] != 0) or (pygame.key.get_pressed()[pygame.K_w] !=0 and pygame.key.get_pressed()[pygame.K_d] != 0)):
				throttle=throttle
				steer=steer				
			elif((pygame.key.get_pressed()[pygame.K_s] != 0 and pygame.key.get_pressed()[pygame.K_a] != 0) or (pygame.key.get_pressed()[pygame.K_s] !=0 and pygame.key.get_pressed()[pygame.K_d] != 0)):
				throttle=throttle
				steer=steer
			elif(pygame.key.get_pressed()[pygame.K_w] != 0):
				throttle=15.1
				steer=14.5
			elif(pygame.key.get_pressed()[pygame.K_s] != 0):
				throttle=13.2
				steer=14.5
			elif(pygame.key.get_pressed()[pygame.K_a] != 0):
				throttle=14
				steer=11
			elif(pygame.key.get_pressed()[pygame.K_d] != 0):
				throttle=14
				steer=18
			else:
				throttle=14
				steer=14.5
			t.ChangeDutyCycle(throttle)
			s.ChangeDutyCycle(steer)