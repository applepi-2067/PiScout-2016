import cv2
import os
import numpy as np
from ast import literal_eval
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
from time import sleep
from tkinter import messagebox

class PiScout:
	# Firstly, initializes the fields of a PiScout object
	# Then it starts the main loop of PiScout
	# Requires a function "main" which contains the sheet configuration
	# Loops indefinitely and triggers a response whenever a new sheet is added
	def __init__(self, main):
		self.sheet = None;
		self.display = None;
		self.data = {}
		self.shift = 0

		# I have a vague feeling that putting the main loop in init is bad practice
		# But whatever
		f = set()
		while True:
			sleep(0.25)
			files = set(os.listdir()) #grabs all file names as a set
			added = files - f #check if any files were added (if first iteration, added = files)
			f = files #will hold onto this value for the next iteration
			for file in added:
				if ('.jpg' or 'png') in file:
					self.loadsheet(file)
					main(self) #call the main loop with this PiScout object as an argument


	# Loads a new scout sheet from an image
	# Processes the image and stores the result in self.sheet
	def loadsheet(self, imgpath):
		print('Loading a new sheet: ' + imgpath)
		img = cv2.imread(imgpath)
		imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		# The first step is to figure out the four markers on the corners of the page
		# The next two lines will blur the image and extract the edges from the shapes
		blur = cv2.GaussianBlur(imgray,(5,5),0)
		edges = cv2.Canny(blur,150,300)

		# Next, we use the edges to find the contours of the shapes
		# Once the contours are found, we use approxPolyDP to resolve the contours into polygon approximations
		# If the polygons have 4 sides and are relatively large, save the center coordinates in sq[]
		image, contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		sq = []
		for cont in contours:
				poly = cv2.approxPolyDP(np.array(cont), 3, True)
				if len(poly) == 4 and cv2.contourArea(cont) > 2048:
					xpos = 0; ypos = 0
					for a in poly:
						xpos += a[0][0]
						ypos += a[0][1]
					sq.append((int(xpos/4), int(ypos/4)))

		# Here, we determine which four elements of sq[] are the marks
		# To do this, we iterate through each corner of the sheet
		# On each iteration, we find the element of sq[] with the shortest distance to the corner being examined
		marks = []
		h, w, c  = img.shape
		corners = [(0, 0), (0, h), (w, 0), (w,h)]
		for corner in corners:
			marks.append(sq[np.argmin([(corner[0] - a[0])**2 + (corner[1] - a[1])**2 for a in sq])])

		# Now, we fit apply a perspective transform
		# The centers of the 4 marks become the 4 corners of the image
		pts1 = np.float32(marks)
		pts2 = np.float32([[0,0],[0,784],[560,0],[560,784]])
		M = cv2.getPerspectiveTransform(pts1,pts2)
		img = cv2.warpPerspective(img,M,(560,784))
		self.display = img.copy()
		self.sheet = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		print("Loading complete")

	# Shifts all fields down by amount
	# Useful for when there are two matches on one sheet of paper
	# After reading the first match, shift down and read again
	def shiftDown (self, amount):
		self.shift = amount

	# Gets the shading value of a grid unit
	# 0 is completely shaded, 102000 is completely unshaded
	def getvalue(self, loc):
		col,row = loc
		box = self.sheet[row*16:(row+1)*16, col*16:(col+1)*16]
		#box = [item[col*16:(col+1)*16] for item in self.sheet[row*16:(row+1)*16]]
		return sum(map(sum, box))

	# Parses a location in Letter-Number form and returns a tuple of the pixel coordinates
	def parse(self, loc):
		col,row = loc.upper().split('-')
		return (ord(col)-67 if len(col)==1 else ord(col[1])-41, self.shift + int(row)-3)

	# Define a new boolean field at a given location
	# Returns whether or not the grid unit is shaded
	def boolfield(self, location):
		loc = self.parse(location)
		cv2.rectangle(self.display, (loc[0]*16, loc[1]*16), (loc[0]*16+16, loc[1]*16+16), (0,50,150),3)
		return self.getvalue(loc) < 45000

	# Define a new range field at a given location
	# This field spans across multiple grid units
	# Returns the shaded value, or 0 if none is shaded
	def rangefield(self, startlocation, startval, endval):
		loc = self.parse(startlocation)
		end = loc[0]-startval+endval+1 #grid coordinate where the rangefield ends
		cv2.rectangle(self.display, (loc[0]*16, loc[1]*16), (end*16, loc[1]*16+16), (0,50,150),3)
		values = [self.getvalue((val, loc[1])) for val in range(loc[0], end)]
		min = np.argmin(values)
		if values[min] < 45000:
			return startval + min
		return 0

	# Adds a data entry into the data dictionary
	def set(self, name, contents):
		self.data[name] = contents

	# Opens the GUI, preparing the data for submission
	def submit(self):
		if self.data['team'] == 0:
			print("Found an empty match, skipping")
			return
		with open("history.txt", "a+") as file:
			d = str(self.data['team']) + ' ' + str(self.data['match'])
			file.seek(0)
			if d in file.read():
				print("Already processed this match, skipping")
				return
			file.write(d + '\n')

		print("Found a new match, opening")
		output = ''
		for key,val in self.data.items():
			output += "'" + key + "'" + ": " + str(val) + '\n'
		output = output.replace(', ', '\n    ')
		fig = plt.figure('PiScout')
		fig.subplots_adjust(left=0, right=0.6)
		ax = plt.subplot(111)
		plt.imshow(self.display)
		plt.title('Scanned Sheet')
		plt.text(600,784,output,fontsize=14)
		upload = Button(plt.axes([0.68, 0.31, 0.15, 0.07]), 'Upload Data')
		upload.on_clicked(self.upload)
		save = Button(plt.axes([0.68, 0.24, 0.15, 0.07]), 'Save Data Offline')
		save.on_clicked(self.save)
		edit = Button(plt.axes([0.68, 0.17, 0.15, 0.07]), 'Edit Data')
		edit.on_clicked(self.edit)
		cancel = Button(plt.axes([0.68, 0.1, 0.15, 0.07]), 'Cancel')
		cancel.on_clicked(self.cancel)
		mng = plt.get_current_fig_manager()
		mng.window.state('zoomed')
		plt.show()
		self.data = {}
		self.display = cv2.cvtColor(self.sheet, cv2.COLOR_GRAY2BGR)

	# Invoked by the "Save Data Offline" button
	# Adds data to a queue to be uploaded online at a later time
	# Eventually will also store the data locally in an elegant format
	def save(self, event):
		print("Queueing match for upload later")
		with open("queue.txt", "a") as file:
			file.write(str(self.data) + '\n')
		plt.close()
		#SAVE LOCAL VERSION

	# Invoked by the "Upload Data" button
	# Eventually, this will upload to an AWS server
	def upload(self, event):
		print("Attempting upload to server")
		plt.close()
		#UPLOAD

	# Invoked by the "Edit Data" button
	# Opens up the data in notepad, and lets the user make modifications
	# Afterward, it re-opens the GUI with the updated data
	def edit(self, event):
		datastr = ''
		for key,val in self.data.items():
			datastr += "'" + key + "'" + ": " + str(val) + "\n"
		with open('piscout.txt', "w") as file:
			file.write(datastr)
		os.system('piscout.txt')
		datastr = '{'
		with open('piscout.txt', 'r') as file:
			for line in file:
				datastr += line.replace('\n', ', ')
		datastr += "}"
		try:
			self.data = literal_eval(datastr)
		except:
			messagebox.showerror("Malformed Data", "You messed something up; the data couldn't be read. Try again.")
		plt.close()
		self.submit()

	# Invoked by the "Cancel" button
	# Closes the GUI and erases the entry from the history file
	def cancel(self, event):
		plt.close()
		with open('history.txt', 'w+') as file:
			lines = file.readlines()
			lines = lines[:-1]
			file.writelines(lines)