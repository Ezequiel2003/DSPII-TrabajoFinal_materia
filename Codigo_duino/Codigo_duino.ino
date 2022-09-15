#include <DCMotor.h>

DCMotor mot_izq(M0_EN, M0_D0, M0_D1);
DCMotor mot_der(M1_EN, M1_D0, M1_D1);

void setup(){
  Serial.begin(9600);
  mot_izq.brake();
  mot_der.brake();
}

void loop(){ 
  if( Serial.available() ){
    char lectura = Serial.read();
    if(lectura == 'a'){ //corte de linea
      mot_izq.setSpeed(37);
      mot_der.setSpeed(37);
    }
    else if(lectura == 'b'){ //dentro de la linea negra
      mot_izq.setSpeed(37);
      mot_der.setSpeed(35); 
    }
    else if(lectura == 'c'){ //doblar a la derecha, suave
      mot_izq.setSpeed(40);
      mot_der.setSpeed(30); 
    }
    else if(lectura == 'd'){ //doblar a la derecha, brusco
      mot_izq.setSpeed(0);
      mot_der.setSpeed(-40);
    }
    else if(lectura == 'e'){ //doblar a la izquierda, suave
      mot_izq.setSpeed(30);
      mot_der.setSpeed(35);
    }
    else if(lectura == 'f'){ //doblar a la izquierda, brusco
      mot_izq.setSpeed(-40);
      mot_der.setSpeed(0);
    }
    else if(lectura == 'g'){ //doblar a la derecha, medio
      mot_izq.setSpeed(37);
      mot_der.setSpeed(0);
    }
    else if(lectura == 'h'){ //doblar a la izquierda, medio
      mot_izq.setSpeed(0);
      mot_der.setSpeed(35);
    }
    else if(lectura == 'z'){ //significa que se tiene que apagar
      mot_izq.setSpeed(0);
      mot_der.setSpeed(0);
    }
    Serial.flush();
  }
}







