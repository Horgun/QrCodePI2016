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
		ret, imgCaixa = cv.threshold(imgCaixa, 127, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
		kernel = np.ones((5,5),np.uint8)
		imgCaixa = cv.morphologyEx(imgCaixa, cv.MORPH_OPEN, kernel)
		imgEscura = img.copy()
		cv.convertScaleAbs(img, imgEscura, 1.0/2, 0)
		imgEscura[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM] = img[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM]
		imgBorders = imgCaixa.copy()
		contours, hierarchy = cv.findContours(imgBorders,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
		contours = sorted(contours, key = cv.contourArea, reverse = True)[:10]
		screenCnt = []
		for c in contours:
			peri = cv.arcLength(c, True)
			approx = cv.approxPolyDP(c, 0.021 * peri, True)
			if len(approx) == 4:
				screenCnt.append(approx)
				if len(screenCnt) == 3:
					break
		img2 = img[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM]
		print screenCnt
		cv.drawContours(img2, screenCnt, -1, (0,255,0), 2)
		imgEscura = cv.flip(imgEscura, 1)
		cv.imshow("QrCode Reader", imgEscura)
		cv.imshow("QrCode", imgCaixa)
		cv.imshow("Contornos", imgBorders)
		cv.imshow("Contornos2", img2)
		ch = 0xFF & cv.waitKey(1)
		if ch == 27:
			break

	cap.release()
	cv.destroyAllWindows()
	return ""

if __name__ == "__main__":
	print GetCode()