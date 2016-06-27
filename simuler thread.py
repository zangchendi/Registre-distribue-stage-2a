
#author @chendi ZANG
import random
import os, time
import tkinter
import threading

class Message:
	def __init__(self, sender, body, current_round, chiffre = False):
		self.sender = sender
		self.chiffre = chiffre
		self.body = body
		self.current_round=current_round
	
	def print_chiffre(self):
		if self.chiffre:
			print("bid from " + str(self.sender.username) +  " for round "+str(self.current_round)+" :\n" + str(self.body) + "\n")
			
	def print_message(self):
		if not self.chiffre:
			print ("Message from " + str(self.sender.username) +" for round "+str(self.current_round) + " :\n" + str(self.body) + "\n")
			
			
class Peer:
			
	def __init__(self, ip_add, username, peer_list, active=False):
		self.username = username
		self.active = active
		self.index = len(peer_list)
		self.messageBox = []
		self.bids_current = []
		self.results_current=[]
		self.pref=None
		self.ip_add=ip_add
		peer_list.append(self)
		return
		
	def disconnect(self):
		self.active=False
		
	def print_peer(self):
		print('name=',self.username,'  ip=', self.ip_add,' index=', self.index, 'is active:' , self.active)
	
	def print_message_box(self):
		print('messageBox=')
		for message in self.messageBox:
			message.print_message()
	
	def clear_message_box(self):
		self.messageBox=[]
		return 0;
	
		
	def random_bid_generator(self, bids, peer_list,round_current ):
		if self.active:
			size=count_active(peer_list)
			num = random.randint(0, size-1)
			bid = Message(self, num, round_current, True)
			self.bids_current.append(bid)
			bids.append(bid) 		
			time.sleep(2)
		return bids
	
	def random_message_generator(self):
		message='salut, je suis '+self.username
		return message
		
	def input_bid(self, bids, peer_list, round_current):
		if self.active:
			num = int(input('--> Saisissez un entier entre 0 et ' + str(count_active(peer_list)-1) + ': '	))
			bid = Message(self, num, round_current, True)
			self.bids_current.append(bid)
			bids.append(bid)
		return bids
	
	def input_bid_interface(self, bids, peer_list,round_current):
		if self.active:
			root = tkinter.Tk() 
			ent = tkinter.Entry(root) 
			txt='--> Saisissez un entier entre 0 et ' + str(count_active(peer_list)-1) + ': '
			ent.insert(0, txt)                # set text 
			ent.pack(side=tkinter.TOP, fill=tkinter.X)         # grow horiz
			ent.focus()                                        # save a click 
			ent.bind('<Return>', (lambda event: fetch()))      # on enter key 
			btn = tkinter.Button(root, text='Fetch', command=fetch)    # and on button 
			btn.pack(side=tkinter.LEFT) 
			num=int(ent.get())
			root.mainloop()
			
			bid = Message(self, num, round_current, True)
			self.bids_current.append(bid)
			bids.append(bid)
		return bids
	def clear_bids_results_current(self):
		self.bids_current=[]
		self.results_current=[]
	
	def send_bid (self, peer_list):#envoyer le bid a tout le monde
		for bid in self.bids_current:
			if bid.sender==self:
				mon_bid=bid
		for peer in peer_list:
			if peer.active and peer!=self:
				peer.bids_current.append(mon_bid)
		return True
	
	def tournoi(self, peer_list):# chacun trouve son propre resultat du gagnant
		n=count_active(peer_list)
		if len(self.bids_current)==n:
			sum=0
			for bid in self.bids_current:
				sum+=bid.body
			index_winner=sum % n
			
			index=-1
			for peer in peer_list:
				if peer.active:
					index+=1
					if index==index_winner:
						self.pref=peer
						self.bids_current=[]
						return peer
	
	def send_result(self, peer_list):
		for peer in peer_list:
			if peer.active:
				peer.results_current.append(self.pref)
		return True
		
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
		
	def input_message(self):
		m=str(input('Congratulations! you win! now you can type in your message: '))
		return m
	
	def send_message(self, m, peer_list):
		message=Message(self, m ,self.get_current_round(),False)
		#message.print_message()
		for peer in peer_list:
			if peer.active:
				peer.messageBox.append(message)
		time.sleep(1)
		return
		
	def read_save(self):
		d=os.getcwd()
		current_round=self.get_current_round()
		path=d+'\\'+self.username
		os.chdir(path)
		f=open('registre.txt' ,'a')
		for message in self.messageBox:
			if message.current_round==current_round and message.sender==self.pref:
				text_to_write = "\n" + str(message.sender.username) + " a gagne le tournoi! Son message est : " + str(message.body) + "\n" + "Fin du tournoi numero " + str(current_round) + "\n"
				#print(text_to_write)
				f.write(text_to_write)
				f.close()
				os.chdir(d)
				return True
		return False
		

def find_user_via_name(username,peer_list):
	for peer in peer_list:
		if peer.username==username:
			return peer
	return None
	
def count_active( peer_list):
	n=0
	for peer in peer_list:
		if peer.active:
			n+=1
	return n

def fetch():
	print('Input => "%s"' % ent.get())
def valider(peer_list):
	##PHASE KING
	n=count_active(peer_list)
	f=int(n/4)            #f=nombre de faulty processors ===> donc f+1 phase
	for k in range(f+1):  #KING
		#round 1
		for peer in peer_list:
			peer.results_list=[]
		for peer in peer_list:
			if peer.active:
				#print(peer.pref.username)
				peer.send_result(peer_list)
		#print('#####################')
		i=-1
		maj=None
		dico={}
		for peer in peer_list:
			if peer.active:
				i+=1
				if i==k: #le roi
					for result in peer.results_current:
						if result in dico:
							dico[result.username]+=1
						else:
							dico[result.username]=1
					for winner in dico:
						if dico[winner]>n/2: #majorite du roi
							maj=find_user_via_name(winner, peer_list)
							peer.pref=maj
					if maj==None:
						maj=peer.pref		#valeur par defaut
						
		for peer in peer_list:
			if peer.active:
				i+=1
				dico={}
				if i!=k:
					for result in peer.results_current:
						if result.username in dico:
							dico[result.username]+=1
						else:
							dico[result.username]=1
					mult=0
					'''print('----------------')
					print(dico)
					print('-----------------')'''
					for winner in dico:
						if dico[winner]>n/2+f: 
							peer.pref=find_user_via_name(winner,peer_list)
							mult=dico[winner]
					if mult==0:
						peer.pref=maj
					'''bob.pref=bob
					moi.pref=bob'''
					
def run(peer, peer_list):
	peer.random_bid_generator(bids,Peer_list,current_round)
	peer.send_bid(peer_list)
	time.sleep(5)
	
	peer.tournoi(peer_list)
	valider(peer_list)

	
def moi_run( peer_list):
	moi.input_bid(bids,Peer_list,current_round)
	moi.send_bid(peer_list)
	time.sleep(5)
	
	moi.tournoi(peer_list)
	valider(peer_list)

					
			
		
			
	
	
	
					
			
				
	
	
				
if __name__ == '__main__':
						
				
	#Creat Liste
	Peer_list=[]
	alice=Peer('1.215.21.16', 'alice', Peer_list , True)
	bob=Peer('255.255.255.19' , 'bob' , Peer_list , True)
	catheline=Peer('255.25.5.19' , 'catheline' , Peer_list , True)
	alphabet='abcdefghijklmnopqrstuvwxyz'
	for i in range(2):
		Peer('1.1.2.4', alphabet[i], Peer_list, True)

#initialise and create the files

	d=os.getcwd()
	for peer in Peer_list:
		path=d+'\\'+peer.username
		if not os.path.exists(path):
			os.makedirs(path)
			os.chdir(path)
			f=open('registre.txt','w')
			f.close()
			os.chdir(d)
			


	bids=[]

#log in	
	print('On a ces identifiants dans la liste:')
	for user in Peer_list:
		user.print_peer()
	
	log=False
	while log==False:
		identifiant=str(input(' Identifiant:'))
		moi=find_user_via_name(identifiant,Peer_list)
		if moi==None:
			print('Identifiant inconnu, Veuillez reessayer')
		else:
			#if moi.active: pour vrai reseau
			txt='Bienvenu '+identifiant+'!'
			print(txt)
			msg=tkinter.Message(text=txt)
			msg.pack()
			tkinter.mainloop()
			moi.active=True
			log=True
	

	while log== True:
	#give the bid for current round
		current_round=moi.get_current_round()
	
		moi.input_bid(bids,Peer_list,current_round)
		#moi.input_bid_interface(bids,Peer_list,current_round)
		
		threads=[]
	#simulate the bid for the others(cause they're machines)
		for peer in Peer_list:
			if peer!=moi:
				#peer.random_bid_generator(bids,Peer_list,current_round)
				t1=threading.Thread(target=peer.random_bid_generator, args=(bids,Peer_list, current_round))
				threads.append(t1)
		for t in threads:
			t.setDaemon(True)
			t.start()
		t.join()
		
		for bid in bids:
			bid.print_chiffre()
		for peer in Peer_list:
			if peer.active:
				#peer.send_bid(Peer_list)
				threading.Thread(target=peer.send_bid, args=(Peer_list,)).start()
	#print(len(bob.bids_current))
		for peer in Peer_list:
			#peer.tournoi(Peer_list)
			threading.Thread(target=peer.tournoi, args=(Peer_list,)).start()
		"""#test faulty or milicious processors
		moi.pref=bob
		bob.pref=bob
		catheline.pref=moi"""
		valider(Peer_list)#phase KIng
		
		
		print(moi.pref.username,'win this tournament')
		
		if moi.pref==moi: # I win
			message=moi.input_message()
		else:
			message=moi.pref.random_message_generator()
			
		#print(message)
		moi.pref.send_message(message,Peer_list)
		print(moi.pref.username,'vous a envoye un message')
			
		#check the message	
		for peer in Peer_list:
			peer.read_save()
			#peer.print_message_box()
		
		print('ce message a ete enregistre dans votre registre')
		for peer in Peer_list:
			peer.clear_bids_results_current()
			peer.pref=None
		
		choice=input('Tournoi fini, vous voulez continuer? typez y pour oui et n pour non: \n ')
		
		if choice=='y':
			log=True
		else:
			log=False
			moi.active=False





	
