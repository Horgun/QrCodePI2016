#!/usr/bin/python
import cv2 as cv
import numpy as np
import time

TAM = 150

def GetCode():
	cap = cv.VideoCapture(0)

	if cap is None or not cap.isOpened():
		print 'Warning: unable to open video source: 0'
		quit(-1)
    
	ret, img = cap.read()

	h, w = img.shape[:2]

	meioH = h/2
	meioV = w/2
	while True:
		ret, img = cap.read()
		#img  = cv.medianBlur(img, 3)
		imgCaixa = img[meioH-TAM:meioH+TAM, meioV-TAM:meioV+TAM]	# Get read line content
		imgCaixa = cv.cvtColor(imgCaixa, cv.COLOR_BGR2GRAY)
		ret, imgCaixa = cv.threshold(imgCaixa, 128, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
		kernel = np.ones((15,15),np.uint8)
		imgCaixa = cv.morphologyEx(imgCaixa, cv.MORPH_OPEN, kernel)
		imgEscura = img.copy()
		cv.convertScaleAbs(img, imgEscura, 1.0/2, 0)
		imgEscura[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM] = img[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM]

		img = cv.flip(img, 1)
		cv.imshow("QrCode Reader", imgEscura)
		cv.imshow("QrCode", imgCaixa)
		ch = 0xFF & cv.waitKey(1)
		if ch == 27:
			break

	cap.release()
	cv.destroyAllWindows()
	return ""

if __name__ == "__main__":
	print GetCode()