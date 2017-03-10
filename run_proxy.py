#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------------------

import socket
import sys
import select

HOST = ''   # Symbolic name, meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

#Bind socket to local host and port
try:
  s.bind((HOST, PORT))
except socket.error as msg:
  print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
  sys.exit()

print ('Socket bind complete')

#Start listening on socket
s.listen(10)


#now keep talking with the client
while 1:
  print ('Socket now listening')
  #wait to accept a connection - blocking call
  conn, addr = s.accept()
  print ('Connected with ' + addr[0] + ':' + str(addr[1]))
  print('socket from client')
  print(conn.fileno())
  
  sock = socket.create_connection(('localhost', 3000))
  print('socket to server')
  print(sock.fileno())
  
  #infinite loop so that function do not terminate and thread do not end.
  while True:

    reading = 1
    while reading == 1:
      try:
        inputready,outputready,exceptready = select.select([conn, sock], [], [], 0.1)
      except select.error:
        break

      is_conn = 1

      for aa in inputready:
        if aa == conn:
          
          data = conn.recv(4096)
          print("Received from client " + str(len(data)) + "bytes")
          if not data:
            print('client closed the connection')
            is_conn = 0
            break
          else :
            sock.sendall(data)
            #conn.sendall('500 problem HTTP/1.0\r\n\r\n'.encode('ascii'))
            print('send data to server')

        elif aa == sock:
          
          data = sock.recv(4096)
          print("Received from server " + str(len(data)) + "bytes")
          if not data:
            print('server closed the connection')
            is_conn = 0
            break
          else :
            conn.sendall(data)
            print('send data to client')

      # end for
      if is_conn == 0:
        conn.close()
        sock.close()
        reading = 0
        break
      
    # end While
    print('Waiting for next client')
    break # toto je blbost a treba to uplne odstranit!!!!
  #came out of loop
  conn.close()
  sock.close()

s.close()
