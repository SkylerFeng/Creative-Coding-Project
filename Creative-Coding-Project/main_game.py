# main_game.py
import pygame
import sys
import cv2
from head_and_hand import HandAndHeadControl  # 导入 HandAndHeadControl 类
from stickman import StickMan
from collections import deque
from movement_analyzer import MovementAnalyzer
import math
import random

pygame.init()
pygame.mixer.init()  # 初始化音频系统

# 加载音效
try:
    pygame.mixer.music.load('sounds/background.mp3')
    jump_sound = pygame.mixer.Sound('sounds/jump.mp3')
    hit_sound = pygame.mixer.Sound('sounds/hit.mp3')
    game_start_sound = pygame.mixer.Sound('sounds/game_start.mp3')
    game_over_sound = pygame.mixer.Sound('sounds/game_over.mp3')
except Exception as e:
    print("音效文件加载失败：", e)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Battle Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

clock = pygame.time.Clock()
FPS = 30

# 游戏状态
game_state = "start"  # start, playing, game_over
round_number = 1
player1_score = 0
player2_score = 0

player1 = StickMan(200, 450, RED)
player2 = StickMan(600, 450, BLUE, flip=True)

cap = cv2.VideoCapture(0)
hand_and_head_control = HandAndHeadControl()  # 初始化 HandAndHeadControl 类
movement_analyzer = MovementAnalyzer()

hand_sequence_length = 15
index_hand = 0
head_sequence_length = 30
index_head = 0
head_sequence = deque(maxlen=head_sequence_length)

left_hand_sequence = deque(maxlen=hand_sequence_length)
right_hand_sequence = deque(maxlen=hand_sequence_length)

# 初始化手部和头部位置为(0,0)，防止空列表访问错误
left_hand_sequence.append((0, 0))
right_hand_sequence.append((0, 0))
head_sequence.append((0, 0))

LEFT_ATTACK_BOUNDARY = 100
RIGHT_ATTACK_BOUNDARY = 700

print("📷 摄像头帧率:", cap.get(cv2.CAP_PROP_FPS))
running = True
start = False

# 背景粒子效果
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 4)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.speed = random.uniform(1, 3)
        self.life = random.randint(20, 40)

    def update(self):
        self.y -= self.speed
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

particles = []

def draw_cloud(screen, x, y, scale=1.0):
    # 画一朵简单的云
    pygame.draw.ellipse(screen, (255,255,255), (x, y, 60*scale, 30*scale))
    pygame.draw.ellipse(screen, (255,255,255), (x+20*scale, y-10*scale, 50*scale, 35*scale))
    pygame.draw.ellipse(screen, (255,255,255), (x+40*scale, y, 60*scale, 30*scale))

def draw_health_bar(screen, x, y, width, height, health, color, border_color=(0,0,0)):
    # 背景
    pygame.draw.rect(screen, (220,220,220), (x, y, width, height), border_radius=10)
    # 低血量变色
    if health > 60:
        bar_color = color
    elif health > 30:
        bar_color = (255, 165, 0)  # 橙色
    else:
        bar_color = (220, 20, 60)  # 红色
    # 血量条
    inner_width = int((health/100)*width)
    if inner_width > 0:
        pygame.draw.rect(screen, bar_color, (x, y, inner_width, height), border_radius=10)
    # 边框
    pygame.draw.rect(screen, border_color, (x, y, width, height), 2, border_radius=10)
    # 数值
    font = pygame.font.SysFont(None, 22)
    text = font.render(f"{int(health)}%", True, (30,30,30))
    screen.blit(text, (x+width//2-text.get_width()//2, y+height//2-text.get_height()//2))

while running:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # 水平翻转图像
    if not ret:
        print("摄像头读取失败")
        break

    keys = pygame.key.get_pressed()  # 提前放到这里
    
    hands = hand_and_head_control.get_hands(frame)
    head_center = hand_and_head_control.get_head_center(frame)
    if hands['left']:
        left_hand_sequence.append(hands['left'])
        #cv2.circle(frame, hands['left'], 5, (0, 255, 0), -1)  # 绿色标记左手
        cv2.putText(frame, f"Left Hand Center: {hands['left']}", (hands['left'][0] + 10, hands['left'][1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if hands['left'][0] < LEFT_ATTACK_BOUNDARY:
            player1.attack_left()
    else: 
        # 修复：确保列表不为空
        if left_hand_sequence:
            left_hand_sequence.append(left_hand_sequence[-1])
        else:
            left_hand_sequence.append((0, 0))
            
    if hands['right']:
        right_hand_sequence.append(hands['right'])
        #cv2.circle(frame, hands['right'], 5, (255, 0, 0), -1)  # 蓝色标记右手
        cv2.putText(frame, f"Right Hand Center: {hands['right']}", (hands['right'][0] + 10, hands['right'][1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        if hands['right'][0] > RIGHT_ATTACK_BOUNDARY:
            player1.attack_right()
    else: 
        # 修复：确保列表不为空
        if right_hand_sequence:
            right_hand_sequence.append(right_hand_sequence[-1])
        else:
            right_hand_sequence.append((0, 0))
            
    index_hand = (index_hand + 1) % hand_sequence_length   
     
    if head_center:
        head_sequence.append(head_center)
        #cv2.circle(frame, head_center, 5, (0, 0, 255), -1)  # 红色标记头部
        cv2.putText(frame, f"Head Center: {head_center}", (head_center[0] + 10, head_center[1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
        # 基于头部位置区域的移动识别
        # 获取视频帧宽度
        frame_width = frame.shape[1]
        
        # 定义左、中、右区域边界
        left_region_boundary = frame_width * 0.4  # 从0.3调整到0.4
        right_region_boundary = frame_width * 0.6  # 从0.7调整到0.6
        
        # 显示区域分界线（用于调试）
        cv2.line(frame, (int(left_region_boundary), 0), (int(left_region_boundary), frame.shape[0]), (0, 255, 255), 2)
        cv2.line(frame, (int(right_region_boundary), 0), (int(right_region_boundary), frame.shape[0]), (0, 255, 255), 2)
        
        # 根据头部在哪个区域决定移动
        head_x = head_center[0]
        
        if head_x < left_region_boundary:
            # 头在左区域，向左移动
            print("👈 头部在左区域，向左移动")
            player1.x -= 5
            player1.is_moving = True
            player1.facing_right = False
        elif head_x > right_region_boundary:
            # 头在右区域，向右移动
            print("👉 头部在右区域，向右移动")
            player1.x += 5
            player1.is_moving = True
            player1.facing_right = True
        else:
            # 头在中间区域，不移动
            print("🔄 头部在中间区域，不移动")
            player1.is_moving = False
    index_head = (index_head + 1) % head_sequence_length
    print("🎥 当前帧读取状态:", ret)
    print("🧠 当前头部坐标:", head_center)
    print("🖐 当前手部坐标:", hands)
    print("🔁 当前 index_hand:", index_hand, "| index_head:", index_head)
    print(f"📏 head_sequence: {len(head_sequence)} | left_hand: {len(left_hand_sequence)} | right_hand: {len(right_hand_sequence)}")
    
    # 显示摄像头图像
    cv2.imshow("Hand and Head Detection", frame)
    #cv2.waitKey(1)
    
    # 更新和绘制粒子
    for particle in particles[:]:
        if not particle.update():
            particles.remove(particle)
        else:
            particle.draw(screen)
    
    # 随机生成新粒子
    if random.random() < 0.3:
        particles.append(Particle(random.randint(0, WIDTH), HEIGHT))

    # 绘制蓝天渐变
    for i in range(HEIGHT):
        color = (135 - i//20, 206 - i//10, 250)
        pygame.draw.line(screen, color, (0, i), (WIDTH, i))
    # 绘制多朵云
    draw_cloud(screen, 100, 80, 1.2)
    draw_cloud(screen, 300, 120, 0.8)
    draw_cloud(screen, 500, 60, 1.0)
    draw_cloud(screen, 650, 100, 1.5)
    draw_cloud(screen, 200, 200, 0.7)

    # 绘制游戏状态
    if game_state == "start":
        font = pygame.font.SysFont(None, 48)
        title = font.render("Stickman Battle", True, BLACK)
        start_text = font.render("Press SPACE to Start", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
        
        if keys[pygame.K_SPACE]:
            game_state = "playing"
            game_start_sound.play()
            pygame.mixer.music.play(-1)  # 循环播放背景音乐

    elif game_state == "playing":
        # 绘制回合信息
        font = pygame.font.SysFont(None, 36)
        round_text = font.render(f"Round {round_number}", True, BLACK)
        score_text = font.render(f"Score: {player1_score} - {player2_score}", True, BLACK)
        screen.blit(round_text, (WIDTH//2 - round_text.get_width()//2, 10))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 50))

        # 检查游戏结束条件
        if player1.health <= 0 or player2.health <= 0:
            game_state = "game_over"
            game_over_sound.play()
            pygame.mixer.music.stop()
            if player1.health <= 0:
                player2_score += 1
            else:
                player1_score += 1

    elif game_state == "game_over":
        font = pygame.font.SysFont(None, 48)
        winner = "Player 2" if player1.health <= 0 else "Player 1"
        game_over_text = font.render(f"{winner} Wins!", True, BLACK)
        restart_text = font.render("Press R to Restart", True, BLACK)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//3))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))
        
        if keys[pygame.K_r]:
            game_state = "playing"
            player1.health = 100
            player2.health = 100
            round_number += 1
            game_start_sound.play()
            pygame.mixer.music.play(-1)

    # 在玩家跳跃时播放音效
    if player1.is_jumping and not player1.jump_sound_played:
        jump_sound.play()
        player1.jump_sound_played = True
    if player2.is_jumping and not player2.jump_sound_played:
        jump_sound.play()
        player2.jump_sound_played = True

    # 在检测到攻击命中时播放音效
    if player1.check_hit(player2) or player2.check_hit(player1):
        hit_sound.play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    print("1111111")
    if index_head == head_sequence_length - 1:
        start = True
    if start:
        
        try:
            print("✅ 进入动作判断区")

            player1.is_moving = False

            if movement_analyzer.is_jumping(head_sequence, index_head):
                player1.jump()

            if movement_analyzer.is_attacking_left(left_hand_sequence, index_hand):
                player1.attack_left()

            if movement_analyzer.is_attacking_right(right_hand_sequence, index_hand):
                player1.attack_right()

            if hands['left'] and hands['right'] and head_center:
                head_x, head_y = head_center
                
                # 定义胸口区域
                chest_top = head_y + 30
                chest_bottom = head_y + 100
                chest_left = head_x - 70
                chest_right = head_x + 70
                
                # 检查双手是否都在胸口区域
                is_left_hand_in_chest = (
                    chest_left < hands['left'][0] < chest_right and
                    chest_top < hands['left'][1] < chest_bottom
                )
                
                is_right_hand_in_chest = (
                    chest_left < hands['right'][0] < chest_right and
                    chest_top < hands['right'][1] < chest_bottom
                )
                
                # 打印调试信息
                print(f"左手在胸口: {is_left_hand_in_chest}, 右手在胸口: {is_right_hand_in_chest}")
                print(f"胸口区域: ({chest_left}, {chest_top}) - ({chest_right}, {chest_bottom})")
                print(f"左手位置: {hands['left']}, 右手位置: {hands['right']}")
                
                # 只要双手都在胸口区域，就触发防守
                if is_left_hand_in_chest and is_right_hand_in_chest:
                    print("🛡️ 防守动作已触发!")
                    player1.defend()
        
        except Exception as e:
            print("❌ 动作分析时出错：", e)
        

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
    if keys[pygame.K_COMMA]:
        player2.attack_left()
    if keys[pygame.K_PERIOD]:
        player2.attack_right()
    if keys[pygame.K_SLASH]:
        player2.defend()

    player1.x = max(50, min(player1.x, WIDTH - 50))
    player2.x = max(50, min(player2.x, WIDTH - 50))

    player1.update(player2)
    player2.update(player1)

    player1.check_hit(player2)
    player2.check_hit(player1)

    pygame.draw.line(screen, BLACK, (0, 450), (WIDTH, 450), 5)

    health_bar_width = 200
    health_bar_height = 24
    health_x1 = 50
    health_y = 30
    draw_health_bar(screen, health_x1, health_y, health_bar_width, health_bar_height, player1.health, RED)
    health_x2 = WIDTH - 50 - health_bar_width
    draw_health_bar(screen, health_x2, health_y, health_bar_width, health_bar_height, player2.health, BLUE)

    player1.draw(screen)
    player2.draw(screen)

    font = pygame.font.SysFont(None, 24)
    attack_text1 = font.render("Player 1: F - Left, H - Right, G - Defend, W - Jump", True, BLACK)
    attack_text2 = font.render("Player 2: K - Left, ; - Right, L - Defend, ↑ - Jump", True, BLACK)
    screen.blit(attack_text1, (10, HEIGHT - 30))
    screen.blit(attack_text2, (WIDTH - 310, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
