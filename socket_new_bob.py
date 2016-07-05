#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  socket_new.py
#  
#  Copyright 2016 chendi <chendi@ZANGCHENDI>
import random
import os
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
import time
host = 'localhost'

class Message:
	def __init__(self, sender, body, current_round, isbid = False, isresult=False):
		self.sender=sender
		self.body=body
		self.is_bid=isbid
		self.is_result=isresult
		self.current_round=current_round
	
	def check(self):
		if (self.is_bid*self.is_result):
			return False
		else:
			return True
		
	def encode(self):
		if self.is_bid:
			message='bid from '+ self.sender.username+' round '+ str(self.current_round) + ' : '+str(self.body) 
		elif self.is_result:
			message='result from '+ self.sender.username+' round '+ str(self.current_round) + ' : '+str(self.body) 
		else:
			message='message from '+ self.sender.username+' round '+ str(self.current_round) + ' : '+str(self.body) 
		return message.encode()
	def print_message(self):
		print (self.encode())

class Peer:
	def __init__(self, ip, username,peerlist, isactive=False):
		self.ip=ip
		self.username=username
		self.is_active=isactive
		self.messagebox=[]
		self.bids=[]
		self.results=[]
		self.pref=None
		self.index=len(peerlist)
		peerlist.append(self)
	
	def disconnect(self):
		self.is_active=False
		
	def print_peer(self):
		print('name=',self.username,'  ip=', self.ip,' index=', self.index, 'is active:' , self.is_active)
	
	def print_message_box(self):
		print('messageBox=')
		for message in self.messagebox:
			message.print_message()
	
	def clear_message_box(self):
		self.messageBox=[]
		return 0
	
	def clear_all(self):
		self.bids=[]
		self.results=[]
		self.pref=None
		return 0
	
	def random_bid_generator(self, bids, peer_list,round_current ):
		if self.is_active:
			size=count_active(peer_list)
			num = random.randint(0, size-1)
			bid = Message(self, num, round_current, True, False)
			self.bids.append(bid)
			bids.append(bid) 		
			return bid
		else:
			return None
			
	def input_bid(self, bids, peer_list, round_current):
		if self.is_active:
			num = int(input('--> Saisissez un entier entre 0 et ' + str(count_active(peer_list)-1) + ': '	))
			bid = Message(self, num, round_current, True, False)
			self.bids.append(bid)
			bids.append(bid)
			return bid
		else:
			return None
	
	def random_message_generator(self, round_current ):
		if self.is_active:
			text='salut, je suis '+self.username
			message=Message(self,text, round_current,False,False)
			return message
		else:
			return None
	
	def input_message(self, round_current):
		m=str(input('Congratulations! you win! now you can type in your message: '))
		message=Message(self, m, round_current, False, False)
		return message
		
	def receive(self):
		sock = socket(AF_INET, SOCK_STREAM)         # ip addresses tcp connection    
		sock.bind(('', self.ip))    				# bind to port on this machine    
		sock.listen(5)                              # allow up to 5 pending clients    
		while True:
			conn, addr = sock.accept()				 # wait for client to connect 
			try:       
				conn.settimeout(None)	                    
				data = conn.recv(1024)                  # read bytes data from this client  
				if data:      
					reply = 'server got: [%s]' % data
				
					print(reply)       # conn is a new connected socket        
					conn.send(reply.encode()) 
			except :
				print('timeout')
				      
	def send(self, message,peer):
		sock = socket(AF_INET, SOCK_STREAM)    
		sock.connect((host, peer.ip))                     
		sock.send(message.encode())
		sock.close()
	
	def send_all(self, message, peerlist):	
		for peer in peerlist:
			s=Thread(target=peer.send, args=(message, peer))
			s.setDaemon(True)
			s.start()
		
	
	def get_current_round(self):
		current_dir=os.getcwd()
		d=current_dir+'\\'+self.username
		os.chdir(d)
		f = open('registre.txt', 'r') 
		content = f.readlines() 
		for line in content: 
			if line == "\n": 
				content.remove(line) 
		n = len(content)
		if n==0:
			f.close()
			os.chdir(current_dir)
			return 1
		ligne = content[n-1] 
		ligne = ligne.split() 
		index = len(ligne) - 1 
		current_round = int(ligne[index]) + 1 
		f.close() 
		os.chdir(current_dir)
		return current_round
		
def count_active( peer_list):
	n=0
	for peer in peer_list:
		if peer.is_active:
			n+=1
	return n
			
#Creat Liste
Peer_list=[]
alice=Peer(50001, 'alice', Peer_list , True)
bob=Peer(50002 , 'bob' , Peer_list , True)
catheline=Peer(50003, 'catheline' , Peer_list , True)
bids=[]
if __name__ == '__main__':
	thread=[]
	moi=catheline
	t=Thread(target=moi.receive)
	thread.append(t)
	bid=moi.random_bid_generator(bids, Peer_list, moi.get_current_round())
	#print(bid)
	t=Thread(target=moi.send_all, args=(bid, Peer_list))
	thread.append(t)
	for t in thread:
		t.start()
		time.sleep(2)
