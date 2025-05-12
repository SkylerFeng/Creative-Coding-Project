import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Battle Game")

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Frame rate control
clock = pygame.time.Clock()
FPS = 60

class StickMan:
    def __init__(self, x, y, color, flip=False):
        self.x = x
        self.y = y
        self.color = color
        self.flip = flip  # Whether the character is facing left
        
        # State
        self.attacking = False
        self.defending = False
        self.attack_timer = 0
        self.defense_timer = 0
        self.health = 100
        
        # Animation parameters
        self.attack_duration = 20
        self.defense_duration = 20
        self.punch_scale = 1.0
        self.head_scale = 1.0
        self.arm_length = 40  # Initial arm length
        
        # Jumping
        self.is_jumping = False
        self.jump_velocity = 0
        self.jump_height = 15
        self.gravity = 0.8
        self.jump_speed = 15
        
        # Movement
        self.is_moving = False
        self.facing_right = not flip
        self.animation_frame = 0
        
    def update(self, other):
        self.animation_frame += 0.2
        
        # Jump physics
        if self.is_jumping:
            self.y -= self.jump_velocity
            self.jump_velocity -= self.gravity
            
            # Check if landed
            if self.y >= 400:
                self.y = 400
                self.is_jumping = False
                self.jump_velocity = 0
        
        # Attack animation
        if self.attacking:
            self.attack_timer += 1
            
            dx = other.x - self.x if not self.flip else self.x - other.x
            dx = max(40, min(dx, 150))  # Clamp distance
            
            if self.attack_timer <= self.attack_duration / 2:
                self.punch_scale = 1.0 + (self.attack_timer / (self.attack_duration / 2)) * 2.0
                self.arm_length = dx
            else:
                self.punch_scale = 3.0 - ((self.attack_timer - self.attack_duration / 2) / (self.attack_duration / 2)) * 2.0
                self.arm_length = 40 + ((self.attack_duration - self.attack_timer) / (self.attack_duration / 2)) * (dx - 40)

            if self.attack_timer >= self.attack_duration:
                self.attacking = False
                self.attack_timer = 0
                self.punch_scale = 1.0
                self.arm_length = 40
                
        # Defense animation
        if self.defending:
            self.defense_timer += 1
            if self.defense_timer <= self.defense_duration / 2:
                self.head_scale = 1.0 + (self.defense_timer / (self.defense_duration / 2)) * 2.0
            
            if self.defense_timer >= self.defense_duration:
                self.defending = False
                self.defense_timer = 0
                self.head_scale = 1.0
    
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = self.jump_speed
    
    def attack(self):
        if not self.attacking and not self.defending:
            self.attacking = True
            self.attack_timer = 0
    
    def defend(self):
        if not self.defending and not self.attacking:
            self.defending = True
            self.defense_timer = 0
            
    def take_damage(self, amount):
        if not self.defending:
            self.health -= amount
            if self.health < 0:
                self.health = 0
    
    def draw(self):
        head_radius = 15 * self.head_scale
        body_length = 60
        leg_length = 50
        
        head_x = self.x
        head_y = self.y
        
        punch_x_offset = self.arm_length if not self.flip else -self.arm_length
        punch_radius = 8 * self.punch_scale if self.attacking else 8
        
        # Head
        pygame.draw.circle(screen, self.color, (head_x, head_y), int(head_radius))
        
        # Body
        body_bottom_x = head_x
        body_bottom_y = head_y + body_length
        pygame.draw.line(screen, self.color, (head_x, head_y + int(head_radius)), 
                         (body_bottom_x, body_bottom_y), 3)
        
        # Arms
        arm_joint_y = head_y + int(head_radius) + 15
        
        # Main arm (attacking direction)
        arm_end_x = head_x + punch_x_offset
        arm_end_y = arm_joint_y
        pygame.draw.line(screen, self.color, (head_x, arm_joint_y), 
                         (arm_end_x, arm_end_y), 3)
        pygame.draw.circle(screen, self.color, (int(arm_end_x), int(arm_end_y)), int(punch_radius))
        
        # Other arm
        other_arm_x = head_x + (-self.arm_length // 2 if not self.flip else self.arm_length // 2)
        other_arm_y = arm_joint_y + 10
        pygame.draw.line(screen, self.color, (head_x, arm_joint_y), 
                         (other_arm_x, other_arm_y), 3)
        pygame.draw.circle(screen, self.color, (int(other_arm_x), int(other_arm_y)), 5)
        
        # Legs
        left_leg_x = body_bottom_x + (leg_length // 2 if not self.flip else -leg_length // 2)
        right_leg_x = body_bottom_x + (-leg_length // 2 if not self.flip else leg_length // 2)
        leg_y = body_bottom_y + leg_length
        pygame.draw.line(screen, self.color, (body_bottom_x, body_bottom_y), (left_leg_x, leg_y), 3)
        pygame.draw.line(screen, self.color, (body_bottom_x, body_bottom_y), (right_leg_x, leg_y), 3)
    
    def check_hit(self, other):
        if self.attacking and self.attack_timer == self.attack_duration // 2:
            arm_joint_y = self.y + 15 * self.head_scale + 15
            punch_x = self.x + (self.arm_length if not self.flip else -self.arm_length)
            punch_y = arm_joint_y
            distance = math.sqrt((punch_x - other.x)**2 + (punch_y - other.y)**2)
            if distance < 40:
                other.take_damage(10)
                return True
        return False

# Create two stickmen
player1 = StickMan(200, 400, RED)
player2 = StickMan(600, 400, BLUE, flip=True)

# Main game loop
running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    
    # Player 1 controls
    player1.is_moving = False
    if keys[pygame.K_a]:
        player1.x -= 5
        player1.is_moving = True
        player1.facing_right = False
    if keys[pygame.K_d]:
        player1.x += 5
        player1.is_moving = True
        player1.facing_right = True
    if keys[pygame.K_w]:
        player1.jump()
    if keys[pygame.K_f]:
        player1.attack()
    if keys[pygame.K_g]:
        player1.defend()
    
    # Player 2 controls
    player2.is_moving = False
    if keys[pygame.K_LEFT]:
        player2.x -= 5
        player2.is_moving = True
        player2.facing_right = False
    if keys[pygame.K_RIGHT]:
        player2.x += 5
        player2.is_moving = True
        player2.facing_right = True
    if keys[pygame.K_UP]:
        player2.jump()
    if keys[pygame.K_k]:
        player2.attack()
    if keys[pygame.K_l]:
        player2.defend()
    
    # Keep players inside the screen
    player1.x = max(50, min(player1.x, WIDTH - 50))
    player2.x = max(50, min(player2.x, WIDTH - 50))
    
    player1.update(player2)
    player2.update(player1)
    
    player1.check_hit(player2)
    player2.check_hit(player1)
    
    # Draw ground
    pygame.draw.line(screen, BLACK, (0, 450), (WIDTH, 450), 5)
    
    # Draw health bars
    health_bar_width = 200
    health_bar_height = 20
    health_x1 = 50
    health_y = 30
    pygame.draw.rect(screen, BLACK, (health_x1, health_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, RED, (health_x1, health_y, (player1.health / 100) * health_bar_width, health_bar_height))
    
    health_x2 = WIDTH - 50 - health_bar_width
    pygame.draw.rect(screen, BLACK, (health_x2, health_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, BLUE, (health_x2, health_y, (player2.health / 100) * health_bar_width, health_bar_height))
    
    # Draw players
    player1.draw()
    player2.draw()
    
    # Controls hint
    font = pygame.font.SysFont(None, 24)
    attack_text1 = font.render("Player 1: F - Attack, G - Defend, W - Jump", True, BLACK)
    attack_text2 = font.render("Player 2: K - Attack, L - Defend, ↑ - Jump", True, BLACK)
    screen.blit(attack_text1, (10, HEIGHT - 30))
    screen.blit(attack_text2, (WIDTH - 270, HEIGHT - 30))
    
    # Win condition
    if player1.health <= 0 or player2.health <= 0:
        font = pygame.font.SysFont(None, 72)
        if player1.health <= 0 and player2.health <= 0:
            text = font.render("Draw!", True, BLACK)
        elif player1.health <= 0:
            text = font.render("Blue Wins!", True, BLUE)
        else:
            text = font.render("Red Wins!", True, RED)
        
        screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
