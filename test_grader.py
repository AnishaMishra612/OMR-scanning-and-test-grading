#from transform import order_points , four_point_transform
from imutils.perspective import four_point_transform
from imutils import contours
#from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
	help = "Path to the image to be scanned")
args = vars(ap.parse_args())
# define the answer key which maps the question number
# to the correct answer
ANSWER_KEY = {0: 1, 1: 4, 2: 0, 3: 3, 4: 1}
image = cv2.imread(args["image"])
orig=image.copy()
#
# convert the image to grayscale, blur it, and find edges
# in the image
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)
# show the original image and the edge detected image
print("STEP 1: Edge Detection")
cv2.imshow("Image", image)
cv2.imshow("Edged", edged)
cv2.waitKey(0)
cv2.destroyAllWindows()
cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
# ensure that at least one contour was found
if len(cnts) > 0:
	# sort the contours according to their size in
	# descending order
	cnts = sorted(cnts, key=cv2.contourArea, reverse=True)


                 # loop over the sorted contours
	for c in cnts:
	# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	# if our approximated contour has four points, then we
	# can assume that we have found our paper
		if len(approx) == 4:
			screenCnt = approx
			break
# show the contour (outline) of the piece of paper
print("STEP 2: Find contours of paper")
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)
cv2.imshow("Outline", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# apply a four point perspective transform to both the
# original image and grayscale image to obtain a top-down
# birds eye view of the paper
paper = four_point_transform(orig, screenCnt.reshape(4, 2))
warped = four_point_transform(gray, screenCnt.reshape(4, 2))
cv2.imshow("paper",paper)
cv2.imshow("warped",warped)
cv2.waitKey(0)
cv2.destroyAllWindows()
# apply Otsu's thresholding method to binarize the warped
# piece of paper
thresh = cv2.threshold(warped, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
cv2.imshow("otsu",thresh)
cv2.waitKey(0)
#print("thresh is:",thresh)
	# find contours in the thresholded image, then initialize
# the list of contours that correspond to questions
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
questionCnts = []
# loop over the contours
for c in cnts:
	# compute the bounding box of the contour, then use the
	# bounding box to derive the aspect ratio
	(x, y, w, h) = cv2.boundingRect(c)
	ar = w / float(h)
	# in order to label the contour as a question, region
	# should be sufficiently wide, sufficiently tall, and
	# have an aspect ratio approximately equal to 1
	if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
		questionCnts.append(c)
# sort the question contours top-to-bottom, then initialize
# the total number of correct answers
questionCnts = contours.sort_contours(questionCnts,
	method="top-to-bottom")[0]
#print(len(questionCnts))
correct = 0
min=500
#print(np.arange(0,len(questionCnts),5))
#

#print(questionCnts[j:j + 5])
#cnts = contours.sort_contours(questionCnts[j:j + 5],method="right-to-left")[0]
#print("sorted cnts r to l",cnts)
# each question has 5 possible answers, to loop over the
# question in batches of 5
for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):
	# sort the contours for the current question from
	# left to right, then initialize the index of the
	# bubbled answer

	cnts = contours.sort_contours(questionCnts[i:i + 5])[0]
	bubbled = None
	flag=0
	print("Q,I",q,i)
		#loop over the sorted contours
	for (j, c) in enumerate(cnts):
        # construct a mask that reveals only the current
		# "bubble" for the question
		mask = np.zeros(thresh.shape, dtype="uint8")
		cv2.drawContours(mask, [c], -1, 255, -1)
		print("j,c",j)
		cv2.imshow("mask",mask)
		#cv2.imshow("threshold",thresh)
		cv2.waitKey(0)
		# apply the mask to the thresholded image, then
		# count the number of non-zero pixels in the
		# bubble area
		mask = cv2.bitwise_and(thresh, thresh, mask=mask)
		cv2.imshow("mergemask",mask)
		cv2.waitKey(0)
		total = cv2.countNonZero(mask)
		print("total",total)
		if total >=min:
		# if the current total has a larger number of total
		# non-zero pixels, then we are examining the currently
		# bubbled-in answer
			flag=1
			if bubbled is None or total > bubbled[0]:
				bubbled = (total, j)
				print("No. of non zero pixel,count",bubbled)
				#continue
		# else:
		# 	flag=0
		# 	#print("no bubbled answer")
		# 	continue

	# initialize the contour color and the index of the
	# *correct* answer

	color = (0, 0, 255)
	k = ANSWER_KEY[q]
	print("answer",k)

	if flag==1:
		if k == bubbled[1]:
			color = (0, 255, 0)
			correct += 1
			# draw the outline of the correct answer on the test
	elif flag==0:
		print("Answer Skipped")
	cv2.drawContours(paper, [cnts[k]], -1, color, 3)
	cv2.imshow("paper",paper)

# grab the test taker
score = (correct / 5.0) * 100
print("[INFO] score: {:.2f}%".format(score))
cv2.putText(paper, "{:.2f}%".format(score), (10, 30),
	cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
cv2.imshow("Original", image)
cv2.imshow("Exam", paper)
cv2.waitKey(0)
cv2.destroyAllWindows()
