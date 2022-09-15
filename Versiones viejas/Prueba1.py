import cv2
import numpy as np
from RC_lib import encontrar_bordes
import serial

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'DIVX') 
out = cv2.VideoWriter('output.avi',fourcc, 30.0, (1280,480))
#---------- configuración texto en imagen
font = cv2.FONT_HERSHEY_SIMPLEX
position = (0,50)
fontScale = 1
fontColor = (255,255,255)
thick = 3
#----------

#---------configuración comunicación serie con el Arduino
COM = 'COM6' #puerto com del duino bot, en windows
#COM = '/dev/ttyACM0' #en linux, se obtiene el nombre del dispositivo con el comando dmesg | grep -v disconnect | grep -Eo "tty(ACM|USB)." | tail -1
arduinoSerial = serial.Serial(COM,9600)
if(not(arduinoSerial.isOpen())): #si el puerto está cerrado, lo abre
    arduinoSerial.open()

pausa = 1

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True: 
        imagen_final,bordes = encontrar_bordes(frame,"binv","ext","r",5) #buscar bordes
        alto,ancho = imagen_final.shape[:2]
        
        pts1 = np.float32([[0,alto-100], [ancho-600,alto-350], [ancho-40, alto-350], [ancho,alto-100]]) #puntos de la imagen de entrada
        pts2 = np.float32([[0,alto], [0,0], [ancho,0], [ancho,alto]]) #puntos de la imagen de salida, deben tener coherencia con los puntos elegidos en la imagen de entrada
        M = cv2.getPerspectiveTransform(pts1, pts2) #matriz 3x3 con la transformación
        img_perspectiva = cv2.warpPerspective(imagen_final, M, (ancho,alto)) #aplicar la matriz de transformación a la imagen original
        
        cv2.line(imagen_final, (0,alto-100), (ancho-600,alto-350), (255,0,0),thickness = 5) #linea izquierda
        cv2.line(imagen_final, (0,alto-100), (ancho,alto-100), (255,0,0),thickness = 5) #linea inferior
        cv2.line(imagen_final, (ancho,alto-100), (ancho-40,alto-350), (255,0,0),thickness = 5) #linea derecha
        cv2.line(imagen_final, (ancho-600,alto-350), (ancho-40,alto-350), (255,0,0),thickness = 5) #linea superior
        
        #cv2.imshow('bordes',imagen_final)
        #cv2.imshow('perspectiva',img_perspectiva)
        
        cv2.line(img_perspectiva, (int(ancho/2),int(alto/2)-20),(int(ancho/2),int(alto/2)+20),(0,255,0),thickness=5)
        #cv2.imwrite('perspectiva.png', img_perspectiva)
                
        distancia_borde_izquierdo = "None"
        distancia_borde_derecho = "None"
        cont_izq = 0
        cont_der = 0
        ancho_aprox = 95+112 #con valores medidos respecto a las distancias de los bordes, ancho de la línea
        for i in range(0,int(ancho/2)-1):
            
            if(img_perspectiva[int(alto/2)-1,int(ancho/2)-1-i , 2] == 255 and cont_izq == 0 and img_perspectiva[int(alto/2)-1,int(ancho/2)-1-i, 0:1] == 0): #este contador es para que detecte una sola línea
                distancia_borde_izquierdo = i
                cont_izq +=1
            if(img_perspectiva[int(alto/2)-1,int(ancho/2)-1+i , 2] == 255 and cont_der == 0 and img_perspectiva[int(alto/2)-1,int(ancho/2)-1+i, 0:1] == 0):
                distancia_borde_derecho = i
                cont_der +=1
                
        #con el for, recorro la mitad de la imagen en todo el ancho, y busco aquellos 
        #puntos que estén en rojo, esto significa que son los bordes, de ahí sacar la distancia
              
        if(distancia_borde_izquierdo == "None" and distancia_borde_derecho == "None"): #hay un corte de línea
            cv2.putText(img_perspectiva,'Despacio, corte de linea',position,font,fontScale,fontColor,thick)
            letra = "a"
        
        elif(distancia_borde_izquierdo != "None" and distancia_borde_izquierdo < ancho_aprox and distancia_borde_derecho != "None" and  distancia_borde_derecho < ancho_aprox): #si está dentro la línea, sigue derecho
            cv2.putText(img_perspectiva,'Seguir derecho',position,font,fontScale,fontColor,thick)
            letra = "b"
        
        elif(distancia_borde_izquierdo == "None" and distancia_borde_derecho > 1 and distancia_borde_derecho < 240): #si se pasó a la izquierda, doblar a la derecha
            cv2.putText(img_perspectiva,'Doblar a la derecha',position,font,fontScale,fontColor,thick)
            cv2.line(img_perspectiva, (int(ancho/2),int(alto/2)), (int(ancho/2) + distancia_borde_derecho ,int(alto/2)), (255,0,0),thickness = 5) #linea izquierda
            letra = "c"
        
        elif(distancia_borde_izquierdo == "None" and distancia_borde_derecho > 240): #si se pasó a la izquierda por mucho, doblar a la derecha más brusco 
            cv2.putText(img_perspectiva,'Doblar mas a la derecha',position,font,fontScale,fontColor,thick)
            cv2.line(img_perspectiva, (int(ancho/2),int(alto/2)), (int(ancho/2) + distancia_borde_derecho ,int(alto/2)), (0,255,255),thickness = 5) #linea izquierda
            letra = "d"
        
        elif(distancia_borde_derecho == "None" and distancia_borde_izquierdo > 1 and distancia_borde_izquierdo < 240): #si se pasó a la derecha, doblar a la izquierda
            cv2.putText(img_perspectiva,'Doblar a la izquierda',position,font,fontScale,fontColor,thick)
            cv2.line(img_perspectiva, (int(ancho/2),int(alto/2)), (int(ancho/2) - distancia_borde_izquierdo ,int(alto/2)), (255,0,0),thickness = 5)
            letra = "e"
        
        elif(distancia_borde_derecho == "None" and distancia_borde_izquierdo > 240): #si se pasó a la derecha por mucho, doblar a la izquierda más brusco
            cv2.putText(img_perspectiva,'Doblar mas a la izquierda',position,font,fontScale,fontColor,thick)
            cv2.line(img_perspectiva, (int(ancho/2),int(alto/2)), (int(ancho/2) - distancia_borde_izquierdo ,int(alto/2)), (0,255,255),thickness = 5)
            letra = "f" 
        
        #cv2.imshow('perspectiva',img_perspectiva)
        out.write(cv2.hconcat([imagen_final, img_perspectiva]))
        cv2.imshow('Bordes y perspectiva', cv2.hconcat([imagen_final, img_perspectiva])) #muestra las imágenes juntas
        
        tecla = cv2.waitKey(1)
        
        if tecla == ord('q'): #terminar de ejecutar
            arduinoSerial.write("z".encode()) #Le dice a la otra placa que se debe apagar
            break
        
        elif tecla == ord('p'): #si se presiona la letra 'p' en el teclado, se pone en pausa o reanuda
            pausa = not pausa
            
        elif(pausa):
            letra = "z"
        
        else:       
            arduinoSerial.write(letra.encode())
        
        
    else:
        break
 
#Libera todo si la tarea ha terminado
cap.release()
out.release()
cv2.destroyAllWindows() 
arduinoSerial.close()

