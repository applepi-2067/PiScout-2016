import cv2
import numpy as np
from matplotlib import pyplot as plt

imgcolor = cv2.imread('sheet.png')
img = cv2.cvtColor(imgcolor, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(img,(5,5),0)
edges = cv2.Canny(img,100,200)

ret,thresh = cv2.threshold(edges,127,255,0)
image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
sq = []
for cont in contours:
		poly = cv2.approxPolyDP(np.array(cont), 3, True)
		if len(poly) == 4 and cv2.contourArea(cont) > 2048:
			xpos = 0; ypos = 0
			for a in poly:
				xpos += a[0][0]
				ypos += a[0][1]
			sq.append((int(xpos/4), int(ypos/4)))

marks = []
h, w  = img.shape
corners = [(0, 0), (0, w), (h, 0), (h,w)]
for corner in corners:
	mark = sq[np.argmin(list(map(lambda a : (corner[0] - a[0])**2 + (corner[1] - a[1])**2, sq)))]
	imgcolor = cv2.circle(imgcolor, mark, 32, (0, 255, 0), -1)
	marks.append(mark)

'''mark1 = sq[np.argmin(list(map(lambda a : a[0]**2 + a[1]**2, sq)))]
dist2 = list(map(lambda a : a[0]**2 + a[1]**2, sq))
dist3 = list(map(lambda a : a[0]**2 + a[1]**2, sq))
dist4 = list(map(lambda a : a[0]**2 + a[1]**2, sq))'''

'''params = cv2.SimpleBlobDetector_Params()
params.minThreshold = 0
params.maxThreshold = 250
params.filterByCircularity = True
params.minCircularity = 0.7
params.maxCircularity = 0.83
detector = cv2.SimpleBlobDetector_create(params)
keypoints = detector.detect(img)
print(len(keypoints))
im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.namedWindow("Keypoints", cv2.WINDOW_NORMAL)
cv2.imshow("Keypoints", im_with_keypoints)
cv2.waitKey(0)'''


cv2.namedWindow("Scanned Sheet", cv2.WINDOW_KEEPRATIO)
cv2.imshow('Scanned Sheet', imgcolor)
cv2.waitKey(0) #wait for keystroke (no timeout)
cv2.destroyAllWindows()
