#include <Servo.h>
Servo myServos[6];

String data; // for incoming serial data

//for each midi event
int absoluteTime; 
int ServoNo;//a ServoNo maps to a specific note
int NoteOnOff;
int ServoDegree;
float MidiNoteNumber;
int Time=0; 

void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  
  for(int i=0; i<6  ;i++){
    myServos[i].attach(i+2); 
    myServos[i].write(90);     
    delay(30);  
  }

  pinMode(9, OUTPUT); // Set buzzer - pin 9 as an output

}

void loop() {
  // send data only when you receive data:
  if (Serial.available() > 0) {
    data = Serial.readStringUntil('\n');
    
    //convert to char array
    char data_array[data.length()+1];
    data.toCharArray(data_array, data.length()+1);
    
    //split data
    char delim[] = " ";
    char* ptr = strtok(data_array, delim);
    absoluteTime=atoi(ptr);
    ptr = strtok(NULL, delim);
    ServoNo=atoi(ptr);
    ptr = strtok(NULL, delim);
    NoteOnOff=atoi(ptr);
    ptr = strtok(NULL, delim);
    MidiNoteNumber=atoi(ptr);//for buzzer

    if(NoteOnOff==1){
      ServoDegree=150;
    }
    else if(NoteOnOff==0){
      ServoDegree=90;
    }
    //Serial.println(absoluteTime);
    //Serial.println(ServoNo);
    //Serial.println(NoteOnOff);
    //Serial.println(MidiNoteNumber);//for buzzer
    //Serial.println(pow(2,(MidiNoteNumber-69)/12)*440);
    myServos[ServoNo].write(ServoDegree);
    
    if(NoteOnOff==1){//for buzzer
      tone(9, pow(2,(MidiNoteNumber-69)/12)*440 ,500);//frequency is multiplied by 10 for fitting the buzzer
    }//pow(2,(MidiNoteNumber-69)/12)*440*10
    
  }
}
