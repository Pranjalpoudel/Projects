import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors (Neon Palette)
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_YELLOW = (255, 255, 0)
NEON_RED = (255, 50, 50)
GRID_COLOR = (40, 20, 60)

# Physics
GRAVITY = 0.8
JUMP_STRENGTH = -15
FLOOR_Y = HEIGHT - 100
CEILING_Y = 100

def draw_neon_rect(surface, color, rect, width=2, glow_radius=10):
    # Draw glow
    for i in range(glow_radius, 0, -2):
        alpha = 255 // (i + 1)
        s = pygame.Surface((rect.width + i*2, rect.height + i*2), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, 50), (0, 0, rect.width + i*2, rect.height + i*2), width)
        surface.blit(s, (rect.x - i, rect.y - i))
    # Draw core
    pygame.draw.rect(surface, color, rect, width)
    pygame.draw.rect(surface, WHITE, rect, 1)

def draw_neon_circle(surface, color, center, radius, width=2, glow_radius=10):
    for i in range(glow_radius, 0, -2):
        pygame.draw.circle(surface, (*color, 50), center, radius + i, width)
    pygame.draw.circle(surface, color, center, radius, width)
    pygame.draw.circle(surface, WHITE, center, radius - 2, 1)

class Particle:
    def __init__(self, x, y, color, vel_x, vel_y, size=5):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.size = size
        self.life = 255

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 10
        self.size -= 0.1

    def draw(self, screen):
        if self.life > 0 and self.size > 0:
            s = pygame.Surface((int(self.size)*4, int(self.size)*4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.life), (int(self.size)*2, int(self.size)*2), int(self.size))
            screen.blit(s, (self.x - self.size*2, self.y - self.size*2))

class Player:
    def __init__(self):
        self.size = 40
        self.x = 100
        self.y = FLOOR_Y - self.size
        self.vel_y = 0
        self.is_jumping = False
        self.gravity_inverted = False
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.angle = 0
        self.trail = [] # List of (x, y, angle, alpha)
        self.color = NEON_CYAN

    def jump(self):
        if not self.is_jumping:
            self.vel_y = JUMP_STRENGTH if not self.gravity_inverted else -JUMP_STRENGTH
            self.is_jumping = True

    def flip_gravity(self):
        self.gravity_inverted = not self.gravity_inverted
        self.vel_y = 0
        self.is_jumping = True # Treat as jumping until we hit the new floor/ceiling

    def move(self):
        # Apply Gravity
        if not self.gravity_inverted:
            self.vel_y += GRAVITY
        else:
            self.vel_y -= GRAVITY
        
        self.y += self.vel_y

        # Floor/Ceiling Collision
        if not self.gravity_inverted:
            if self.y >= FLOOR_Y - self.size:
                self.y = FLOOR_Y - self.size
                self.vel_y = 0
                self.is_jumping = False
                self.angle = 0
        else:
            if self.y <= CEILING_Y:
                self.y = CEILING_Y
                self.vel_y = 0
                self.is_jumping = False
                self.angle = 0

        # Rotation
        if self.is_jumping:
            self.angle -= 5 if not self.gravity_inverted else 5

        self.rect.y = int(self.y)
        
        # Trail Logic
        self.trail.append([self.x, self.y, self.angle, 255])
        if len(self.trail) > 10:
            self.trail.pop(0)

    def draw(self, screen):
        # Draw Trail
        for t in self.trail:
            t[3] -= 20 # Fade out
            if t[3] < 0: t[3] = 0
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*self.color, t[3]), (0, 0, self.size, self.size), 2)
            rot_surf = pygame.transform.rotate(surf, t[2])
            screen.blit(rot_surf, rot_surf.get_rect(center=(t[0] + self.size/2, t[1] + self.size/2)).topleft)

        # Draw Player
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.color, (0, 0, self.size, self.size), 3)
        pygame.draw.rect(surf, WHITE, (10, 10, 20, 20), 2) # Core
        
        rotated_surf = pygame.transform.rotate(surf, self.angle)
        new_rect = rotated_surf.get_rect(center=self.rect.center)
        
        # Glow effect for player
        draw_neon_rect(screen, self.color, new_rect, 2, 15)

class Obstacle:
    def __init__(self, x, inverted=False, type_override=None):
        self.type = type_override if type_override else random.choice(['spike', 'block', 'saw', 'portal'])
        self.x = x
        self.inverted = inverted
        self.width = 40
        self.height = 40
        self.angle = 0
        self.active = True # For portals (one-time use)

        # Determine Y position based on floor/ceiling
        if not self.inverted:
            base_y = FLOOR_Y
        else:
            base_y = CEILING_Y

        if self.type == 'spike':
            if not self.inverted:
                self.y = base_y
                self.rect = pygame.Rect(self.x, self.y - self.height, self.width, self.height)
            else:
                self.y = base_y
                self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.color = NEON_RED
        elif self.type == 'block':
            self.height = 60
            if not self.inverted:
                self.y = base_y
                self.rect = pygame.Rect(self.x, self.y - self.height, self.width, self.height)
            else:
                self.y = base_y
                self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.color = NEON_MAGENTA
        elif self.type == 'saw':
            if not self.inverted:
                self.y = base_y - 20
                self.rect = pygame.Rect(self.x, self.y - 40, 40, 40)
            else:
                self.y = base_y + 20
                self.rect = pygame.Rect(self.x, self.y, 40, 40)
            self.color = NEON_RED
        elif self.type == 'portal':
            if not self.inverted:
                self.y = base_y - 60
                self.rect = pygame.Rect(self.x, self.y, 40, 80)
            else:
                self.y = base_y - 20 # Adjust for ceiling
                self.rect = pygame.Rect(self.x, self.y, 40, 80)
            self.color = NEON_YELLOW

    def move(self, speed):
        self.x -= speed
        self.rect.x = int(self.x)
        if self.type == 'saw':
            self.angle += 10

    def draw(self, screen):
        if self.type == 'spike':
            if not self.inverted:
                points = [
                    (self.x, self.y),
                    (self.x + self.width // 2, self.y - self.height),
                    (self.x + self.width, self.y)
                ]
            else:
                points = [
                    (self.x, self.y),
                    (self.x + self.width // 2, self.y + self.height),
                    (self.x + self.width, self.y)
                ]
            pygame.draw.polygon(screen, self.color, points, 3)
            pygame.draw.polygon(screen, (*self.color, 100), points, 6)
            
        elif self.type == 'block':
            draw_neon_rect(screen, self.color, self.rect)
            
        elif self.type == 'saw':
            center = self.rect.center
            radius = 20
            draw_neon_circle(screen, self.color, center, radius)
            for i in range(0, 360, 45):
                rad = math.radians(i + self.angle)
                end_x = center[0] + math.cos(rad) * (radius + 10)
                end_y = center[1] + math.sin(rad) * (radius + 10)
                pygame.draw.line(screen, WHITE, center, (end_x, end_y), 2)

        elif self.type == 'portal':
            if self.active:
                draw_neon_rect(screen, self.color, self.rect, 3, 20)
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10
                inner_rect = self.rect.inflate(-10 + pulse, -10 + pulse)
                pygame.draw.rect(screen, WHITE, inner_rect, 1)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Geometric Dash: NEON HARDCORE")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30)

    def reset_game():
        return Player(), [], 0, 7, False, []

    player, obstacles, score, game_speed, game_over, particles = reset_game()
    spawn_timer = 0
    bg_offset = 0

    running = True
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if not game_over:
                        player.jump()
                    else:
                        player, obstacles, score, game_speed, game_over, particles = reset_game()

        if not game_over:
            player.move()
            
            # Background movement
            bg_offset -= game_speed * 0.5
            if bg_offset <= -40: bg_offset = 0

            # Spawn obstacles
            spawn_timer += 1
            if spawn_timer > random.randint(40, 100): 
                # Spawn logic: mostly on the side the player is on, but sometimes opposite to trick them?
                # For now, let's strictly spawn on the player's gravity side to ensure gameplay.
                # Or better: if gravity is inverted, spawn on ceiling. If normal, spawn on floor.
                
                spawn_inverted = player.gravity_inverted
                
                # Occasional portal to switch back/forth
                if random.random() < 0.1: 
                    # Force a portal spawn on the CURRENT side to allow switching
                    obstacles.append(Obstacle(WIDTH + 50, inverted=spawn_inverted, type_override='portal'))
                else:
                    obstacles.append(Obstacle(WIDTH + 50, inverted=spawn_inverted))
                
                spawn_timer = 0

            # Update Obstacles
            for obs in obstacles[:]:
                obs.move(game_speed)
                
                # Collision
                if player.rect.colliderect(obs.rect):
                    if obs.type == 'portal':
                        if obs.active:
                            player.flip_gravity()
                            obs.active = False 
                            for _ in range(20):
                                particles.append(Particle(player.x, player.y, NEON_YELLOW, random.uniform(-5, 5), random.uniform(-5, 5)))
                    else:
                        game_over = True
                        for _ in range(50):
                            particles.append(Particle(player.x, player.y, player.color, random.uniform(-10, 10), random.uniform(-10, 10)))

                if obs.x < -100:
                    obstacles.remove(obs)
                    score += 1
                    if score % 5 == 0:
                        game_speed += 0.5

            # Update Particles
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

        # Draw
        screen.fill(BLACK)
        
        # Draw Grid Background
        for x in range(0, WIDTH + 40, 40):
            pygame.draw.line(screen, GRID_COLOR, (x + bg_offset, 0), (x + bg_offset, HEIGHT))
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))
            
        # Draw Floor and Ceiling
        pygame.draw.line(screen, NEON_CYAN, (0, FLOOR_Y), (WIDTH, FLOOR_Y), 3)
        pygame.draw.line(screen, NEON_CYAN, (0, CEILING_Y), (WIDTH, CEILING_Y), 3)

        for obs in obstacles:
            obs.draw(screen)
            
        for p in particles:
            p.draw(screen)

        if not game_over:
            player.draw(screen)

        # UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))

        if game_over:
            over_text = font.render("GAME OVER", True, NEON_RED)
            restart_text = font.render("Press SPACE to Restart", True, WHITE)
            screen.blit(over_text, (WIDTH//2 - 100, HEIGHT//2 - 50))
            screen.blit(restart_text, (WIDTH//2 - 150, HEIGHT//2 + 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
