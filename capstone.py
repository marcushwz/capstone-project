# importing all the libraries and functions

from lidar_lite import Lidar_Lite
import picamera
import datetime as dt
import time
from time import sleep
import os
import serial
import pigpio

# setting up LIDAR-Lite v3 and connecting bluetooth data from Sensoduino

ser = serial.Serial('/dev/ttyACM0',9600)
lidar = Lidar_Lite()
connected = lidar.connect(1)

# Creating a file to log all the data from the test run

file = open("/media/pi/WEIZHE/capstone101/16thRun.csv","a")

# setting all the initial condition

i = 0
distance1 = 0
distance2 = 0
safety_distance = 0
pi = pigpio.pi()

if connected < -1 :
	print ("Not Connected ")
else:
	print ("Connected")
	
# main body

with picamera.PiCamera() as camera:
	if os.stat("/media/pi/WEIZHE/capstone101/16thRun.csv").st_size == 0:
	
	# creating a csv file with six columns
	
		file.write("Time,Distance(m),Speed(km/h),Relative_Speed(km/h),Rear_Speed(km/h),Safe_Distance(m)\n")
		
	while True:
		now = dt.datetime.now()
		
		# reading the speed data from sensoduino and distance data from LIDAR-Lite v3
		
		read_serial = float(ser.readline())
		distance = float(lidar.getDistance())
		
		# Giving condition to data from LIDAR-Lite 
		
		if distance < 0:
			distance = 0
			
		# convert the distance into meter 
		
		distance_in_m = distance/100
		print("Distance to target = %s" % (distance))
		
		# Using the continous distance data to calculate the relative speed of rear vehicle using 1 second rule
		
		i += 1
		if i%2 == 0:
			distance2 = distance_in_m
		else:
			distance1 = distance_in_m
		if (distance2 == 0) or (distance1 == 0):
			relative_speed = 0
		else:
			relative_speed = abs(distance2 - distance1)*3.6
			
		# calculate the rear vehicle speed by adding speed of our vehicle with the relative speed
		
		rear_speed = read_serial + relative_speed
		
		# Converting the rear vehicle speed into m/s 
		
		rear_speed_in_mpersec = rear_speed / 3.6
		
		# Giving 2 conditions to safety distance and assuming the average length of vehicle is 4m
		
		if rear_speed == 0:
			safety_distance = 2
		else:
			safety_distance = rear_speed_in_mpersec - 4
		
		# Converting safety distance into cm
		
		safety_distance_in_cm = safety_distance*100
		
		# writing the data into the csv file created above
		
		file.write(str(now)+","+str(distance11)+","+str(read_serial)+","+str(relative_speed)+","+str(rear_speed)+","+str(safety_distance)+"\n")
		file.flush()
		
		# Triggering the camera's video recording function and LED when safety distance is surpassed
		
		if (int(distance) < safety_distance_in_cm) and (int(distance) > 0.01):
			pi.set_PWM_dutycycle(17,255)
			filename = "{0:%Y}-{0:%m}-{0:%d}-{0:%H}-{0:%M}-{0:%S}.h264".format(now)
			camera.annotate_background = picamera.Color('black')
			camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			camera.start_recording(filename)
			start = dt.datetime.now()
			while (dt.datetime.now() - start).seconds <10:
				camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				camera.wait_recording(0.2)
				camera.stop_recording()
		else:
			pi.set_PWM_dutycycle(17,0)
        file.close()
