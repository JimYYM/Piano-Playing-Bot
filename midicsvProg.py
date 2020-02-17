import os
import subprocess
import re
import serial
from time import sleep
import sys

COM_PORT = 'COM6'  
BAUD_RATES = 9600
ser = serial.Serial(COM_PORT, BAUD_RATES)

def ImportMidi():
    outfd=open('Out.txt','w')
    errfd=open('Err.txt','w')

    subprocess.call(['midicsv','-v','test6.mid','Out.txt'],stdout=outfd,stderr=errfd) #midicsv prog write data to Out.txt

    outfd.close()
    errfd.close()

def EditCsvData(CsvData):
    with open('Out.txt','r',encoding='utf-8',errors='ignore') as file_object:
        lines = file_object.readlines()
        count=0        
        for line in lines:
            line=re.split(', |\n',line)
            #print(line)
            if line[2]=='Note_on_c' or line[2]=='Note_off_c'or (line[2]=='Control_c' and line[4]=='64'):
                CsvData.append(line)


def DataTransformer(event):
    #NoteToEngineMapping=[48,50,52,53,55,57,59]#Midi number mapping to engine. Edit here if adding more engines or octave shift
    NoteToEngineMapping=[60,62,64,65,67,69,71]
    
    EngineNo=NoteToEngineMapping.index(int(event[4]))
    EngineNo=str(EngineNo).zfill(2)
    
    if(event[2]=='Note_on_c'):
        EngineNo=EngineNo+' '+'1'+' '+event[4]
    elif (event[2]=='Note_off_c'):
        EngineNo=EngineNo+' '+'0'+' '+event[4]
    time=str(event[1]).zfill(5)
    
    return time+' '+EngineNo+"\n"

def SerialCommuication(InputData):
    try:
        ser.write(InputData.encode("utf-8"))
        
    except KeyboardInterrupt:
        ser.close()
        print('再見！')

def SustainControl(CsvData,EditedCsvData):
    Stack=[]
    Sustain=0 #boolean switch. 1 = sustain on, 0 = sustain off
    for i in range (len(CsvData)):
        if(CsvData[i][2]=='Control_c' and CsvData[i][4]=='64'): #if it's a sustain message
            if int(CsvData[i][5])>=64: #sustain on
                print('sustain on')
                Sustain=1
            elif int(CsvData[i][5])<=64: #sustain off
                print('sustain off')
                Sustain=0
                if Stack: #if Stack is not empty
                    for item in Stack: 
                        item[1]=CsvData[i][1]#change the time of note off for sustaining
                        EditedCsvData.append(item)#rearrange the order
                        
                    Stack=[] #clear stack
                    
        elif(Sustain==1 and CsvData[i][2]=='Note_off_c'): #if a note off should be sustained
            Stack.append(CsvData[i])
            print(CsvData[i])
            
        else:#ordinary notes
            EditedCsvData.append(CsvData[i])
        

def main():
    os.chdir("C:/Users/Jassson/Desktop/midicsv-1.1")
    print(os.getcwd())
    
    ImportMidi()#call midicsv program to read midi and write data to Out.txt

    CsvData=[]
    EditCsvData(CsvData)#store data into array

    EditedCsvData=[]
    SustainControl(CsvData,EditedCsvData)
    for line in EditedCsvData: print(line)

    sleep(5)
    
    SerialCommuication("\n")#tell arduino to start reading serial data
    sleep(1)

    for i in range (len(EditedCsvData)):
        if EditedCsvData[i][2]=='Note_on_c' or EditedCsvData[i][2]=='Note_off_c':
            InputData=DataTransformer(EditedCsvData[i])
            print(InputData)
            SerialCommuication(InputData)
            
            if i+1!=len(EditedCsvData):
                DeltaTime=(int(EditedCsvData[i+1][1])-int(EditedCsvData[i][1]))/200 #might have bug
                print(DeltaTime)
            elif i+1==len(EditedCsvData):
                print('End')
            else:
                print('report')
            
            sleep(DeltaTime)
            
            while ser.in_waiting:
                mcu_feedback = ser.readline().decode()  # 接收回應訊息並解碼
                print('控制板回應：', mcu_feedback)

    #print('Enter your name:')
    #x = input()
    #SerialCommuication("00000 00 1\n")            
            
    ser.close()

main()
