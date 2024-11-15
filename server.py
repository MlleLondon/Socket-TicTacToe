import pygame
from grid import Grid
import os
import socket
from thread_util import create_thread  # Import de la fonction de gestion des threads

class TicTacToeServer:
    def __init__(self, width=600, height=600):
        # Initialisation réseau
        self.HOST = socket.gethostbyname(socket.gethostname())
        self.PORT = 65432
        self.ADDR = (self.HOST, self.PORT)
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn, self.addr = None, None
        self.connection_established = False
        
        # Initialisation de la fenêtre Pygame
        self.width = width
        self.height = height
        os.environ['SDL_VIDEO_WINDOW_POS'] = "500, 150"
        pygame.init()
        
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tic-tac-toe")
        programIcon = pygame.image.load('images/icon_tic_tac_toe.png')
        pygame.display.set_icon(programIcon)
        
        # Variables de jeu
        self.running = True
        self.player = "X"
        self.turn = True
        self.playing = "True"
        self.grid = Grid()
        self.clock = pygame.time.Clock()

        # Bind du socket
        try:
            self.sock.bind(self.ADDR)
        except socket.error as e:
            print(str(e))

        self.sock.listen(1)  # Écoute d'une connexion

    def waiting_for_connection(self):
        print("Waiting for connection....")
        self.grid.waiting_for_conn = True

        # Accepte une connexion client
        self.conn, self.addr = self.sock.accept()
        print("Joueur connecté !!!")
        
        # Mise à jour de l'état de connexion
        self.grid.waiting_for_conn = False
        self.connection_established = True
        
        # Début de la réception des données
        self.receive_data()

    def receive_data(self):
        while True:
            data = self.conn.recv(1024).decode()
            data = data.split("-")
            x, y = int(data[0]), int(data[1])
            if data[2] == "yourturn":
                self.turn = True
            if data[3] == "False":
                self.grid.winner = None if data[4] == "None" else data[4]
                self.grid.game_over = True
            if self.grid.get_cell_value(x, y) == 0:
                self.grid.set_cell_value(x, y, "O")
            print(data)

    def draw_text(self, text, pos, font_size=24, color=(255, 255, 255)):
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        self.win.blit(text_surface, pos)

    def run(self):
        create_thread(self.waiting_for_connection)  # Utilisation de la fonction externe

        while self.running:
            self.clock.tick(60)

            if self.turn and not self.grid.game_over:
                self.grid.waiting_for_move = False
            elif (not self.turn) and not self.grid.game_over:
                self.grid.waiting_for_move = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN and not self.grid.game_over and self.connection_established:
                    if pygame.mouse.get_pressed()[0]:  # Left click
                        if self.turn and not self.grid.game_over:
                            pos = pygame.mouse.get_pos()
                            cell_x, cell_y = pos[0] // 200, pos[1] // 200
                            if self.grid.get_cell_value(cell_x, cell_y) == 0:
                                self.grid.get_mouse(cell_x, cell_y, self.player)
                                if self.grid.game_over:
                                    self.playing = "False"
                                send_data = "{}-{}-{}-{}-{}".format(cell_x, cell_y, 'yourturn', self.playing, str(self.grid.winner)).encode()
                                self.conn.send(send_data)
                                self.turn = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.grid.game_over:
                        self.grid.clear_grid()
                        self.player = "X"
                        self.grid.game_over = False
                        self.playing = "True"
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

            self.grid.draw(self.win)
            self.draw_text(f"IP: {self.HOST}:{self.PORT}", (10, 10), font_size=30, color=(255, 255, 255))
            pygame.display.flip()
