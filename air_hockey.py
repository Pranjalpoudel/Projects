import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Game Objects
PADDLE_RADIUS = 30
PUCK_RADIUS = 20
GOAL_WIDTH = 200
WINNING_SCORE = 7
PHYSICS_STEPS = 5

# Setup Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Air Hockey")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 50)
small_font = pygame.font.SysFont("Arial", 30)

class Paddle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = PADDLE_RADIUS
        self.speed = 7
        self.mass = 10

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), self.radius)
        # Add a highlight for 3D effect
        pygame.draw.circle(win, (min(self.color[0]+50, 255), min(self.color[1]+50, 255), min(self.color[2]+50, 255)), (int(self.x - 5), int(self.y - 5)), self.radius // 2)

    def move(self, keys, up, down, left, right, boundary_x_min, boundary_x_max, dt):
        step_speed = self.speed * dt
        if keys[up] and self.y - self.radius > 0:
            self.y -= step_speed
        if keys[down] and self.y + self.radius < HEIGHT:
            self.y += step_speed
        if keys[left] and self.x - self.radius > boundary_x_min:
            self.x -= step_speed
        if keys[right] and self.x + self.radius < boundary_x_max:
            self.x += step_speed

class Puck:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PUCK_RADIUS
        self.x_vel = 0
        self.y_vel = 0
        self.max_speed = 15
        self.friction = 0.998
        self.mass = 5

    def draw(self, win):
        pygame.draw.circle(win, BLACK, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(win, GRAY, (int(self.x), int(self.y)), self.radius - 2)

    def apply_friction(self):
        self.x_vel *= self.friction
        self.y_vel *= self.friction

    def move(self, dt):
        self.x += self.x_vel * dt
        self.y += self.y_vel * dt

        # Wall Collisions
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.y_vel *= -1
        elif self.y + self.radius >= HEIGHT:
            self.y = HEIGHT - self.radius
            self.y_vel *= -1

        if self.x - self.radius <= 0:
            # Check for goal
            if self.y > (HEIGHT - GOAL_WIDTH) // 2 and self.y < (HEIGHT + GOAL_WIDTH) // 2:
                return 2 # Player 2 scored
            self.x = self.radius
            self.x_vel *= -1
        elif self.x + self.radius >= WIDTH:
            # Check for goal
            if self.y > (HEIGHT - GOAL_WIDTH) // 2 and self.y < (HEIGHT + GOAL_WIDTH) // 2:
                return 1 # Player 1 scored
            self.x = WIDTH - self.radius
            self.x_vel *= -1
        
        return 0

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.x_vel = 0
        self.y_vel = 0

def resolve_collision(paddle, puck):
    dx = puck.x - paddle.x
    dy = puck.y - paddle.y
    distance = math.sqrt(dx**2 + dy**2)

    if distance == 0:
        distance = 0.1 # Avoid division by zero, treat as very close

    if distance < paddle.radius + puck.radius:
        # Collision detected
        
        # Normal vector
        nx = dx / distance
        ny = dy / distance

        # Tangent vector
        tx = -ny
        ty = nx

        # Dot Product Tangent
        dpTan1 = paddle.speed * 0 # Simplified paddle velocity assumption for tangent
        dpTan2 = puck.x_vel * tx + puck.y_vel * ty

        # Dot Product Normal
        dpNorm1 = 0 # Paddle is "heavy" and controlled by player, treat as imparting force
        # Better physics: Elastic collision
        # But since paddle is controlled, let's just push the puck away
        
        # Move puck out of collision
        overlap = (paddle.radius + puck.radius) - distance
        puck.x += nx * overlap
        puck.y += ny * overlap

        # Simple bounce logic based on relative position + paddle movement could be complex
        # Let's try a momentum transfer approximation
        
        # Calculate relative velocity
        # We don't track paddle velocity vector explicitly in move(), but we can infer or just add a push
        # A simple way is to reflect the puck velocity along the normal and add some speed
        
        v_dot_n = puck.x_vel * nx + puck.y_vel * ny
        
        # Reflect
        puck.x_vel -= 2 * v_dot_n * nx
        puck.y_vel -= 2 * v_dot_n * ny
        
        # Add a "kick" if the paddle is moving (simplified)
        # For now, just ensure it doesn't get stuck and gains some energy
        puck.x_vel += nx * 2
        puck.y_vel += ny * 2
        
        # Cap speed
        speed = math.sqrt(puck.x_vel**2 + puck.y_vel**2)
        if speed > puck.max_speed:
            puck.x_vel = (puck.x_vel / speed) * puck.max_speed
            puck.y_vel = (puck.y_vel / speed) * puck.max_speed


def draw_board(win):
    win.fill(WHITE)
    
    # Center Line
    pygame.draw.line(win, RED, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 5)
    
    # Center Circle
    pygame.draw.circle(win, RED, (WIDTH // 2, HEIGHT // 2), 100, 5)
    
    # Goals
    pygame.draw.rect(win, GRAY, (0, (HEIGHT - GOAL_WIDTH) // 2, 10, GOAL_WIDTH))
    pygame.draw.rect(win, GRAY, (WIDTH - 10, (HEIGHT - GOAL_WIDTH) // 2, 10, GOAL_WIDTH))

def main():
    run = True
    
    player1 = Paddle(100, HEIGHT // 2, RED)
    player2 = Paddle(WIDTH - 100, HEIGHT // 2, BLUE)
    puck = Puck(WIDTH // 2, HEIGHT // 2)
    
    score1 = 0
    score2 = 0

    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        
        # Physics Sub-stepping
        puck.apply_friction()
        
        goal = 0
        dt = 1.0 / PHYSICS_STEPS
        
        for _ in range(PHYSICS_STEPS):
            # Player 1 Controls (WASD) - Restricted to left half
            player1.move(keys, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, 0, WIDTH // 2, dt)
            
            # Player 2 Controls (Arrows) - Restricted to right half
            player2.move(keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, WIDTH // 2, WIDTH, dt)
            
            # Move Puck
            g = puck.move(dt)
            if g != 0:
                goal = g
                break

            # Collisions
            resolve_collision(player1, puck)
            resolve_collision(player2, puck)
            
        if goal == 1:
            score1 += 1
            puck.reset()
        elif goal == 2:
            score2 += 1
            puck.reset()

        # Drawing
        draw_board(screen)
        
        # Draw Scores
        score_text1 = font.render(str(score1), True, BLACK)
        score_text2 = font.render(str(score2), True, BLACK)
        screen.blit(score_text1, (WIDTH // 4, 20))
        screen.blit(score_text2, (3 * WIDTH // 4, 20))
        
        # Draw Instructions
        inst_text = small_font.render("P1: WASD   P2: Arrows", True, BLACK)
        screen.blit(inst_text, (WIDTH // 2 - inst_text.get_width() // 2, HEIGHT - 40))

        player1.draw(screen)
        player2.draw(screen)
        puck.draw(screen)
        
        # Check for winner
        winner_text = ""
        if score1 >= WINNING_SCORE:
            winner_text = "Player 1 Wins!"
        elif score2 >= WINNING_SCORE:
            winner_text = "Player 2 Wins!"
            
        if winner_text:
            text = font.render(winner_text, True, BLACK)
            restart_text = small_font.render("Press SPACE to Restart", True, BLACK)
            
            # Create a semi-transparent overlay
            s = pygame.Surface((WIDTH,HEIGHT))
            s.set_alpha(128)
            s.fill(WHITE)
            screen.blit(s, (0,0))
            
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))
            pygame.display.update()
            
            # Wait for restart
            waiting = True
            while waiting:
                clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        waiting = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            score1 = 0
                            score2 = 0
                            puck.reset()
                            # Reset paddles too
                            player1.x, player1.y = 100, HEIGHT // 2
                            player2.x, player2.y = WIDTH - 100, HEIGHT // 2
                            waiting = False
            continue # Skip the rest of the loop to restart fresh logic

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
