#include <DCMotor.h>

DCMotor mot_izq(M0_EN, M0_D0, M0_D1);
DCMotor mot_der(M1_EN, M1_D0, M1_D1);

String lectura;
int vel = 0;
void setup(){
  Serial.begin(9600);
  mot_izq.brake();
  mot_der.brake();
}

void loop(){
  if(Serial.available()){
    //Serial.println(Serial.read());
    //char lectura = Serial.read();
    
    lectura = Serial.readStringUntil('\n');
    //Serial.println(lectura);
    if(lectura[0] == 'i'){ //Si está en positivo o tiene signo menos antes
      //Serial.print("Velocidad izquierda: ");

      if(lectura.length() >= 2 && lectura[1] != '-'){ //si es un número solo y positivo
        vel = lectura[1] - '0';
      }
      else if(lectura.length() == 3 && lectura[1] == '-'){//si es un número solo y negativo
        vel = '0' - lectura[2];
      }
      else if(lectura.length() == 3 && lectura[1] != '-'){//si es un número de dos dígitos y positivo
        vel = 10*(lectura[1] - '0') + lectura[2] - '0';
      }
      else if(lectura.length() == 4 && lectura[1] == '-'){//si es un número de dos dígitos y negativo
        vel = 10*('0' - lectura[2]) + ('0' - lectura[3]);
      }
      mot_izq.setSpeed(vel);

      //Serial.println(vel);
    }
    else if(lectura[0] == 'd'){ //Si está en positivo o tiene signo menos antes
      //Serial.print("Velocidad derecha: ");
      if(lectura.length() == 2 && lectura[1] != '-'){ //si es un número solo y positivo
        vel = lectura[1] - '0';
      }
      else if(lectura.length() == 3 && lectura[1] == '-'){//si es un número solo y negativo
        vel = '0' - lectura[2];
      }
      else if(lectura.length() == 3 && lectura[1] != '-'){//si es un número de dos dígitos y positivo
        vel = 10*(lectura[1] - '0') + lectura[2] - '0';
      }
      else if(lectura.length() == 4 && lectura[1] == '-'){//si es un número de dos dígitos y negativo
        vel = 10*('0' - lectura[2]) + ('0' - lectura[3]);
      }
      //Serial.println(vel);
      mot_der.setSpeed(vel);
    }

    Serial.flush();
  }  
}




