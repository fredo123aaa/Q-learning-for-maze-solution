import os
import random
import pygame
import numpy as np

class Player(object):
    def __init__(self,x,y):
        self.rect = pygame.Rect(x, y, 16, 16)

    def move(self, dx, dy):
        # Mueva cada eje por separado. Tenga en cuenta que esto verifica las colisiones en ambas ocasiones.
        if (dx != 0):
            self.move_single_axis(dx, 0)
        if (dy != 0):
            self.move_single_axis(0, dy)

    def move_single_axis(self, dx, dy):
        # Mueve la recto
        self.rect.x += dx
        self.rect.y += dy

        # Si chocas con una pared, muévete según la velocidad.
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0: # Moving right; Hit the left side of the wall
                    self.rect.right = wall.rect.left
                if dx < 0: # Moving left; Hit the right side of the wall
                    self.rect.left = wall.rect.right
                if dy > 0: # Moving down; Hit the top side of the wall
                    self.rect.bottom = wall.rect.top
                if dy < 0: # Moving up; Hit the bottom side of the wall
                    self.rect.top = wall.rect.bottom

# Buena clase para sostener una pared recta
class Wall(object):
    def __init__(self, pos):
        walls.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], 16, 16)

def arraymax(array):
    maximo=np.max(array)
    a=[]
    for i in range(len(array)):
        if (array[i]==maximo):
            a.append(i)
    return a

# Initialise pygame
os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()

# Set up the display
pygame.display.set_caption("Get to the red square!")
screen = pygame.display.set_mode((320, 240))

clock = pygame.time.Clock()
walls = [] # List to hold the walls
#player = Player() # Create the player

# Holds the level layout in a list of strings.
level = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W                  W",
    "W         WWWWWW   W",
    "W   WWWW       W   W",
    "W   W        WWWW  W",
    "W WWW  WWWW        W",
    "W   W     W W      W",
    "W   W     W   WWW WW",
    "W   WWW WWW   W W  W",
    "W     W   W   W W  W",
    "WWW   W   WWWWW W  W",
    "W W      WW        W",
    "W W   WWWW   WWW   W",
    "W     W    E   W   W",
    "WWWWWWWWWWWWWWWWWWWW",
]

# Parse the level string above. W = wall, E = exit
x = y = 0
for row in level:
    for col in row:
        if col == "W":
            Wall((x, y))
        if col == "E":
            end_rect = pygame.Rect(x, y, 16, 16)
        x += 16
    y += 16
    x = 0
# Define los posibles estados y acciones
states = []
for i in range(len(level)):
    for j in range(len(level[0])):
        if level[i][j] != "W":
            states.append((j*16, i*16))
actions = ["UP", "DOWN", "LEFT", "RIGHT"]

# Define la función de recompensa
def reward(state, action):
    if state == end_rect.topleft:
        return 100
    return -1

# Define la matriz de transición de estado-acción
transitions = np.zeros((len(states), len(actions)))
for i, state in enumerate(states):
    for j, action in enumerate(actions):
        x, y = state
        if action == "UP":
            if (x, y-16) in states:
                transitions[i][j] = states.index((x, y-16))
            else:
                transitions[i][j] = states.index(state)
        elif action == "DOWN":
            if (x, y+16) in states:
                transitions[i][j] = states.index((x , y+16))
            else:
                transitions[i][j] = states.index(state)
        elif action == "LEFT":
            if (x-16, y) in states:
                transitions[i][j] = states.index((x-16,y))
            else:
                transitions[i][j] = states.index(state)
        elif action == "RIGHT":
            if (x+16, y) in states:
                transitions[i][j] = states.index((x+16, y))
            else:
                transitions[i][j] = states.index(state)

# Inicializa la matriz Q
Q = np.zeros((len(states), len(actions)))

# Define la tasa de aprendizaje
alpha = 0.1

# Define el factor de descuento
gamma = 0.99

# Define el número de episodios a ejecutar
n_episodes = 1000

#variable para la estadística
k=0
errores=0

# Ejecuta el proceso de aprendizaje por refuerzo
for episode in range(n_episodes):
    # Selecciona un estado inicial al azar
    #current_state = random.choice(states)
    current_state=(48,176)

    player = Player(current_state[0],current_state[1])  # creamos el jugador
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False

        # Selecciona una acción al azar en base a lo aprendido
        current_action = actions[random.choice(arraymax(Q[states.index(current_state),:]))]
        #current_action=random.choice(actions)

        #Se mueve el jugador
        if current_action=="LEFT":
            player.move(-16, 0)
        if current_action=="RIGHT":
            player.move(16, 0)
        if current_action=="UP":
            player.move(0, -16)
        if current_action=="DOWN":
            player.move(0, 16)

        # Draw the scene
        screen.fill((0, 0, 0))
        for wall in walls:
            pygame.draw.rect(screen, (255, 255, 255), wall.rect)
        pygame.draw.rect(screen, (255, 0, 0), end_rect)
        pygame.draw.rect(screen, (255, 200, 0), player.rect)
        pygame.display.flip()

        # Actualiza la matriz Q
        Q[states.index(current_state)][actions.index(current_action)] = (1 - alpha) * Q[states.index(current_state)][actions.index(current_action)] + alpha * (reward(states[int(transitions[states.index(current_state)][actions.index(current_action)])], current_action) + gamma * np.max(Q[int(transitions[states.index(current_state)][actions.index(current_action)]), :]))

        # Actualiza el estado actual
        current_state = states[int(transitions[states.index(current_state)][actions.index(current_action)])]

        #Aumentar el valor del numero de errores:
        errores+=1

        # Verifica si se ha alcanzado el estado final
        if current_state == end_rect.topleft:
            break
        #pygame.time.delay(10)

    if (episode+1)%10==0:
        k+=1
        print("promedio de pasos para el destino en la "+str(k)+"° decena de episodios:\t"+str(errores/10))
        errores=0

current_state = (48,176)

player = Player(current_state[0],current_state[1])  # creamos el jugador
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            running = False

    # Selecciona una acción al azar en base a lo aprendido

    current_action = actions[random.choice(arraymax(Q[states.index(current_state),:]))]


    #Se mueve el jugador
    if current_action=="LEFT":
        player.move(-16, 0)
    if current_action=="RIGHT":
        player.move(16, 0)
    if current_action=="UP":
        player.move(0, -16)
    if current_action=="DOWN":
        player.move(0, 16)

    # Draw the scene
    screen.fill((0, 0, 0))
    for wall in walls:
        pygame.draw.rect(screen, (255, 255, 255), wall.rect)
    pygame.draw.rect(screen, (255, 0, 0), end_rect)
    pygame.draw.rect(screen, (255, 200, 0), player.rect)
    pygame.display.flip()

        # Actualiza la matriz Q
    Q[states.index(current_state)][actions.index(current_action)] = (1 - alpha) * Q[states.index(current_state)][actions.index(current_action)] + alpha * (reward(states[int(transitions[states.index(current_state)][actions.index(current_action)])], current_action) + gamma * np.max(Q[int(transitions[states.index(current_state)][actions.index(current_action)]), :]))

        # Actualiza el estado actual
    current_state = states[int(transitions[states.index(current_state)][actions.index(current_action)])]

        # Verifica si se ha alcanzado el estado final
    if current_state == end_rect.topleft:
        break
    pygame.time.delay(500)

pygame.quit()
# Selecciona la mejor acción para cada estado
#best_actions = []
#for state in states:
#    best_actions.append(actions[np.argmax(Q[states.index(state), :])])

# Ejecuta el proceso de aprendizaje por refuerzo
#current_state = (32, 32)
#while current_state != end_rect.topleft:
    # Selecciona la mejor acción para el estado actual
#   current_action = best_actions[states.index(current_state)]
    # Actualiza el estado actual
#    current_state = states[int(transitions[states.index(current_state)][actions.index(current_action)])]

# Imprime la solución encontrada
#print("Solución encontrada:")
#for i, row in enumerate(level):
#    for j, col in enumerate(row):
#        if (i, j) == current_state:
#            print("E", end="")
#        elif (i, j) in states:
#            print(best_actions[states.index((i, j))][0], end="")
#        else:
#            print(col, end="")
#    print()