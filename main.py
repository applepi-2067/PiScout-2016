import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('sheet.png')
imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# The first step is to figure out the four markers on the corners of the page
# The next two lines will blur the image and extract the edges from the shapes
blur = cv2.GaussianBlur(imgray,(5,5),0)
edges = cv2.Canny(imgray,100,200)

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
dst = cv2.warpPerspective(img,M,(500,700))
#plt.subplot(121),plt.imshow(img),plt.title('Input')
#plt.subplot(122),plt.imshow(dst),plt.title('Output')
#plt.show()

# Apply a binary threshold
img = dst
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)

# Detect filled boxes
# This iterates through each grid location and picks the ones that are most dark
data = [[None]*25]*35
for row in range(34):
	for col in range(24):
		# I have no idea how the next line works, but it sums the pixels in the grid unit
		a = [item[col*20+10:col*20+30] for item in img[row*20+10:row*20+30]]
		if sum(map(sum, a)) < 25000:
			img = cv2.circle(img, (col*20+20, row*20+20), 4, 127, -1)

cv2.imshow("Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()