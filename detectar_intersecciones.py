import cv2
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

upper_green = np.array([80,255,255],np.uint8)
lower_green = np.array([45,80,5],np.uint8)

mask_izq = np.zeros((480,640), np.uint8)
mask_der = np.zeros((480,640), np.uint8)
mask_izq[:,0:319] = 255
mask_der[:,320:639] = 255

while(cap.isOpened()):
    
  # Tomar de a un frame
  ret, frame = cap.read()
  
  
  # Convertir BGR en HSV
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
  
  # "umbralizar" la imagen en hsv para que quede solamente el verde
  mask2 = cv2.inRange(hsv,lower_green,upper_green)
  
  # operación AND bit a bit con la mascara y el frame capturado
  green = cv2.bitwise_and(frame,frame,mask = mask2)
  
  #separar la imagen en dos
  verde_izq = cv2.bitwise_and(green,green,mask = mask_izq)
  verde_der = cv2.bitwise_and(green,green,mask = mask_der)
  
  #convertir ambas mitades a escala de gris
  verde_izq_gray = cv2.cvtColor(verde_izq, cv2.COLOR_BGR2GRAY)
  verde_der_gray = cv2.cvtColor(verde_der, cv2.COLOR_BGR2GRAY)
  
  #Para la imagen izquierda, se obtienen los contornos y luego se extrae el area mas grande
  contornos_izq,_ = cv2.findContours(verde_izq_gray, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  
  area_izq = 0
  area_der = 0
  for c in contornos_izq:
      area = cv2.contourArea(c)
      if(area > area_izq): #sobreescribe el area con el mayor valor que va encontrando
          area_izq = area
            
  print("area mayor_izq",area_izq)
  
  #Para la imagen derecha, se obtienen los contornos y luego se extrae el area mas grande
  contornos_der,_ = cv2.findContours(verde_der_gray, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  
  for c in contornos_der:
      area = cv2.contourArea(c)
      if(area > area_der): #sobreescribe el area con el mayor valor que va encontrando
          area_der = area
      
  print("area mayor_der",area_der)
  
  cv2.imshow('frame',frame)  
  cv2.imshow('Verde',green)
  cv2.imshow('Verde_izq',verde_izq)
  cv2.imshow('Verde_der',verde_der)
  
  k = cv2.waitKey(1)
  # si pulsa q se rompe el ciclo
  if k == ord("q"):
    break

#libera todo
cap.release() 
cv2.destroyAllWindows()
