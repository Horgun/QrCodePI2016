#!/usr/bin/python
# -*- coding: utf-8 -*-

#Alunos: Johnata Rodrigo Pinheiro Montanher, Paulo Henrique Silva de Arruda, Sávio Soares Meira, Vicente Antonio da Conceição Junior

import cv2 as cv
import numpy as np
import time
import math

TAM = 150

class Square:
	x1 = x2 = y1 = y2 = None
	width = None

	def __init__(self, x1, x2, y1, y2):
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.width = float(x2 - x1)

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

def abso(n):
	if n < 0:
		return -n
	return n

def getPositionMarkers(s):
	mesmoTamanho = [[], [], []]
	if len(s) > 0:#separar entre os modulos 7, 5 e 3
		p = 0
		for i in range(3):
			result = 0;
			contador = 0
			c = 0
			for x in s:
				if c >= p:
					if abs(result - x.width) < 5:
						if contador < 3:
							contador = contador + 1
							mesmoTamanho[i].append(x)
						if contador >= 3:
							p += 1
							break
					else:
						if contador >= 3:
							break
						contador = 1
						mesmoTamanho[i] = []
						mesmoTamanho[i].append(x)
						result = x.width
						
					p += 1
					c += 1
				else:
					c += 1

	if (len(mesmoTamanho[0]) == 3 and len(mesmoTamanho[1]) == 3):
		razao = mesmoTamanho[0][0].width / mesmoTamanho[1][0].width
		if 1.3 < razao < 1.5 or 2.2 < razao < 2.6:
			return mesmoTamanho

	return -1
	

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
		imgCaixa = img[meioH-TAM:meioH+TAM, meioV-TAM:meioV+TAM]#pega o pedaço da imagem que será analisado
		imgCaixa = cv.cvtColor(imgCaixa, cv.COLOR_BGR2GRAY)#converte para escala de cinza
		ret, imgCaixa = cv.threshold(imgCaixa, 127, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)#realiza o limiar
		kernel = np.ones((3,3),np.uint8)#cria o kernel
		imgCaixa = cv.morphologyEx(imgCaixa, cv.MORPH_OPEN, kernel)#Faz erosion e dilation
		
		screenCnt, imgBorders, squares = getSquares(imgCaixa)

		modules = getPositionMarkers(squares)
		if modules != -1:
			x = modules[0].pop(0)
			y = modules[0].pop(0)
			z = modules[0].pop(0)

			p1 = [x.x1 + x.width/2, x.y1 + x.width/2, x.width]
			p2 = [y.x1 + y.width/2, y.y1 + y.width/2, y.width]
			p3 = [z.x1 + z.width/2, z.y1 + z.width/2, z.width]

			Dp1p2 = math.sqrt(math.pow((p1[0]-p2[0]),2) + math.pow((p1[1]-p2[1]),2))
			Dp1p3 = math.sqrt(math.pow((p1[0]-p3[0]),2) + math.pow((p1[1]-p3[1]),2))
			Dp2p1 = Dp1p2
			Dp2p3 = math.sqrt(math.pow((p2[0]-p3[0]),2) + math.pow((p2[1]-p3[1]),2))
			Dp3p1 = Dp1p3
			Dp3p2 = Dp2p3

			if abs(Dp1p2 - Dp1p3) < 6:
				Dzinho = Dp1p2
				topLeft = p1
				ponto2 = p2
				ponto3 = p3
			elif abs(Dp2p1 - Dp2p3) < 6:
				Dzinho = Dp2p1
				topLeft = p2
				ponto2 = p1
				ponto3 = p3
			elif abs(Dp3p1 - Dp3p2) < 6:
				Dzinho = Dp3p1
				topLeft = p3
				ponto2 = p1
				ponto3 = p2
			else:
				continue

			if  ponto2[1] < topLeft[1] and ponto3[0] > topLeft[0]:
				bottomLeft = ponto3
				topRight = ponto2
			elif ponto3[1] < topLeft[1] and ponto2[0] > topLeft[0]:
				bottomLeft = ponto2
				topRight = ponto3
			elif ponto2[1] > topLeft[1] and ponto3[0] > topLeft[0]:
				bottomLeft = ponto2
				topRight = ponto3
			elif ponto3[1] > topLeft[1] and ponto2[0] > topLeft[0]:
				bottomLeft = ponto3
				topRight = ponto2
			elif ponto2[1] > topLeft[1] and ponto3[0] < topLeft[0]:
				bottomLeft = ponto3
				topRight = ponto2
			elif ponto3[1] > topLeft[1] and ponto2[0] < topLeft[0]:
				bottomLeft = ponto2
				topRight = ponto3
			elif ponto2[1] < topLeft[1] and ponto3[0] < topLeft[0]:
				bottomLeft = ponto2
				topRight = ponto3
			elif ponto3[1] < topLeft[1] and ponto2[0] < topLeft[0]:
				bottomLeft = ponto3
				topRight = ponto2

			pts1 = np.float32([[topLeft[0], topLeft[1]], [bottomLeft[0], bottomLeft[1]], [topRight[0], topRight[1]]])
			pts2 = np.float32([[16,16],[16,84],[84,16]])

			M = cv.getAffineTransform(pts1,pts2)

			imgRegistro = img[meioH-TAM:meioH+TAM, meioV-TAM:meioV+TAM]
			imgRegistro = cv.warpAffine(imgRegistro,M,(100,100))
			imgRegistro = cv.cvtColor(imgRegistro, cv.COLOR_BGR2GRAY)#converte para escala de cinza
			ret, imgRegistro = cv.threshold(imgRegistro, 127, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)#Binarizar imagem

			cv.imshow("Registro", imgRegistro)

		imgEscura = img.copy()#imagem para fazer a parte escura q é exibida
		cv.convertScaleAbs(img, imgEscura, 1.0/2, 0)#faz a imagem ficar escura
		
		img2 = img[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM]
		cv.drawContours(img2, screenCnt, -1, (0,255,0), 1)#desenha os contornos

		imgEscura[meioH-TAM:meioH+TAM,meioV-TAM:meioV+TAM] = img2
		imgEscura = cv.flip(imgEscura, 1)
		cv.imshow("QrCode Reader", imgEscura)

	cap.release()
	cv.destroyAllWindows()


GetCode()