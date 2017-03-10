#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------------------

import socket
import sys
import select
from threading import Thread
#---------------------------------------------------------------------------------------------
# handle CTRL + C
import signal
import sys
def signal_handler(signal, frame):
  print('You pressed Ctrl+C!')
signal.signal(signal.SIGINT, signal_handler)
#---------------------------------------------------------------------------------------------
HOST = ''   # Symbolic name, meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

#Bind socket to local host and port
try:
  server_socket.bind((HOST, PORT))
except socket.error as msg:
  print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
  sys.exit()

print('Socket bind complete')

#Start listening on socket
server_socket.listen(10)

# list of socket to local server
sock_2_local_server = []
# list of socket from remote clients
sock_from_client = []
#---------------------------------------------------------------------------------------------
# communicating thread
do_comunicate = True

def communicate():
  
  while do_comunicate :
    
    sockets = []
    # fill the pool of socket to read from
    for s in sock_2_local_server :
      sockets.append(s)

    for s in sock_from_client :
      sockets.append(s)

    # let's read
    try:
      inputready,outputready,exceptready = select.select(sockets, [], [], 0.1)
    except select.error:
      break

    for s in inputready:
      data = s.recv(4096)
      if not data:
        print('Connection is closed')
        

  '''if s_acc == conn:
    data = conn.recv(4096)
    print("Received from client " + str(len(data)) + " bytes")
    if not data:
      print('client closed the connection')
      is_conn = 0
      break
    else :
      sock.sendall(data)
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
'''
#---------------------------------------------------------------------------------------------
# run communicating thread
t1 = Thread(target=communicate, args=[])
t1.start()

#now keep talking with the client
while True:

  try:
  
    print ('Socket now listening')
    sock, addr = server_socket.accept()
    print ('Connected with ' + addr[0] + ':' + str(addr[1]))
    print('socket from client: ' + str(sock.fileno()))
    sock_from_client.append(sock)
    sock_2_local_server.append(socket.create_connection(('localhost', 3000)))
    print('Waiting for next client...')

  except KeyboardInterrupt:
    do_comunicate = False
    t1.join()
    for s in sock_2_local_server :
      s.close()

    for s in sock_from_client :
      s.close()
#---------------------------------------------------------------------------------------------
# finito, the server is going down
server_socket.close()
