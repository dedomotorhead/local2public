#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------------------------

import socket
import sys
import select
from threading import Thread
#---------------------------------------------------------------------------------------------
# Important --> this variable controlls the thread
do_comunicate = True
#---------------------------------------------------------------------------------------------
# list of sockets
comm_sockets = {}
#---------------------------------------------------------------------------------------------
def stop_comm_thread():
  global do_comunicate
  print('going to stop the thread')
  do_comunicate = False
  
  for k, s in comm_sockets.items() :
    print(s)
    s.shutdown()
    s.close()

  # finito, the server is going down
  global server_socket
  server_socket.close()

#---------------------------------------------------------------------------------------------
# handle CTRL + C
import signal
import sys

def signal_handler(signal, frame):
  print('You pressed Ctrl+C!')
  stop_comm_thread()
  
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
  print('Bind failed. Error Code : ' + str(msg.errno) + ' Message ' + msg.strerror)
  sys.exit()

print('Socket bind complete')

#Start listening on socket
server_socket.listen(10)

#---------------------------------------------------------------------------------------------
# communicating thread
def communicate():
  global comm_sockets
  print('Thread started')  
  while do_comunicate :
    
    sockets = []
    # fill the pool of socket to read from
    try:
      for k, ss in comm_sockets.items() :
        sockets.append(ss)
    except Exception as e:
      print(e)
      break
    
    # let's read
    try:
      inputready,outputready,exceptready = select.select(sockets, [], [], 0.1)
    except select.error as e:
      print('Thread got an error...' + e.strerror)
      print(e)
      break

    for s in inputready:
      data = s.recv(4096)
      print("Received " + str(len(data)) + " bytes")
      if not data:
        print('someone closed the connection')
        ss = comm_sockets[str(s.fileno())]
        del comm_sockets[str(ss.fileno())]
        del comm_sockets[str(s.fileno())]
        s.close()
        ss.close()
      else :
        comm_sockets[str(s.fileno())].sendall(data)
        
  print('Thread has finished')
#---------------------------------------------------------------------------------------------
# run communicating thread
t1 = Thread(target=communicate, args=[])
t1.start()

#now keep talking with the client
while do_comunicate:

  try:
  
    print('Socket now listening')
    sock, addr = server_socket.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))
    print('socket from client: ' + str(sock.fileno()))
    try:
      s = socket.create_connection(('localhost', 3000))
      comm_sockets[str(s.fileno())] = sock
      comm_sockets[str(sock.fileno())] = s
    except socket.error as serr:
      print(serr.strerror)
      sock.close()

    # debug
    #print(comm_sockets)
    print('Waiting for next client...')

  except Exception as e:
    print('Exception occured...')
    print(e)
  except KeyboardInterrupt:
    print('KeyboardInterrupt')
    
#---------------------------------------------------------------------------------------------
