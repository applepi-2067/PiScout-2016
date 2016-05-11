import cv2
import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
from time import sleep
import ctypes
import requests
import server
from threading import Thread

# PiScout is a means of collecting match data in a scantron-like format
# This program was designed to be easily configurable, and new sheets can be made rapidly
# The configuration for the sheets is done in a separate file (main.py)
# Cory Lynch 2015
class PiScout:
	# Firstly, initializes the fields of a PiScout object
	# Then it starts the main loop of PiScout
	# Requires a function "main" which contains the sheet configuration
	# Loops indefinitely and triggers a response whenever a new sheet is added
	def __init__(self, main):
		print('PiScout Starting')
		self.sheet = None;
		self.display = None;
		self.data = []
		self.labels = []
		self.shift = 0

		Thread(target=server.start).start() # local database server
		f = set(os.listdir("Sheets"))
		while True:
			sleep(0.25)
			files = set(os.listdir("Sheets")) #grabs all file names as a set
			added = files - f #check if any files were added (if first iteration, added = files)
			f = files #will hold onto this value for the next iteration
			for file in added:
				if '.jpg' in file or '.png' in file:
					self.loadsheet("Sheets/" + file)
					main(self) #call the main loop with this PiScout object as an argument


	# Loads a new scout sheet from an image
	# Processes the image and stores the result in self.sheet
	def loadsheet(self, imgpath, b=3, guess=False):
		self.data = []
		self.labels = []
		print('Loading a new sheet: ' + imgpath)
		img = cv2.imread(imgpath)
		#img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
		imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		# The first step is to figure out the four markers on the corners of the page
		# The next two lines will blur the image and extract the edges from the shapes
		blur = cv2.GaussianBlur(imgray,(b,b),0)
		edges = cv2.Canny(blur,150,300)

		# Next, we use the edges to find the contours of the shapes
		# Once the contours are found, we use approxPolyDP to resolve the contours into polygon approximations
		# If the polygons have 4 sides and are relatively large, save the center coordinates in sq[]
		image, contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

		sq = []
		sqsize = []
		for cont in contours:
				poly = cv2.approxPolyDP(np.array(cont), 64, True)
				if len(poly) == 4 and cv2.contourArea(cont) > 8192:
					xpos = 0; ypos = 0
					for a in poly:
						xpos += a[0][0]
						ypos += a[0][1]
					sq.append((int(xpos/4), int(ypos/4)))
					sqsize.append(cv2.contourArea(cont))

		# Here, we determine which four elements of sq[] are the marks
		# To do this, we iterate through each corner of the sheet
		# On each iteration, we find the element of sq[] with the shortest distance to the corner being examined
		marks = []
		marksize = []
		h, w, c  = img.shape
		corners = [(0, 0), (0, h), (w, 0), (w,h)]
		for corner in corners:
			try:
				ind = np.argmin([(corner[0] - a[0])**2 + (corner[1] - a[1])**2 for a in sq])
			except:
				print("No markers found. Is this an empty image?")
			marks.append(sq[ind])
			marksize.append(sqsize[ind])

		u_marksize = marksize[:] #clone the list
		marksize.sort()
		median = (marksize[1] + marksize[2]) / 2

		#this block contains illegal inefficient recursive nonsense to salvage crappy sheets
		for i,m in enumerate(u_marksize):
			if abs(1 - m/median) > 0.04: #if there is a size anomoly in markers, try some things
				print("Damaged marker detected, attempting fix")
				if b < 13 and b != 1 and not guess:
					print("Increasing gaussian blur to " + str(b+2))
					self.loadsheet(imgpath, b=b+2)
					return
				if b != 1 and not guess:
					print("Trying a really small blur")
					self.loadsheet(imgpath, b=1)
					return
				if not guess:
					print("Attempting to guess the location of the last one")
					self.loadsheet(imgpath, b=3, guess=True)
					return
				if i == 0: #geometry to calculate approximate position of damaged marker
					marks[0] = (marks[1][0] - (marks[3][0]-marks[2][0]), marks[2][1] + (marks[1][1]-marks[3][1]))
				elif i == 1:
					marks[1] = (marks[0][0] + (marks[3][0]-marks[2][0]), marks[3][1] + (marks[0][1]-marks[2][1]))
				elif i == 2:
					marks[2] = (marks[3][0] - (marks[1][0]-marks[0][0]), marks[0][1] - (marks[1][1]-marks[3][1]))
				elif i == 3:
					marks[3] = (marks[2][0] + (marks[1][0]-marks[0][0]), marks[1][1] - (marks[0][1]-marks[2][1]))


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
	# Useful for when there are two (or more) matches on one sheet of paper
	# After reading the first match, shift down and read again
	def shiftDown (self, amount):
		self.shift = amount

	# Gets the shading value of a grid unit
	# 0 is completely shaded, 102000 is completely unshaded
	def getvalue(self, loc):
		col,row = loc
		box = self.sheet[row*16:(row+1)*16, col*16:(col+1)*16]
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
		return int(self.getvalue(loc) < 45000)

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

	# Define a new count field at a given location
	# This field spans across multiple grid units
	# Returns the highest shaded value, or 0 if none are shaded
	def countfield(self, startlocation, endlocation):
		loc = self.parse(startlocation)
		end = self.parse(endlocation)[0] + 1
		cv2.rectangle(self.display, (loc[0]*16, loc[1]*16), (end*16, loc[1]*16+16), (0,50,150),3)
		values = [self.getvalue((val, loc[1])) for val in range(loc[0], end)]
		for el,box in enumerate(values[::-1]):
			if box < 45000:
				return len(values) - el
		return 0

	# Adds a data entry into the data dictionary
	def set(self, name, contents):
		self.data.append(contents)
		self.labels.append(name)

	# Opens the GUI, preparing the data for submission
	def submit(self):
		if self.data[0] == 0:
			print("Found an empty match, skipping")
			self.data = []
			self.labels = []
			return
		with open("history.txt", "a+") as file:
			d = str(self.data[0]) + ' ' + str(self.data[1]) + '\n'
			file.seek(0)
			if d in file.read():
				print("Already processed this match, skipping")
				self.data = []
				self.labels = []
				return
			file.write(d)

		#the following block opens the GUI for piscout, this code shouldn't need to change
		print("Found a new match, opening")
		output = ''
		assert len(self.labels) == len(self.data)
		for a in range(len(self.data)):
			output += self.labels[a] + "=" + str(self.data[a]) + '\n'
		fig = plt.figure('PiScout')
		fig.subplots_adjust(left=0, right=0.6)
		plt.subplot(111)
		plt.imshow(self.display)
		plt.title('Scanned Sheet')
		plt.text(600,784,output,fontsize=12)
		upload = Button(plt.axes([0.68, 0.31, 0.15, 0.07]), 'Upload Data')
		upload.on_clicked(self.upload)
		save = Button(plt.axes([0.68, 0.24, 0.15, 0.07]), 'Save Data Offline')
		save.on_clicked(self.save)
		edit = Button(plt.axes([0.68, 0.17, 0.15, 0.07]), 'Edit Data')
		edit.on_clicked(self.edit)
		cancel = Button(plt.axes([0.68, 0.1, 0.15, 0.07]), 'Cancel')
		cancel.on_clicked(self.cancel)
		mng = plt.get_current_fig_manager()
		try:
			mng.window.state('zoomed')
		except AttributeError:
			print("Window resizing exploded, oh well.")
		plt.show()
		self.data = []
		self.labels = []
		self.display = cv2.cvtColor(self.sheet, cv2.COLOR_GRAY2BGR)

	# Invoked by the "Save Data Offline" button
	# Adds data to a queue to be uploaded online at a later time
	# Also stores in the local database
	def save(self, event):
		print("Queueing match for upload later")
		with open("queue.txt", "a+") as file:
			file.write(str(self.data) + '\n')
		plt.close()
		requests.post("http://127.0.0.1:8000/submit", data={'data': str(self.data)})

	# Invoked by the "Upload Data" button
	# Uploads all data (including queue) to the online database
	# Uploads a copy to the local database as backup
	def upload(self, event):
		plt.close()
		print("Attempting upload to server")

		try: #post it to piscout's ip address
			requests.post("http://52.2.17.191/submit", data={'data': str(self.data)})
			print("Uploading this match was successful")
			if os.path.isfile('queue.txt'):
				with open("queue.txt", "r") as file:
					for line in file:
						requests.post("http://52.2.17.191/submit", data={'data': line})
						print("Uploaded an entry from the queue")
				os.remove('queue.txt')
			requests.post("http://127.0.0.1:8000/submit", data={'data': str(self.data)})
		except:
			print("Failed miserably")
			r = self.message("Upload Failed", 'Upload failed. Retry? Otherwise, data will be stored in the queue for upload later.', type=5)
			if r == 4:
				self.upload(event)
			else:
				self.save(event)

	# Invoked by the "Edit Data" button
	# Opens up the data in notepad, and lets the user make modifications
	# Afterward, it re-opens the GUI with the updated data
	def edit(self, event):
		with open('history.txt', 'r') as file:
			lines = file.readlines()
			lines = lines[:-1]
		with open('history.txt', 'w+') as file:
			file.writelines(lines)
		datastr = ''
		for a in range(len(self.data)):
			datastr += self.labels[a] + "=" + str(self.data[a]) + '\n'
		with open('piscout.txt', "w") as file:
			file.write(datastr)
		os.system('piscout.txt')
		try:
			d = []
			with open('piscout.txt', 'r') as file:
				for line in file:
					d.append(int(line.split('=')[1].replace('\n', '')))
			self.data = d
		except:
			self.message("Malformed Data", "You messed something up; the data couldn't be read. Try again.")
		plt.close()
		self.submit()

	# Invoked by the "Cancel" button
	# Closes the GUI and erases the entry from the history file
	def cancel(self, event):
		plt.close()
		with open('history.txt', 'r') as file:
			lines = file.readlines()
			lines = lines[:-1]
		with open('history.txt', 'w+') as file:
			file.writelines(lines)

	# Displays a message box
	def message(self, title, message, type=0):
		return ctypes.windll.user32.MessageBoxW(0, message, title, type)
