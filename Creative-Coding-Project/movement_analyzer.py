# logic.py

from math import sqrt
from collections import deque

class MovementAnalyzer:
    def __init__(self):
        pass

    def _prepare_sequence(self, sequence):
        """
        确保传入的 sequence 是 list 类型
        """
        if isinstance(sequence, deque):
            return list(sequence)
        return sequence

    def moving_dis(self, sequence, index, target):
        col = 0 if target=="x" else 1

        
        sequence = self._prepare_sequence(sequence)
        length = len(sequence)
        return sequence[index][col] - sequence[index - length + 1][col]
    
    def is_jumping(self, sequence, index):
        if self.moving_dis(sequence, index, "y") < -30:
            return True
        return False
    
    def is_moving_left(self, sequence, index):
        if self.moving_dis(sequence, index, "x") < -5:
            return True
        return False
    
    def is_moving_right(self, sequence, index):
        if self.moving_dis(sequence, index, "x") > 5:
            return True
        return False
    
    def is_attacking_right(self, sequence, index):
        if self.moving_dis(sequence, index, "x") > 50:
            return True
        return False
    
    def is_attacking_left(self, sequence, index):
        if self.moving_dis(sequence, index, "x") < -50:
            return True
        return False
    
    def is_defending(self, sequence_left_hand, sequence_right_hand, sequence_head, index_hand, index_head):
        if sequence_left_hand[index_hand][0] > sequence_right_hand[index_hand][0] and sequence_head[index_head][1] > (sequence_left_hand[index_hand][1] + sequence_right_hand[index_hand][1]) / 2:
            return True
        return False

