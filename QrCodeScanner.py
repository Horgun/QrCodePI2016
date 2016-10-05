#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2 as cv
import numpy as np
import time

TAM = 150

class Square:
	x1 = x2 = y1 = y2 = None
	width = None

	def __init__(self, x1, x2, y1, y2):
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.width = x2 - x1

	def __str__(self):
		string = "X1 = " + str(self.x1) + " Y1 = " + str(self.y1) + "\nX2 = " + str(self.x2) + " Y2 = " + str(self.y2) + "\nW = " + str(self.width)
		return string + "\n"


def canClose():
	ch = 0xFF & cv.waitKey(1)
	return ch == 27

def getSquare(approx):
	X = []
	Y = []
	for i in range(4):
		X.append(int(approx[i][0][0]))
		Y.append(int(approx[i][0][1]))
	s = Square(min(X), max(X), min(Y), max(Y))
	return s

def getSquares(img):
	imgBorders = img.copy()
	contours, hierarchy = cv.findContours(img,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)#encontra os contornos
	contours = sorted(contours, key = cv.contourArea, reverse = True)[:20]#ordena os contornos pelo tamanho da área, do maior pro menor, o 10 maiores
	borders = []
	squares = []
	#filtrar
	for c in contours:
		peri = cv.arcLength(c, True)
		approx = cv.approxPolyDP(c, 0.018 * peri, True)
		if len(approx) == 4 :#se o contorno tem X pontos
			s = getSquare(approx)
			squares.append(s)
			borders.append(approx)#adiciona os contornos na lista
	return borders, imgBorders, squares;

def getPositionMarkers(squares):
	module3 = []
	module5 = []
	module7 = []


	return 0
	

def GetCode():
	cap = cv.VideoCapture(0)

	if cap is None or not cap.isOpened():
		print 'Warning: unable to open video source: 0'
		quit(-1)
    
	ret, img = cap.read()

	h, w = img.shape[:2]

	meioH = h/2
	meioV = w/2

	while not canClose():
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
		
		screenCnt, imgBorders, squares = getSquares(imgCaixa)
		algumaCoisa = getPositionMarkers(squares)
		img2 = img[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM]
		cv.drawContours(img2, screenCnt, -1, (0,255,0), 1)#desenha os contornos
		imgEscura = cv.flip(imgEscura, 1)
		cv.imshow("QrCode Reader", imgEscura)
		cv.imshow("QrCode", imgCaixa)
		cv.imshow("Contornos", imgBorders)
		cv.imshow("Contornos2", img2)

	cap.release()
	cv.destroyAllWindows()
	return ""

if __name__ == "__main__":
	print GetCode()