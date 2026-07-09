import os
import math
import time
from config import *


class CreatureRenderer:
    def __init__(self, creature_id):
        self.creature_id = creature_id
        self.creature_dir = os.path.join(CREATURES_DIR, creature_id)
        
        self.image_path = os.path.join(self.creature_dir, f"{creature_id}.png")
        
        if not os.path.exists(self.image_path):
            self.image_path = None
        
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
    
    def update(self, target_x, target_y, speed, mouth_open):
        self.target_x = target_x
        self.target_y = target_y
        
        self.x += (self.target_x - self.x) * CREATURE_SPEED_FACTOR
        self.y += (self.target_y - self.y) * CREATURE_SPEED_FACTOR
    
    def draw(self, sketch):
        if self.image_path is None:
            return
        
        sketch.push_matrix()
        sketch.translate(self.x * sketch.width, self.y * sketch.height)
        
        scale = CREATURE_SIZE / 100.0
        sketch.scale(scale)
        
        sketch.image_mode(sketch.CENTER)
        
        img = sketch.load_image(self.image_path)
        sketch.image(img, 0, 0)
        
        sketch.pop_matrix()


class CreatureManager:
    def __init__(self):
        self.active_creature = None
        self.creature_data = None
        self.last_summon_time = 0
    
    def summon_creature(self, gesture_id):
        if gesture_id not in CREATURES_DATA:
            return False
        
        current_time = time.time() * 1000
        if current_time - self.last_summon_time < GESTURE_COOLDOWN_MS:
            return False
        
        creature_info = CREATURES_DATA[gesture_id]
        self.active_creature = CreatureRenderer(creature_info['id'])
        self.creature_data = creature_info
        self.last_summon_time = current_time
        
        return True
    
    def update_creature(self, hand_x, hand_y, speed, mouth_open):
        if self.active_creature:
            self.active_creature.update(hand_x, hand_y, speed, mouth_open)
    
    def draw_creature(self, sketch):
        if self.active_creature:
            self.active_creature.draw(sketch)
    
    def has_active_creature(self):
        return self.active_creature is not None
    
    def get_creature_info(self):
        return self.creature_data