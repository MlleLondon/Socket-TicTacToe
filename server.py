import pygame
from grid import Grid #Classe de gestion de la grille du jeu
import os
#Importation gestion du réseau (socket)
import socket
#Importation de la gestion de threads
import threading

#Fonction pour créer un thread
def create_thread(target):
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()


#Définition de l'adresse et du port pour la connexion
HOST = socket.gethostbyname(socket.gethostname()) #Adresse IP locale dynamique
PORT = 65432 #Port d'écoute

ADDR = (HOST,PORT)
connection_established = False
conn , addr = None, None

#Création socket pour l'écoute des connexions
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.bind(ADDR) #Associer le socket à l'adresse et le port
except socket.error as e:
    print(str(e)) #Gestion de l'erreur
    
#Préparation écoute (1 connexion max en attente)
sock.listen(1)

#Recevoir les données de l'autre joueur
def receive_data():
    global turn, grid, player
    while True:
        #Reception
        data = conn.recv(1024).decode()
        data = data.split("-")
        x , y = int(data[0]) , int(data[1]) #Coordonnées du coup récupéré
        #Mise à jour du tour
        if data[2] == "yourturn":
            turn = True
        #Vérification si la partie est finie + gestion du gagnant
        if data[3]  == "False":
            if data[4] == "None":
                grid.winner = None
            else:
                grid.winner = data[4]
            grid.game_over = True 
        #Mise à jour de la grille avec le coup de l'adversaire
        if grid.get_cell_value(x, y) == 0:
            grid.set_cell_value(x, y, "O")

        print(data) #Affiche les données reçues (cmd)


#Position de la fenetre sur l'écran
os.environ['SDL_VIDEO_WINDOW_POS'] = "500, 150"

#Dimensions
width = 600
height = 600

#Création de la fenêtre de jeu avec Pygame
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tic-tac-toe")
programIcon = pygame.image.load('images/icon_tic_tac_toe.png')
pygame.display.set_icon(programIcon)

#Variables initiales
running = True
player = "X"
turn = True
playing = "True"
grid = Grid()  #Création de l'objet de la grille 
clock = pygame.time.Clock() #Gestion du rafraichissement

#Attendre une connexion
def waiting_for_connection():
    global conn, addr, connection_established, grid

    print("Waiting for connection....")
    grid.waiting_for_conn = True #Indique que le serveur attend qu'une personne rejoigne
    
    #Accepte une connexion client (bloque le thread en attendant)
    conn , addr = sock.accept()
    print("Joueur connecté !!!")

    #Mise à jour de l'état de connexion
    grid.waiting_for_conn = False
    connection_established = True

    #Début de la reception des données
    receive_data()

#Créer un thread pour attendre la connexion du client
create_thread(waiting_for_connection)

# Fonction pour dessiner du texte sur la fenêtre
def draw_text(surface, text, pos, font_size=24, color=(255, 255, 255)):
    font = pygame.font.Font(None, font_size)  # Police par défaut
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)


def main() :
    global running, turn, grid, player, playing, clock

    while running: 
        clock.tick(60) #60 fps

        #Mise à jour de l'état de la grille
        if turn and not(grid.game_over):
            grid.waiting_for_move = False
        elif ((not turn) and not(grid.game_over)):
            grid.waiting_for_move = True

        #Boucle pour gérer les événements de Pygame 
        for event in pygame.event.get():

            #Gestion de la fermeture de fenêtre
            if event.type == pygame.QUIT:
                running = False
            #Clique de souris
            if event.type == pygame.MOUSEBUTTONDOWN and (not grid.game_over) and connection_established:
                if pygame.mouse.get_pressed()[0]: #Clique gauche
                    if turn and not(grid.game_over):

                        pos = pygame.mouse.get_pos() #Position du clic
                        Cell_X, Cell_Y = pos[0]//200, pos[1]//200 #Convertir le clic en position dans la grille

                        #Vérification cellule vide
                        if grid.get_cell_value(Cell_X,Cell_Y) == 0:
                            grid.get_mouse(Cell_X, Cell_Y, player) #Mise à jour de la grille avec le symbole du joueur
                            if grid.game_over:
                                playing  = "False"
                            #Envoi des données au serveur
                            send_data = "{}-{}-{}-{}-{}".format(Cell_X, Cell_Y, 'yourturn', playing, str(grid.winner)).encode()
                            conn.send(send_data)

                            turn = False #Changement de joueur

            #Gestion touches de clavier
            if event.type == pygame.KEYDOWN:
                #Relancer une partie (touche espace)
                if event.key == pygame.K_SPACE and grid.game_over:                     
                    grid.clear_grid()
                    player = "X"
                    grid.game_over = False
                    playing = "True"
                #Echap pour quitter le jeu
                elif event.key == pygame.K_ESCAPE:
                    running = False


        #Dessine la grille et rafraîchit l'affichage
        grid.draw(win)
         # Ajouter l'adresse IP sur l'écran
        draw_text(win, f"IP: {HOST}:{PORT}", (10, 10), font_size=30, color=(255, 255, 255))
        pygame.display.flip()

main()
