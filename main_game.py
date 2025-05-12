# main_game.py
import pygame
import sys
import cv2
from head_and_hand import HandAndHeadControl  # 导入 HandAndHeadControl 类
from stickman import StickMan
from collections import deque
from movement_analyzer import MovementAnalyzer

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Battle Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

clock = pygame.time.Clock()
FPS = 30

player1 = StickMan(200, 400, RED)
player2 = StickMan(600, 400, BLUE, flip=True)

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

#head_sequence[0] = hand_and_head_control.get_head_center(frame)
#hand_sequence[0] = hand_and_head_control.get_hands(frame)

start_time = pygame.time.get_ticks()  # 主循环前

print("📷 摄像头帧率:", cap.get(cv2.CAP_PROP_FPS))
running = True
start = False
while running:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # 水平翻转图像
    if not ret:
        print("摄像头读取失败")
        break
    
    
    hands = hand_and_head_control.get_hands(frame)
    head_center = hand_and_head_control.get_head_center(frame)
    if hands['left']:
        left_hand_sequence.append(hands['left'])
        #cv2.circle(frame, hands['left'], 5, (0, 255, 0), -1)  # 绿色标记左手
        cv2.putText(frame, f"Left Hand Center: {hands['left']}", (hands['left'][0] + 10, hands['left'][1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else: 
        left_hand_sequence.append(left_hand_sequence[index_hand - 1])
    if hands['right']:
        right_hand_sequence.append(hands['right'])
        #cv2.circle(frame, hands['right'], 5, (255, 0, 0), -1)  # 蓝色标记右手
        cv2.putText(frame, f"Right Hand Center: {hands['right']}", (hands['right'][0] + 10, hands['right'][1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    else: 
        right_hand_sequence.append(right_hand_sequence[index_hand - 1])
    index_hand = (index_hand + 1) % hand_sequence_length   
     
    if head_center:
        head_sequence.append(head_center)
        #cv2.circle(frame, head_center, 5, (0, 0, 255), -1)  # 红色标记头部
        cv2.putText(frame, f"Head Center: {head_center}", (head_center[0] + 10, head_center[1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    index_head = (index_head + 1) % head_sequence_length
    print("🎥 当前帧读取状态:", ret)
    print("🧠 当前头部坐标:", head_center)
    print("🖐 当前手部坐标:", hands)
    print("🔁 当前 index_hand:", index_hand, "| index_head:", index_head)
    print(f"📏 head_sequence: {len(head_sequence)} | left_hand: {len(left_hand_sequence)} | right_hand: {len(right_hand_sequence)}")
    


    # 显示摄像头图像
    cv2.imshow("Hand and Head Detection", frame)
    #cv2.waitKey(1)
    
    
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    print("1111111")
    if index_head == head_sequence_length - 1:
        start =True
    if start:
        
        try:
            print("✅ 进入动作判断区")

            player1.is_moving = False

            if movement_analyzer.is_moving_right(head_sequence, index_head):
                player1.x -= 5
                player1.is_moving = True
                player1.facing_right = False

            if movement_analyzer.is_moving_left(head_sequence, index_head):
                player1.x += 5
                player1.is_moving = True
                player1.facing_right = True

            if movement_analyzer.is_jumping(head_sequence, index_head):
                player1.jump()

            if movement_analyzer.is_attacking_left(left_hand_sequence, index_hand):
                player1.attack_left()

            if movement_analyzer.is_attacking_right(right_hand_sequence, index_hand):
                player1.attack_right()

            if movement_analyzer.is_defending(left_hand_sequence, right_hand_sequence, head_sequence, index_hand, index_head):
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
    health_bar_height = 20
    health_x1 = 50
    health_y = 30
    pygame.draw.rect(screen, BLACK, (health_x1, health_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, RED, (health_x1, health_y, (player1.health / 100) * health_bar_width, health_bar_height))

    health_x2 = WIDTH - 50 - health_bar_width
    pygame.draw.rect(screen, BLACK, (health_x2, health_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, BLUE, (health_x2, health_y, (player2.health / 100) * health_bar_width, health_bar_height))

    player1.draw(screen)
    player2.draw(screen)

    font = pygame.font.SysFont(None, 24)
    attack_text1 = font.render("Player 1: F - Left, H - Right, G - Defend, W - Jump", True, BLACK)
    attack_text2 = font.render("Player 2: K - Left, ; - Right, L - Defend, ↑ - Jump", True, BLACK)
    screen.blit(attack_text1, (10, HEIGHT - 30))
    screen.blit(attack_text2, (WIDTH - 310, HEIGHT - 30))

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
