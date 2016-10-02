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
		imgCaixa = img[meioH-TAM:meioH+TAM, meioV-TAM:meioV+TAM]#pega o pedaço da imagem que será analisado
		imgCaixa = cv.cvtColor(imgCaixa, cv.COLOR_BGR2GRAY)#converte para escala de cinza
		ret, imgCaixa = cv.threshold(imgCaixa, 127, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)#realiza o limiar
		kernel = np.ones((3,3),np.uint8)#cria o kernel
		imgCaixa = cv.morphologyEx(imgCaixa, cv.MORPH_OPEN, kernel)#Faz erosion e dilation
		imgEscura = img.copy()#imagem para fazer a parte escura q é exibida
		cv.convertScaleAbs(img, imgEscura, 1.0/2, 0)#faz a imagem ficar escura
		imgEscura[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM] = img[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM]#recupera apenas a parte que deve ficar clara na exibição e coloca na imagem escura
		imgBorders = imgCaixa.copy()
		contours, hierarchy = cv.findContours(imgBorders,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)#encontra os contornos
		contours = sorted(contours, key = cv.contourArea, reverse = True)[:10]#ordena os contornos pelo tamanho da área, do maior pro menor, o 10 maiores
		screenCnt = []

		#filtrar
		for c in contours:
			peri = cv.arcLength(c, True)
			approx = cv.approxPolyDP(c, 0.018 * peri, True)
			if len(approx) == 4:#se o contorno tem 4 pontos
				screenCnt.append(approx)#adiciona os contornos na lista
				if len(screenCnt) == 3:#se já tiver 3 elementos na lista
					break#parar

		img2 = img[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM]
		cv.drawContours(img2, screenCnt, -1, (0,255,0), 1)#desenha os contornos
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