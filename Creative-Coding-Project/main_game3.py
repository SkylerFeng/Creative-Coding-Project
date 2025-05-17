# main_game_dual_camera.py
import pygame
import sys
import cv2
from head_and_hand import HandAndHeadControl
from stickman import StickMan
from collections import deque
from movement_analyzer import MovementAnalyzer
import numpy as np

pygame.init()
WIDTH, HEIGHT = 1200, 800  # 🎯 放大游戏画布
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Dual Camera Battle")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

clock = pygame.time.Clock()
FPS = 30

player1 = StickMan(300, 550, RED)  # 修正初始地面高度为 650（避免卡在“虚假地面”）
player2 = StickMan(900, 550, BLUE, flip=True)

winner = None
game_over = False
font_large = pygame.font.SysFont(None, 72)
font_small = pygame.font.SysFont(None, 36)  

# === 双摄像头 ===
cap1 = cv2.VideoCapture(0)  # 控制 player1
cap2 = cv2.VideoCapture(1)  # 控制 player2

# 获取摄像头图像宽度（用于头部位置映射）
cam1_width = cap1.get(cv2.CAP_PROP_FRAME_WIDTH)
cam2_width = cap2.get(cv2.CAP_PROP_FRAME_WIDTH)

hand_and_head_control1 = HandAndHeadControl()
hand_and_head_control2 = HandAndHeadControl()
movement_analyzer = MovementAnalyzer()

hand_sequence_length = 15
head_sequence_length = 30

# === Player 1 序列 ===
left_hand_seq1 = deque(maxlen=hand_sequence_length)
right_hand_seq1 = deque(maxlen=hand_sequence_length)
head_seq1 = deque(maxlen=head_sequence_length)

# === Player 2 序列 ===
left_hand_seq2 = deque(maxlen=hand_sequence_length)
right_hand_seq2 = deque(maxlen=hand_sequence_length)
head_seq2 = deque(maxlen=head_sequence_length)

running = True
while running:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret1 or not ret2:
        print("⚠️ 摄像头读取失败，跳过此帧")
        continue

    frame1 = cv2.flip(frame1, 1)  
    frame2 = cv2.flip(frame2, 1)
    #cv2.imshow("Camera 1", frame1)
    #cv2.imshow("Camera 2", frame2)

    # === Player 1 识别 ===
    hands1 = hand_and_head_control1.get_hands(frame1)
    head1 = hand_and_head_control1.get_head_center(frame1)
    if hands1['left']: left_hand_seq1.append(hands1['left'])
    if hands1['right']: right_hand_seq1.append(hands1['right'])
    if head1: head_seq1.append(head1)

    # === Player 2 识别 ===
    hands2 = hand_and_head_control2.get_hands(frame2)
    head2 = hand_and_head_control2.get_head_center(frame2)
    if hands2['left']: left_hand_seq2.append(hands2['left'])
    if hands2['right']: right_hand_seq2.append(hands2['right'])
    if head2: head_seq2.append(head2)

    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # === Player 1 用头部控制横向位置 ===
    if head1 and cam1_width:
        target_x1 = int(head1[0] / cam1_width * WIDTH)
        delta1 = abs(target_x1 - player1.x)
        player1.x += 0.3 * (target_x1 - player1.x)
        player1.x = max(50, min(WIDTH - 50, player1.x))
        player1.is_moving = delta1 > 1

    # === Player 2 用头部控制横向位置 ===
    if head2 and cam2_width:
        target_x2 = int(head2[0] / cam2_width * WIDTH)
        delta2 = abs(target_x2 - player2.x)
        player2.x += 0.3 * (target_x2 - player2.x)
        player2.x = max(50, min(WIDTH - 50, player2.x))
        player2.is_moving = delta2 > 1

    # === Player 1 动作判断 ===
    if len(head_seq1) == head_sequence_length:
        if movement_analyzer.is_jumping(head_seq1, -1):
            player1.jump()
        if movement_analyzer.is_attacking_left(left_hand_seq1, -1):
            player1.attack_left()
        if movement_analyzer.is_attacking_right(right_hand_seq1, -1):
            player1.attack_right()
        if movement_analyzer.is_defending(left_hand_seq1, right_hand_seq1, head_seq1, -1, -1):
            player1.defend()

    # === Player 2 动作判断 ===
    if len(head_seq2) == head_sequence_length:
        if movement_analyzer.is_jumping(head_seq2, -1):
            player2.jump()
        if movement_analyzer.is_attacking_left(left_hand_seq2, -1):
            player2.attack_left()
        if movement_analyzer.is_attacking_right(right_hand_seq2, -1):
            player2.attack_right()
        if movement_analyzer.is_defending(left_hand_seq2, right_hand_seq2, head_seq2, -1, -1):
            player2.defend()

    # 边界限制
    player1.x = max(50, min(player1.x, WIDTH - 50))
    player2.x = max(50, min(player2.x, WIDTH - 50))

    player1.update(player2)
    player2.update(player1)
    player1.check_hit(player2)
    player2.check_hit(player1)
    
    # 判断胜负
    if player1.health <= 0:
        winner = "Player 2"
        game_over = True
    elif player2.health <= 0:
        winner = "Player 1"
        game_over = True


    # UI
    pygame.draw.line(screen, BLACK, (0, 550), (WIDTH, 550), 5)

    bar_w, bar_h = 200, 20
    pygame.draw.rect(screen, BLACK, (50, 30, bar_w, bar_h))
    pygame.draw.rect(screen, RED, (50, 30, (player1.health / 100) * bar_w, bar_h))

    pygame.draw.rect(screen, BLACK, (WIDTH - 250, 30, bar_w, bar_h))
    pygame.draw.rect(screen, BLUE, (WIDTH - 250, 30, (player2.health / 100) * bar_w, bar_h))

    player1.draw(screen)
    player2.draw(screen)

    # === 摄像头画面嵌入为两个小窗口 ===
    def draw_camera_window(frame, pos):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (200, 150))
        surface = pygame.surfarray.make_surface(np.rot90(frame_resized))
        surface = pygame.transform.flip(surface, True, False)  # 不再翻转（摄像头已经处理了）
        screen.blit(surface, pos)



    draw_camera_window(frame1, (20, HEIGHT - 170))
    draw_camera_window(frame2, (WIDTH - 220, HEIGHT - 170))

    # 显示胜利结算画面
    if game_over:
        screen.fill(WHITE)
        
        # 胜者文字
        text = font_large.render(f"{winner} Wins!", True, (0, 128, 0))
        screen.blit(text, ((WIDTH - text.get_width()) // 2, HEIGHT // 2 - 100))

        # 重新开始
        restart_text = font_small.render("Press R to Restart", True, BLACK)
        screen.blit(restart_text, ((WIDTH - restart_text.get_width()) // 2, HEIGHT // 2))

        # 退出游戏
        quit_text = font_small.render("Press Q to Quit", True, BLACK)
        screen.blit(quit_text, ((WIDTH - quit_text.get_width()) // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

        restart_requested = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                        break
                    elif event.key == pygame.K_r:
                        # 标记重新开始
                        restart_requested = True
                        break
            if not running or restart_requested:
                break

        if not running:
            break  # 退出整个主循环
        elif restart_requested:
            # 执行重置
            player1 = StickMan(300, 550, RED)
            player2 = StickMan(900, 550, BLUE, flip=True)
            left_hand_seq1.clear()
            right_hand_seq1.clear()
            head_seq1.clear()
            left_hand_seq2.clear()
            right_hand_seq2.clear()
            head_seq2.clear()
            winner = None
            game_over = False
            continue  # 跳过这帧，重新读取摄像头


    
    pygame.display.flip()
    clock.tick(FPS)

cap1.release()
cap2.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
