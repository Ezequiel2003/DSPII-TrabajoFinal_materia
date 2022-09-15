import cv2
import numpy as np

img = cv2.imread('perspectiva.png')

alto,ancho = img.shape[:2]

distancia_borde_izquierdo = "None"
distancia_borde_derecho = "None"
ancho_aprox = 95+112 #con valores medidos respecto a las distancias de los bordes, ancho de la línea
for i in range(0,int(ancho/2)-1):
    if(img[int(alto/2)-1,int(ancho/2)-1-i , 2] == 255):
        distancia_borde_izquierdo = i
    if(img[int(alto/2)-1,int(ancho/2)-1+i , 2] == 255):
        distancia_borde_derecho = i
        
#con el for, recorro la mitad de la imagen en todo el ancho, y busco aquellos 
#puntos que estén en rojo, esto significa que son los bordes, de ahí sacar la distancia
