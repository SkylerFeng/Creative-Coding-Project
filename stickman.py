# stickman.py
import pygame
import math

class StickMan:
    def __init__(self, x, y, color, flip=False):
        self.x = x
        self.y = y
        self.color = color
        self.flip = flip

        self.attacking_left = False
        self.attacking_right = False
        self.attack_timer_left = 0
        self.attack_timer_right = 0
        self.attack_duration = 20
        self.punch_scale_left = 1.0
        self.punch_scale_right = 1.0
        self.arm_length_left = 40
        self.arm_length_right = 40

        self.defending = False
        self.defense_timer = 0
        self.defense_duration = 20
        self.head_scale = 1.0

        self.health = 100

        self.is_jumping = False
        self.jump_velocity = 0
        self.jump_height = 15
        self.gravity = 0.8
        self.jump_speed = 15

        self.is_moving = False
        self.facing_right = not flip
        self.animation_frame = 0

    def update(self, other):
        self.animation_frame += 0.2

        if self.is_jumping:
            self.y -= self.jump_velocity
            self.jump_velocity -= self.gravity
            if self.y >= 550:
                self.y = 550
                self.is_jumping = False
                self.jump_velocity = 0

        if self.attacking_left:
            self.attack_timer_left += 1
            dx = abs(other.x - self.x)
            dx = max(40, min(dx, 150))
            if self.attack_timer_left <= self.attack_duration / 2:
                self.punch_scale_left = 1.0 + (self.attack_timer_left / (self.attack_duration / 2)) * 2.0
                self.arm_length_left = dx
            else:
                self.punch_scale_left = 3.0 - ((self.attack_timer_left - self.attack_duration / 2) / (self.attack_duration / 2)) * 2.0
                self.arm_length_left = 40 + ((self.attack_duration - self.attack_timer_left) / (self.attack_duration / 2)) * (dx - 40)
            if self.attack_timer_left >= self.attack_duration:
                self.attacking_left = False
                self.attack_timer_left = 0
                self.punch_scale_left = 1.0
                self.arm_length_left = 40

        if self.attacking_right:
            self.attack_timer_right += 1
            dx = abs(other.x - self.x)
            dx = max(40, min(dx, 150))
            if self.attack_timer_right <= self.attack_duration / 2:
                self.punch_scale_right = 1.0 + (self.attack_timer_right / (self.attack_duration / 2)) * 2.0
                self.arm_length_right = dx
            else:
                self.punch_scale_right = 3.0 - ((self.attack_timer_right - self.attack_duration / 2) / (self.attack_duration / 2)) * 2.0
                self.arm_length_right = 40 + ((self.attack_duration - self.attack_timer_right) / (self.attack_duration / 2)) * (dx - 40)
            if self.attack_timer_right >= self.attack_duration:
                self.attacking_right = False
                self.attack_timer_right = 0
                self.punch_scale_right = 1.0
                self.arm_length_right = 40

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

    def attack_left(self):
        if not self.attacking_left and not self.defending:
            self.attacking_left = True
            self.attack_timer_left = 0

    def attack_right(self):
        if not self.attacking_right and not self.defending:
            self.attacking_right = True
            self.attack_timer_right = 0

    def defend(self):
        if not self.defending and not (self.attacking_left or self.attacking_right):
            self.defending = True
            self.defense_timer = 0

    def take_damage(self, amount):
        if not self.defending:
            self.health -= amount
            if self.health < 0:
                self.health = 0

    def draw(self, screen):
        head_radius = 15 * self.head_scale
        body_length = 60
        leg_length = 50

        head_x = self.x
        head_y = self.y
        arm_joint_y = head_y + int(head_radius) + 15

        pygame.draw.circle(screen, self.color, (head_x, head_y), int(head_radius))
        body_bottom_x = head_x
        body_bottom_y = head_y + body_length
        pygame.draw.line(screen, self.color, (head_x, head_y + int(head_radius)),
                         (body_bottom_x, body_bottom_y), 3)

        right_end_x = head_x + self.arm_length_right
        right_end_y = arm_joint_y
        right_radius = 8 * self.punch_scale_right if self.attacking_right else 8
        pygame.draw.line(screen, self.color, (head_x, arm_joint_y), (right_end_x, right_end_y), 3)
        pygame.draw.circle(screen, self.color, (int(right_end_x), int(right_end_y)), int(right_radius))

        left_end_x = head_x - self.arm_length_left
        left_end_y = arm_joint_y
        left_radius = 8 * self.punch_scale_left if self.attacking_left else 8
        pygame.draw.line(screen, self.color, (head_x, arm_joint_y), (left_end_x, left_end_y), 3)
        pygame.draw.circle(screen, self.color, (int(left_end_x), int(left_end_y)), int(left_radius))

        thigh_length = 30
        calf_length = 30
        base_bend = 10
        animation_offset = math.sin(self.animation_frame) * 10 if self.is_moving and not self.is_jumping else 0

        if self.is_jumping:
            extra_bend = max(5, min(20, abs(self.jump_velocity) * 1.0))
        else:
            extra_bend = 0

        total_bend = base_bend + extra_bend

        left_knee_x = body_bottom_x - total_bend + animation_offset
        left_knee_y = body_bottom_y + thigh_length
        left_foot_x = left_knee_x
        left_foot_y = left_knee_y + calf_length
        pygame.draw.line(screen, self.color, (body_bottom_x, body_bottom_y), (left_knee_x, left_knee_y), 3)
        pygame.draw.line(screen, self.color, (left_knee_x, left_knee_y), (left_foot_x, left_foot_y), 3)

        right_knee_x = body_bottom_x + total_bend - animation_offset
        right_knee_y = body_bottom_y + thigh_length
        right_foot_x = right_knee_x
        right_foot_y = right_knee_y + calf_length
        pygame.draw.line(screen, self.color, (body_bottom_x, body_bottom_y), (right_knee_x, right_knee_y), 3)
        pygame.draw.line(screen, self.color, (right_knee_x, right_knee_y), (right_foot_x, right_foot_y), 3)

    def check_hit(self, other):
        arm_joint_y = self.y + 15 * self.head_scale + 15
        hit = False

        if self.attacking_right and self.attack_timer_right == self.attack_duration // 2:
            punch_x = self.x + self.arm_length_right
            punch_y = arm_joint_y
            if math.hypot(punch_x - other.x, punch_y - other.y) < 40:
                other.take_damage(10)
                hit = True

        if self.attacking_left and self.attack_timer_left == self.attack_duration // 2:
            punch_x = self.x - self.arm_length_left
            punch_y = arm_joint_y
            if math.hypot(punch_x - other.x, punch_y - other.y) < 40:
                other.take_damage(10)
                hit = True

        return hit
