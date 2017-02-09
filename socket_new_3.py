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
		print (self.encode().decode())

class Peer:
	def __init__(self, ip, username,peerlist, isactive=False):
		self.ip=ip
		self.username=username
		self.is_active=isactive
		self.messagebox=[]
		self.bid=None
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
			#self.bids.append(bid)
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
		m=str(input('please type in your message: \n'))
		message=Message(self, m, round_current, False, False)
		return message
		
	def receive(self, peerlist):
		sock = socket(AF_INET, SOCK_STREAM)         # ip addresses tcp connection    
		sock.bind(('', self.ip))    				# bind to port on this machine    
		sock.listen(5)                              # allow up to 5 pending clients
		text='bonjour, je suis '+self.username		#text to save in the registre
		
		message=Message(self,text,self.get_current_round())# can change
		time.sleep(5)
		self.send_all(message, peerlist) 
		self.bid=None
		#phase King
		while count_active(peerlist)>0:
			if self.is_active and self.bid==None:
				bids=[]
				self.bid=self.input_bid(bids, peerlist, self.get_current_round())
				time.sleep(3)  
				self.send_all(self.bid, peerlist)
			conn, addr = sock.accept()				 # wait for client to connect 
			     
			conn.settimeout(None)	                    
			data = conn.recv(1024)                  # read bytes data from this client  
			if data:      
				
				data=data.decode()
				reply = 'server got: [%s]' % data
				#print(reply)  
				head=data.split()[0]     					# conn is a new connected socket
				if head=='bid':
					#print(reply)
					self.receive_bid(data, peerlist)
				elif head=='message':
					
					self.receive_message(data, peerlist)
				elif head=='result':
					self.receive_result(data,peerlist)
				conn.send(reply.encode())
				
				
			
				      
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
		#print(time.clock())
	
	def receive_bid(self,data,peerlist):
		content=data.split()
		m=Message(finduser(content[2],peerlist),int(content[-1]),int(content[-3]),True, False)
		#m.print_message()
		#print(self.get_current_round())
		
		if m.current_round!=self.get_current_round():
			return
		for bid in self.bids:
			#bid.print_message()
			if bid.sender==m.sender:
				
				return
		#print( 'server got: [%s]' % data)
		self.bids.append(m)
		print( 'server got: [%s]' % data)
		if len(self.bids)==count_active(peerlist):
			result=self.calcul_result(peerlist)
			self.clear_all()
			result=Message(self,result, content[-1], False, True)
			self.send_all(result, peerlist) 
	
	def calcul_result(self, peerlist):
		s=0
		for bid in self.bids:
			s+=bid.body
		indice=s%count_active(peerlist)
		i=-1
		for peer in peerlist:
			if peer.is_active:
				i+=1
				if i==indice:
					return peer.username
	
	def receive_message(self, data,peerlist):
		notfull=len(peerlist)-len(self.messagebox)
		if notfull:
			content=data.split()
			m=Message(finduser(content[2],peerlist), ' '.join(content[6:]),int(content[4]))
			for message in self.messagebox:
				if message.sender==m.sender:
					return
			self.messagebox.append(m)
	
	def receive_result(self, data, peerlist):
		notfull = count_active(peerlist)-len(self.results)
		if notfull:
			content=data.split()
			r=Message(finduser(content[2],peerlist), content[-1], int(content[-3]))
			for result in self.results:
				if result.sender==r.sender:
					return
			self.results.append(r)
			if notfull==1:
				winner=finduser(self.calcul_winner(),peerlist)
				if winner.is_active:
					print('winner:',winner.username)
					self.save(winner)
					self.clear_all()
					winner.disconnect()
				
	
	def calcul_winner(self):
		dic={}
		for result in self.results:
			if result.body in dic:
				dic[result.body]+=1
			else:
				dic[result.body]=1
		
		for result in dic:
			#print(0.5*len(self.results))
			#print(dic[result])
			if dic[result]>0.5*len(self.results):
				self.pref=result
				#print('winner:',result)
				return result
		return None
		
	def save(self,  winner):
		d=os.getcwd()
		current_round=self.get_current_round()
		path=d+'/'+self.username
		os.chdir(path)
		f = open('registre.txt', 'a') 
		#print('messagebox len',len(self.messagebox))
		for message in self.messagebox:
			if message.sender==winner:
			
				text_to_write = "\n" + str(message.sender.username) + " a gagne le tournoi! Son message est : " + str(message.body) + "\n" + "Fin du tournoi numero " + str(current_round) + "\n"
				print('text to write:',text_to_write)
				bid=None
				f.write(text_to_write)
				#sql librairie
				f.close()
				os.chdir(d)
		self.bid=None
				
	
	def get_current_round(self):
		current_dir=os.getcwd()
		d=current_dir+'/'+self.username
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

def finduser(name, peerlist):
	for peer in peerlist:
		if name==peer.username:
			return peer
	return None
			
#Creat Liste
Peer_list=[]
a=Peer(50001, 'a', Peer_list , True)
b=Peer(50002 , 'b' , Peer_list , True)
c=Peer(50003, 'c' , Peer_list , True)


if __name__ == '__main__':
	#initialisation pour la premiere foi
	d=os.getcwd()
	for peer in Peer_list:
		path=d+'/'+peer.username
		if not os.path.exists(path):
			os.makedirs(path)
			os.chdir(path)
			f=open('registre.txt','w')
			f.close()
			os.chdir(d)
	
	#login
	flag=1
	while flag==1:
		nom=input('entrez votre nom s''il vous plait:\n')
		user=finduser(nom, Peer_list)
		if user==None:
			choix=input('identifiant inconnu, inscrire? y/n:\n')
			if choix=='y':
				#################inscrire
				print('faut inscrire')
				flag=0
			else:
				print('reessayer s''il vous plait')
		else:
			flag=0
			user.is_active=True
			user.print_peer()
	print('bienvenu',nom)
	time.sleep(4)
	
	user.receive(Peer_list)
	
	#print(alice.is_active)			

	
	
	
