import pygame
import random
import sys
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GREEN = (34, 177, 76)
YELLOW = (255, 242, 0)
RED = (237, 28, 36)
BLUE = (0, 162, 232)
ORANGE = (255, 127, 39)

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, is_player=True):
        super().__init__()
        self.is_player = is_player
        self.width = 40
        self.height = 70
        
        # Create car surface with gradient and details
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if is_player:
            # Player car - Blue sports car
            self.draw_player_car()
        else:
            # Enemy car - Random colored cars
            self.draw_enemy_car()
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5 if is_player else random.randint(3, 7)
        
    def draw_player_car(self):
        # Main body - Blue
        pygame.draw.rect(self.image, BLUE, (5, 15, 30, 50), border_radius=8)
        # Top part - darker blue
        pygame.draw.rect(self.image, (0, 100, 180), (8, 20, 24, 20), border_radius=5)
        # Windows
        pygame.draw.rect(self.image, (100, 200, 255), (10, 22, 20, 8))
        pygame.draw.rect(self.image, (100, 200, 255), (10, 32, 20, 8))
        # Wheels
        pygame.draw.rect(self.image, BLACK, (2, 18, 8, 14), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (30, 18, 8, 14), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (2, 48, 8, 14), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (30, 48, 8, 14), border_radius=3)
        # Front lights
        pygame.draw.circle(self.image, YELLOW, (12, 10), 3)
        pygame.draw.circle(self.image, YELLOW, (28, 10), 3)
        # Racing stripes
        pygame.draw.rect(self.image, WHITE, (18, 15, 4, 50))
        
    def draw_enemy_car(self):
        colors = [RED, GREEN, ORANGE, (255, 192, 203), (128, 0, 128)]
        color = random.choice(colors)
        
        # Main body
        pygame.draw.rect(self.image, color, (5, 15, 30, 50), border_radius=8)
        # Top part - darker shade
        dark_color = tuple(max(0, c - 50) for c in color)
        pygame.draw.rect(self.image, dark_color, (8, 20, 24, 20), border_radius=5)
        # Windows
        pygame.draw.rect(self.image, (200, 200, 200), (10, 22, 20, 8))
        pygame.draw.rect(self.image, (200, 200, 200), (10, 32, 20, 8))
        # Wheels
        pygame.draw.rect(self.image, BLACK, (2, 18, 8, 14), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (30, 18, 8, 14), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (2, 48, 8, 14), border_radius=3)
        pygame.draw.rect(self.image, BLACK, (30, 48, 8, 14), border_radius=3)
        # Rear lights
        pygame.draw.circle(self.image, RED, (12, 62), 3)
        pygame.draw.circle(self.image, RED, (28, 62), 3)
    
    def update(self):
        if not self.is_player:
            self.rect.y += self.speed

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type_name):
        super().__init__()
        self.type = type_name
        self.width = 30
        self.height = 30
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if type_name == "shield":
            # Shield power-up - Blue
            pygame.draw.circle(self.image, BLUE, (15, 15), 14)
            pygame.draw.circle(self.image, (0, 200, 255), (15, 15), 10)
            pygame.draw.polygon(self.image, WHITE, [(15, 8), (10, 22), (20, 22)])
        elif type_name == "speed":
            # Speed boost - Yellow
            pygame.draw.circle(self.image, YELLOW, (15, 15), 14)
            pygame.draw.circle(self.image, ORANGE, (15, 15), 10)
            # Lightning bolt
            points = [(15, 6), (13, 15), (17, 15), (15, 24)]
            pygame.draw.polygon(self.image, WHITE, points)
        elif type_name == "coin":
            # Coin - Gold
            pygame.draw.circle(self.image, YELLOW, (15, 15), 14)
            pygame.draw.circle(self.image, ORANGE, (15, 15), 10)
            pygame.draw.circle(self.image, YELLOW, (15, 15), 6)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 4
    
    def update(self):
        self.rect.y += self.speed

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 40
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw traffic cone
        pygame.draw.polygon(self.image, ORANGE, [(20, 5), (5, 35), (35, 35)])
        pygame.draw.rect(self.image, WHITE, (8, 15, 24, 4))
        pygame.draw.rect(self.image, WHITE, (10, 22, 20, 4))
        pygame.draw.rect(self.image, DARK_GRAY, (15, 35, 10, 5))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
    
    def update(self):
        self.rect.y += self.speed

class RoadLine(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 40))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 8
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.rect.y = -40

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🏎️ Turbo Racer 2D")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.reset_game()
    
    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemy_cars = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.road_lines = pygame.sprite.Group()
        
        # Create road lines
        for i in range(15):
            line = RoadLine(SCREEN_WIDTH // 2 - 5, i * 60)
            self.road_lines.add(line)
            self.all_sprites.add(line)
        
        # Player car
        self.player = Car(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 100, is_player=True)
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.lives = 3
        self.speed_boost = 1.0
        self.shield_active = False
        self.shield_timer = 0
        self.speed_timer = 0
        self.game_speed = 1.0
        self.spawn_timer = 0
        self.powerup_timer = 0
        self.running = True
        self.game_over = False
        self.paused = False
    
    def spawn_enemy(self):
        lanes = [100, 200, 300, 400, 500, 600]
        x = random.choice(lanes)
        enemy = Car(x, -100, is_player=False)
        self.enemy_cars.add(enemy)
        self.all_sprites.add(enemy)
    
    def spawn_powerup(self):
        lanes = [100, 200, 300, 400, 500, 600]
        x = random.choice(lanes)
        powerup_type = random.choice(["shield", "speed", "coin", "coin"])
        powerup = PowerUp(x, -50, powerup_type)
        self.powerups.add(powerup)
        self.all_sprites.add(powerup)
    
    def spawn_obstacle(self):
        lanes = [100, 200, 300, 400, 500, 600]
        x = random.choice(lanes)
        obstacle = Obstacle(x, -50)
        self.obstacles.add(obstacle)
        self.all_sprites.add(obstacle)
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.player.rect.x > 50:
            self.player.rect.x -= 6
        if keys[pygame.K_RIGHT] and self.player.rect.x < SCREEN_WIDTH - 90:
            self.player.rect.x += 6
        if keys[pygame.K_UP] and self.player.rect.y > 0:
            self.player.rect.y -= 5
        if keys[pygame.K_DOWN] and self.player.rect.y < SCREEN_HEIGHT - 80:
            self.player.rect.y += 5
    
    def check_collisions(self):
        # Enemy car collisions
        hits = pygame.sprite.spritecollide(self.player, self.enemy_cars, True)
        if hits and not self.shield_active:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
        
        # Obstacle collisions
        obstacle_hits = pygame.sprite.spritecollide(self.player, self.obstacles, True)
        if obstacle_hits and not self.shield_active:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
        
        # PowerUp collisions
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            if powerup.type == "shield":
                self.shield_active = True
                self.shield_timer = 180  # 3 seconds at 60 FPS
            elif powerup.type == "speed":
                self.speed_boost = 1.5
                self.speed_timer = 180
            elif powerup.type == "coin":
                self.score += 50
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        self.all_sprites.update()
        
        # Spawn enemies
        self.spawn_timer += 1
        if self.spawn_timer > max(30, 60 - self.score // 100):
            self.spawn_enemy()
            self.spawn_timer = 0
        
        # Spawn powerups
        self.powerup_timer += 1
        if self.powerup_timer > 180:
            self.spawn_powerup()
            self.powerup_timer = 0
        
        # Spawn obstacles occasionally
        if random.randint(1, 150) == 1:
            self.spawn_obstacle()
        
        # Remove off-screen sprites
        for enemy in self.enemy_cars:
            if enemy.rect.y > SCREEN_HEIGHT:
                enemy.kill()
                self.score += 10
        
        for powerup in self.powerups:
            if powerup.rect.y > SCREEN_HEIGHT:
                powerup.kill()
        
        for obstacle in self.obstacles:
            if obstacle.rect.y > SCREEN_HEIGHT:
                obstacle.kill()
        
        # Update timers
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.shield_active = False
        
        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer == 0:
                self.speed_boost = 1.0
        
        self.check_collisions()
    
    def draw(self):
        # Draw road background
        self.screen.fill(DARK_GRAY)
        
        # Road
        pygame.draw.rect(self.screen, GRAY, (50, 0, SCREEN_WIDTH - 100, SCREEN_HEIGHT))
        
        # Road edges
        pygame.draw.rect(self.screen, YELLOW, (50, 0, 8, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, YELLOW, (SCREEN_WIDTH - 58, 0, 8, SCREEN_HEIGHT))
        
        # Grass on sides
        for i in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.rect(self.screen, GREEN, (0, i, 50, 10))
            pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 50, i, 50, 10))
        
        # Draw all sprites
        self.all_sprites.draw(self.screen)
        
        # Draw shield effect
        if self.shield_active:
            shield_surface = pygame.Surface((60, 90), pygame.SRCALPHA)
            pygame.draw.ellipse(shield_surface, (0, 200, 255, 100), shield_surface.get_rect(), 3)
            self.screen.blit(shield_surface, (self.player.rect.x - 10, self.player.rect.y - 10))
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.font_small.render(f"Lives:", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        for i in range(self.lives):
            pygame.draw.circle(self.screen, RED, (70 + i * 25, 60), 8)
        
        # Power-ups status
        y_offset = 90
        if self.shield_active:
            shield_text = self.font_small.render(f"🛡️ Shield: {self.shield_timer // 60}s", True, BLUE)
            self.screen.blit(shield_text, (10, y_offset))
            y_offset += 30
        
        if self.speed_boost > 1.0:
            speed_text = self.font_small.render(f"⚡ Speed: {self.speed_timer // 60}s", True, YELLOW)
            self.screen.blit(speed_text, (10, y_offset))
        
        # Instructions
        inst_text = self.font_small.render("Arrow keys to move | P: Pause | ESC: Menu", True, WHITE)
        self.screen.blit(inst_text, (SCREEN_WIDTH - 420, SCREEN_HEIGHT - 30))
    
    def show_menu(self):
        menu_running = True
        while menu_running:
            self.screen.fill(DARK_GRAY)
            
            # Title
            title = self.font_large.render("🏎️ TURBO RACER 2D", True, YELLOW)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(title, title_rect)
            
            # Menu options
            start_text = self.font_medium.render("Press SPACE to Start", True, WHITE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
            self.screen.blit(start_text, start_rect)
            
            # Instructions
            instructions = [
                "How to Play:",
                "• Use Arrow Keys to move your car",
                "• Avoid enemy cars and obstacles",
                "• Collect power-ups:",
                "  🛡️ Shield - Protects from crashes",
                "  ⚡ Speed Boost - Faster movement",
                "  💰 Coins - Extra points",
                "• Survive as long as possible!",
            ]
            
            y = 320
            for line in instructions:
                text = self.font_small.render(line, True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(text, text_rect)
                y += 30
            
            quit_text = self.font_small.render("Press ESC to Quit", True, RED)
            quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(quit_text, quit_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        menu_running = False
                    if event.key == pygame.K_ESCAPE:
                        return False
        
        return True
    
    def show_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font_large.render("GAME OVER!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(score_text, score_rect)
        
        # Restart option
        restart_text = self.font_small.render("Press R to Restart or ESC for Menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 360))
        self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        if not self.show_menu():
            return
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not self.show_menu():
                            self.running = False
                    
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    
                    if self.game_over and event.key == pygame.K_r:
                        self.reset_game()
            
            if not self.game_over and not self.paused:
                self.handle_input()
                self.update()
            
            self.draw()
            
            if self.game_over:
                self.show_game_over()
            
            if self.paused and not self.game_over:
                pause_text = self.font_large.render("PAUSED", True, YELLOW)
                pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(pause_text, pause_rect)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
