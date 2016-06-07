import time
import pickle
import random

def tournoi(bids, messages, peer_list):
    round_courant = bids[0].round_courant
    print ("Round courant: ", round_courant)
    print('bids',bids)
    n = len(bids) 
    soma = 0
    for bid in bids:
        soma += int(bid.body)
        print ("Joueur", bid.sender.username, "a choisi le chiffre ", bid.body )
    gagnant = soma % n
    print ("Somme totale = ", gagnant)
    i = 0
    j = 0
    arreter = False
    while not arreter:
        peer = peer_list[j]
        j += 1
        if peer.active:
            vainqueur = peer
            i = i+1
            if i>gagnant:
                arreter = True
    message_vainqueur = messages[gagnant]
    print(vainqueur.username, "a gagné le tournoi! Son message est: ", message_vainqueur)
    enregistrer_tournoi("message_log.txt", vainqueur.username, message_vainqueur, round_courant)
    return

def enregistrer_tournoi(archive, username, message, round_courant):
	f = open(archive, 'a')
	try:
		text_to_write = "\n" + str(username) + " a gagne le tournoi! Son message a été : " + str(message) + "\n" + "Fin du tournoi numero " + str(round_courant) + "\n"
		f.write(text_to_write)
	finally:
		f.close()
		return;
		
def lire_tournoi_courant(archive):
	f = open(archive, 'r')
	try:
		content = f.readlines()
		for line in content:
			if line == "\n":
				content.remove(line)
		n = len(content)
		ligne = content[n-1]
		ligne = ligne.split()
		index = len(ligne) - 1
		tournoi_courant = int(ligne[index]) + 1
	finally:
		f.close()
	return tournoi_courant

def validation (peer_list):
	#principe: majorite simple(51%)
	#toutes les chiffres seront valides
	for peer_cible in peer_list:
		liste_choix = []
		dico = {}
		for peer_testeur in peer_list:
			for bid in peer_testeur.bids_courants:
				if bid.sender.username == peer_cible.username:
					liste_choix.append(bid.body)
		#trouver element majoritaire dans la liste
		for chiffre in liste_choix:
			if chiffre in dico:
				dico[chiffre] += 1
			else :
				dico[chiffre] = 1
		mult = 0
		maj = -1
		for chiffre in dico:
			if dico[chiffre]>mult:
				maj = chiffre
				mult = dico[chiffre]
		for peer in peer_list:
			for bid in peer.bids_courants:
				round_courant = bid.round_courant
				if bid.sender == peer_cible:
					peer.bids_courants.remove(bid)
					bid_valide = Message(peer_cible, maj, round_courant, True)
					peer.bids_courants.append(bid_valide)

def random_client_generator(peer_list, nb_clients):
	values = "abcdefghijklmnopqrstuvwxyz"
	for i in range(nb_clients):
		
		#generate id
		parte_1 = (random.randint(0, 255))
		parte_2 = (random.randint(0, 255))
		parte_3 = (random.randint(0, 255))
		parte_4 = (random.randint(0, 255))
		peer_id = str(parte_1) + '.' + str(parte_2) + '.' + str(parte_3) + '.' + str(parte_4)
		
		#generate username
		size = (random.randint(7,12))
		username = ''
		for a in range(size):
			username = username + str(random.choice(values))
			
		#active or not active?
		active = bool(random.getrandbits(1))
		
		peer = Peer(peer_id, username, peer_list, active)
	return peer_list

def load_peers():
	peer_list = []
	with open('peers.pk1', 'rb') as input:
		nb_objects = pickle.load(input)
		for i in range(nb_objects):
			peer = pickle.load(input)
			peer_list.append(peer)
	return peer_list;

class Peer:
			
	def __init__(self, ip_add, username, peer_list, active=False):
		self.ip_add = ip_add
		self.username = username
		self.active = active
		self.index = len(peer_list)
		self.messageBox = []
		self.bids_courants = []
		peer_list.append(self)
		return;
		
	def random_bid_generator(self, bids, round_courant, peer_list):
		size = 0
		z = -1
		for peer in peer_list:
			if peer.active:
				size += 1
		for peer in peer_list:
			if peer.active:
				z += 1
				if peer != self:
					num = random.randint(0, size-1)
					bid = Message(peer, num, round_courant, True)
					peer.bids_courants.append(bid)
					bids[z] = bid		
		return bids
		
	def clear_bids_courants(self):
		for bid in self.bids_courants:
			a = self.bids_courants.remove(bid)
		return;
										
			
	def lire_chiffres (self, peer_list):
		# recevoir les chiffres de tout le monde
		for peer_1 in peer_list:
			if peer_1 != self:
				for bid in peer_1.bids_courants:
					if bid.sender == peer_1:
						self.bids_courants.append(bid)	
		
	def random_message_generator(self, messages, peer_list):
		values = "abcdefghijklmnopqrstuvwxyz"
		values_maj = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		choices = ["Bonjour", "J'ai gagne, je suis trop fort", "Batatinha quando nasce",
		"Pouca criatividade", "Aupa Atleti!", "Salut tout le monde", "Wesh", "C'est bon le macarron"]
		z = -1
		for peer in peer_list:
			if peer.active:
				z += 1
				if peer != self:
					num_mots = random.randint(2, 8)
					mess = ''
					for i in range(num_mots):
						taille_mot = random.randint(2, 8)
						if i == 0:
							mess += str(random.choice(values_maj))
							taille_mot -= 1
						for j in range(taille_mot):
							mess += str(random.choice(values))
						if i == num_mots-1:
							mess+= '.'
						mess += ' ' 
					messages[z] = random.choice(choices)
		return messages
		
	def print_user(self):
		if self.active == True:			
			print ("User " + self.username + ", IP: " + self.ip_add + ", index " + str(self.index) + " is active" )
		else:
			print ("User " + self.username + ", IP: " + self.ip_add + ", index " + str(self.index) +  " is not active" )
		return;
		
	def print_bids_courants(self):
		print("Liste de ", self.username, "\n")
		for bid in self.bids_courants:
			print ("User:", bid.sender.username, "bid:", bid.body, "in round", bid.round_courant)
			
			

	def send_message(self, peer, body, round_courant):
		m = self.Message(self, body, round_courant)
		peer.messageBox.append(m)
		return;
		
		
	def print_message_box(self):
		print ("\nBoite de messages de " + self.username + "\n")
		for message in self.messageBox:
			message.print_message()
		return;
		
	def save_peers(self, peer_list):
		with open('peers.pk1', 'wb') as output:
			pickle.dump(len(peer_list), output, -1)
			for peer in peer_list:
				pickle.dump(peer, output, -1)
		return;
						
	def run_client(self, peer_list):
		self.active = True
		continuer = True
		while continuer:
			round_courant = lire_tournoi_courant("message_log.txt")
			print ("Bienvenue, utilisateur", self.username, "!")
			
			#get status of peers (comme il n'y a pas de réseau on le simule avec une fonction aléatoire)
			for peer in peer_list:
				peer.clear_bids_courants()
				if peer != self:
					status = bool(random.getrandbits(1))
					peer.active = status
					
			n = -1
			for peer in peer_list:
				if peer.active==True:
					n += 1
			text = 	'--> Saisissez un entier entre 0 et ' + str(n) + ': '	
			num = int(input(text))
			
			message = str(input('--> Saisissez le message desiré: '))
			messages = []
			bids = []
			z = -1
			for peer in peer_list:
				if peer.active:
					z += 1
					messages.append(0)
					bids.append(0)
					if peer == self:
						messages[z] = message
						bid = Message(self, num, round_courant, True)
						bids[z] = bid
						self.bids_courants.append(bid)
			
			bids = self.random_bid_generator(bids, round_courant, peer_list)
			
			#tout le monde lit les chiffres de tout le monde
			
			for peer in peer_list:
				peer.lire_chiffres(peer_list)
			
			"""for peer in peer_list:
				peer.print_bids_courants()"""
				
			#fonction qui resout le consensus!!
			validation(peer_list)
			
			"""for peer in peer_list:
				peer.print_bids_courants()"""
				
			messages = self.random_message_generator(messages, peer_list)
			
			tournoi(bids, messages, peer_list)
			
			for peer in peer_list:
				peer.clear_bids_courants()
				
			choix = input("--> Tournoi fini! Vous desirez continuer? Tapez 'y' pour oui, et 'n pour non'")
			if choix == 'y':
				continuer = True
			else :
				continuer = False
				
		print ("Merci pour participer. A la prochaine!")
		return;			
				
class Message:
	def __init__(self, sender, body, round_courant, chiffre = False):
		self.sender = sender
		self.chiffre = chiffre
		self.body = body
		self.round_courant = round_courant
			
	def print_message(self):
		sender_username = self.sender.username
		if not self.chiffre:
			print ("Message from " + str(sender_username) + " (envoyee au round " + str(self.round_courant) + ") :\n" + str(self.body) + "\n")
				

if __name__ == '__main__':
	peer_list = load_peers()
	peer_list[0].run_client(peer_list)
		


