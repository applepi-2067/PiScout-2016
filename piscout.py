import cv2
import numpy as np
from matplotlib import pyplot as plt

class PiScout:
	def __init__(self):
		self.sheet = None;
		self.output = ''

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
			marks.append(sq[np.argmin(list(map(lambda a : (corner[0] - a[0])**2 + (corner[1] - a[1])**2, sq)))])

		# Now, we fit apply a perspective transform
		# The centers of the 4 marks become the 4 corners of the image
		pts1 = np.float32(marks)
		pts2 = np.float32([[0,0],[0,700],[500,0],[500,700]])
		M = cv2.getPerspectiveTransform(pts1,pts2)
		img = cv2.warpPerspective(img,M,(500,700))

		# Apply a binary threshold
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		ret, self.sheet = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)


	def viewsheet(self):
		cv2.imshow("Loaded Sheet", self.sheet)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def getvalue(self, loc):
		col,row = loc
		box = [item[col*20+10:col*20+30] for item in self.sheet[row*20+10:row*20+30]]
		return sum(map(sum, box))

	def parse(self, loc):
		col = loc[0]
		row = loc[1:]
		return (ord(col)-67, int(row)-3)

	def boolfield(self, location):
		loc = self.parse(location)
		return self.getvalue(loc) < 25000

	def rangefield(self, startlocation, startval, endval):
		loc = self.parse(startlocation)
		values = [self.getvalue((val, loc[1])) for val in range(loc[0], loc[0]+endval-startval+1)]
		min = np.argmin(values)
		if values[min] < 30000:
			return startval + min
		return 0

	def getsheet(self):
		return self.sheet

	def disp(self, text):
		self.output += str(text) + '\n'

	def finish(self):
		img = cv2.cvtColor(self.sheet, cv2.COLOR_GRAY2BGR)
		fig = plt.figure('PiScout')
		fig.subplots_adjust(left=0, right=0.6)
		plt.subplot(111)
		plt.imshow(img)
		plt.title('Scanned Sheet')
		plt.text(540,700,self.output,fontsize=14)
		plt.show()