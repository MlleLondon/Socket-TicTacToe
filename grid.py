import pygame
import os 

pygame.init() #Initialiser pygame

#Chargement des images comme objets Python
x_img = pygame.image.load(os.path.join("images","the-letter-x.png")) 
o_img = pygame.image.load(os.path.join("images","the-letter-o.png")) 
#Redimenssionner les images
x_img = pygame.transform.scale(x_img, (200, 200)) 
o_img = pygame.transform.scale(o_img, (200, 200)) 
   
#Gestion grille du jeu
class Grid:
    def __init__(self):
        self.grid_lines = [((0,200), (600,200)), #1ere ligne horizontale
                        ((0,400), (600,400)),   #2e ligne horizontale
                        ((200,0), (200,600)),   #1ere ligne verticale
                        ((400,0), (400,600))]   #2e ligne verticale
        #Initialisation à vide de la grille
        self.grid = [[0,0,0]
                    ,[0,0,0]
                    ,[0,0,0]]

        #Variables pour gérer l'état du jeu
        self.switch_player = True
        #Recherche direction N        NW      W       SW     ...
        self.search_dir = [(0,-1) ,(-1,-1), (-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1)]
        
        self.waiting_for_conn = False #Indication si le serveur attend une connexion

        self.waiting_for_move = None #Indique si le joueur attend le coup de l'adversaire

        self.game_over = False #Etat de fin de jeu

        self.winner = None  #Indication vainqueur de la partie (None si égalité)
        
    #Méthode pour dessiner la grille et afficher l'état de la partie
    def draw(self, win):
        if self.waiting_for_conn:
            #Si le serveur attend un joueur
            font = pygame.font.Font("Fonts/Nunito-Black.ttf", 50)
            text = font.render("En attente de joueur...", True, (47, 54, 64))
            win.fill((9, 132, 227, 1.0)) #Couleur de fond
            win.blit(text, (60, 240))
        else:
            win.fill((9, 132, 227,1.0)) #Couleur de fond

            #Déssine les lignes de la grille
            for line in self.grid_lines:
                pygame.draw.line(win, (255,255,255), line[0], line[1], 2)

            #Déssine les symboles X et O dans les cases correspondantes
            for y in range(len(self.grid)):
                for x in range(len(self.grid[y])):
                    if self.get_cell_value(x,y) == "X":
                        win.blit(x_img, (x*200, y*200))
                    elif self.get_cell_value(x,y) == "O":
                        win.blit(o_img, (x*200, y*200))
            
            #Afficher un message si c'est le tour de l'adversaire
            if self.waiting_for_move:
                font = pygame.font.Font("Fonts/Nunito-SemiBold.ttf", 40)
                text = font.render("Tour adverse !", True, (47, 54, 64), (9, 132, 227))
                text.set_alpha(255)
                win.blit(text, ((600/2 - 150), (600/2- 50)))

            #Affiche le gagnant si la partie est finie
            if self.game_over:
                font = pygame.font.Font("Fonts/Nunito-Black.ttf", 60)
                win.fill((9, 132, 227, 1.0))
                if self.winner != None:
                    text = font.render("{} a gagné !".format(self.winner), True, (47, 54, 64))
                    win.blit(text, (35, 250))
                else:
                    text = font.render("Egalité !", True, (47, 54, 64))
                    win.blit(text, (210, 250))
        
    #Imprimer la grille dans le cmd
    def print_grid(self):
        for row in self.grid:
            print(row)

    #Obtenir la valeur d'une cellule
    def get_cell_value(self ,x ,y):
        return self.grid[y][x]

    #Définir la valleur d'une cellule
    def set_cell_value(self ,x ,y, value):
        self.grid[y][x] = value

    #Méthode gérer le clic de la souris sur une case de la grille
    def get_mouse(self, x, y, player):
        if self.get_cell_value(x, y) == 0:
            self.set_cell_value(x, y, player)
            self.check_grid(x, y, player)

    #Vérification - hors du terrain
    def is_within_bound(self, x, y):
        return x >= 0 and x < 3 and y>= 0 and y < 3

    #Vérifie si un joueur a gagné
    def check_grid(self,x,y,player):    
        count = 1
        for index, (dirx, diry) in enumerate(self.search_dir):
            if self.is_within_bound(x+dirx, y+diry) and self.get_cell_value(x+dirx , y+diry) == player:
                count += 1
                xx = x + dirx
                yy = y + diry
                if self.is_within_bound(xx+dirx, yy+diry) and self.get_cell_value(xx+dirx, yy+diry) == player:
                    count += 1
                    if count == 3:
                        break
                
                if count < 3:
                    new_dir = 0
                # now we need to reverse the direction or else we can count 3 cells but they might not be a row or a column
                    if index == 0:
                        new_dir = self.search_dir[4] # N to S
                    elif index == 1:
                        new_dir = self.search_dir[5] # NW to SE
                    elif index == 2:
                        new_dir = self.search_dir[6] # W to E
                    elif index == 3:
                        new_dir = self.search_dir[7] # SW to NE
                    elif index == 4:
                        new_dir = self.search_dir[0] # S to N
                    elif index == 5:
                        new_dir = self.search_dir[1] # SE to NW
                    elif index == 6:
                        new_dir = self.search_dir[2] # E to W
                    elif index == 7:
                        new_dir = self.search_dir[3] # NE to SW
                    
                    if self.is_within_bound(x + new_dir[0], y + new_dir[1]) and self.get_cell_value(x + new_dir[0], y + new_dir[1]) == player:
                        count += 1
                        if count == 3:
                            break
                    else:
                        count = 1
        #Si 3 symboles alignés, le joueur gagne
        if count == 3:
            print(player, "gagne !!!")
            self.winner = player
            self.game_over = True
        #Egalité
        else:
            self.winner = None
            self.game_over = self.is_grid_full()

    #Si la grille est remplie
    def is_grid_full(self):
        for row in self.grid:
            for value in row:
                if value == 0:
                    return False
        return True

    #Vide la grille pour jouer une nouvelle partie
    def clear_grid(self):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                self.set_cell_value(x, y , 0)
