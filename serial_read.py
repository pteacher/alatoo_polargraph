import time
import serial


ser = serial.Serial(
  port='/dev/ttyS0',
  baudrate = 57600,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=0.01
)
counter=0
f = open('5.ngc', 'r')
init = False

while 1:
  x=ser.readline()
  if init is False:
    ser.write(str.encode('HELP;'))
    init = True
  try:
    if len(x) > 0:
      print(x.decode())
      if '>' in x.decode():
        line = f.readline()
        if line == '':
          break
        comm = str.encode(line.strip() + ';')
        print(comm)
        ser.write(comm)
  except:
    print("olmadi")
  
