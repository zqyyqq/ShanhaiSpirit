"""
《山海灵识》国风粒子系统模块
基于 pygame 实现双体系粒子效果：祥光体系 + 水墨祥云体系
"""

import pygame
import math
import random


def draw_cloud_shape(surface, center_x, center_y, size, color):
    """绘制云形状"""
    cx, cy = center_x, center_y
    s = size / 2
    
    points = [
        (cx - s * 0.8, cy),
        (cx - s * 0.6, cy - s * 0.3),
        (cx - s * 0.3, cy - s * 0.2),
        (cx, cy - s * 0.4),
        (cx + s * 0.3, cy - s * 0.2),
        (cx + s * 0.6, cy - s * 0.3),
        (cx + s * 0.8, cy),
        (cx + s * 0.5, cy + s * 0.2),
        (cx + s * 0.2, cy + s * 0.3),
        (cx, cy + s * 0.25),
        (cx - s * 0.2, cy + s * 0.3),
        (cx - s * 0.5, cy + s * 0.2),
    ]
    
    pygame.draw.polygon(surface, color, points)


def draw_cloud_layers(surface, center_x, center_y, size, alpha, base_color):
    """绘制多层次云形状"""
    layer1_color = (*base_color, int(alpha * 0.8))
    layer2_color = (*base_color, int(alpha * 0.5))
    layer3_color = (*base_color, int(alpha * 0.3))
    
    draw_cloud_shape(surface, center_x, center_y, size * 0.7, layer1_color)
    draw_cloud_shape(surface, center_x - size * 0.2, center_y + size * 0.1, size * 0.5, layer2_color)
    draw_cloud_shape(surface, center_x + size * 0.2, center_y - size * 0.1, size * 0.5, layer2_color)
    draw_cloud_shape(surface, center_x, center_y + size * 0.15, size * 0.4, layer3_color)


class AuraBurstParticle:
    """召唤爆发祥光粒子"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.025)
        self.size = random.uniform(20, 40)
        
        self.gold_color = (255, 220, 100)

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        self.vy -= 0.08 * dt * 60
        
        self.vx *= 0.98
        self.vy *= 0.98
        
        self.life -= self.decay * dt * 60
        self.size *= 0.99

    def draw(self, screen):
        if self.life <= 0:
            return
        
        alpha = int(self.life * 150)
        size = max(10, int(self.size))
        
        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        draw_cloud_layers(surface, size, size, size, alpha, self.gold_color)
        
        screen.blit(surface, (self.x - size, self.y - size))


class TrailParticle:
    """流光拖尾祥云粒子"""

    def __init__(self, x, y, color=(255, 220, 100)):
        self.x = x
        self.y = y
        
        self.vx = random.uniform(2, 5)
        self.vy = random.uniform(-1, 1)
        
        self.life = 1.0
        self.decay = random.uniform(0.008, 0.015)
        self.size = random.uniform(25, 50)
        
        self.wobble_speed = random.uniform(0.03, 0.06)
        self.wobble_offset = random.uniform(0, 2 * math.pi)
        self.wobble_amplitude = random.uniform(5, 15)
        
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        self.wobble_offset += self.wobble_speed * dt * 60
        self.y += math.sin(self.wobble_offset) * self.wobble_amplitude * dt * 60
        
        self.life -= self.decay * dt * 60
        self.size *= 0.995

    def draw(self, screen):
        if self.life <= 0:
            return
        
        alpha = int(self.life * 120)
        size = max(15, int(self.size))
        
        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        draw_cloud_layers(surface, size, size, size, alpha, self.color)
        
        screen.blit(surface, (self.x - size, self.y - size))


# 祥云布局配置：每个yun图片对应特定位置和大小
# 位置相对于神兽中心：offset_x(水平偏移), offset_y(垂直偏移，正值向下)
# size: 基础大小
CLOUD_LAYOUT = {
    0: {"name": "yun1", "pos": "神兽中下偏右下", "offset_x": (120, 200), "offset_y": (100, 160), "size": (160, 220), "behind": False},
    1: {"name": "yun2", "pos": "神兽中下偏左下", "offset_x": (-200, -120), "offset_y": (100, 160), "size": (160, 220), "behind": False},
    2: {"name": "yun3", "pos": "神兽中下（大）", "offset_x": (-40, 40), "offset_y": (120, 180), "size": (260, 360), "behind": False},
    3: {"name": "yun4", "pos": "神兽中下偏左下", "offset_x": (-220, -140), "offset_y": (100, 160), "size": (160, 220), "behind": False},
    4: {"name": "yun5", "pos": "神兽中上（大，包裹）", "offset_x": (-280, 280), "offset_y": (-160, -60), "size": (400, 520), "behind": False},
    5: {"name": "yun6", "pos": "神兽中下偏右下", "offset_x": (140, 220), "offset_y": (100, 160), "size": (160, 220), "behind": False},
    6: {"name": "yun7", "pos": "神兽正后面偏下", "offset_x": (-30, 30), "offset_y": (80, 140), "size": (220, 300), "behind": True},
}

class CloudParticle:
    """围绕神兽的祥云粒子 - 根据布局固定位置"""

    def __init__(self, center_x, center_y, cloud_image, layout_config, color=(230, 245, 240)):
        # 根据布局配置生成位置
        ox_range = layout_config["offset_x"]
        oy_range = layout_config["offset_y"]
        self.offset_x = random.uniform(*ox_range)
        self.offset_y = random.uniform(*oy_range)
        self.x = center_x + self.offset_x
        self.y = center_y + self.offset_y
        
        # 浮动参数（轻微浮动）
        self.float_speed_x = random.uniform(0.3, 0.8)
        self.float_speed_y = random.uniform(0.2, 0.5)
        self.float_amplitude_x = random.uniform(2, 5)
        self.float_amplitude_y = random.uniform(1, 3)
        self.phase_x = random.uniform(0, 2 * math.pi)
        self.phase_y = random.uniform(0, 2 * math.pi)
        
        self.life = 1.0
        self.decay = 0  # 不衰减，云永久存在
        
        size_range = layout_config["size"]
        self.size = random.uniform(*size_range)
        
        self.cloud_image = cloud_image
        self.color = color
        self.time = 0
        self.z_index = 0  # 用于分层渲染
        self.behind = layout_config.get("behind", False)  # 是否在神兽后面

    def update(self, dt, center_x, center_y):
        self.time += dt
        
        # 跟随神兽位置 + 固定偏移 + 轻微浮动
        float_x = math.sin(self.time * self.float_speed_x + self.phase_x) * self.float_amplitude_x
        float_y = math.sin(self.time * self.float_speed_y + self.phase_y) * self.float_amplitude_y
        
        self.x = center_x + self.offset_x + float_x
        self.y = center_y + self.offset_y + float_y
        
        # 生命周期衰减
        self.life -= self.decay * dt * 60

    def draw(self, screen):
        if self.life <= 0:
            return
        
        alpha = int(self.life * 200)  # 提高透明度
        size = max(30, int(self.size * self.life))
        
        if self.cloud_image:
            # 使用云图片
            scaled_img = pygame.transform.scale(self.cloud_image, (int(size), int(size)))
            # 创建半透明表面并调整整体透明度
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            surface.blit(scaled_img, (0, 0))
            # 用BLEND_RGBA_MULT调整整体透明度（比set_alpha更可靠）
            surface.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            img_rect = surface.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(surface, img_rect)
        else:
            # 程序生成云
            surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            draw_cloud_layers(surface, size, size, size, alpha, self.color)
            screen.blit(surface, (int(self.x) - size, int(self.y) - size))


class FireParticle:
    """朱雀喷火粒子 - 向下扩散的火焰效果"""

    def __init__(self, x, y, direction="right"):
        self.x = x
        self.y = y
        
        # 火焰以向下扩散为主，带水平分量
        angle = random.uniform(-0.5, 0.5)  # 水平扩散角度
        base_speed = random.uniform(3, 6)
        
        # 主要向下，带水平分量
        if direction == "right":
            self.vx = base_speed * 0.6 * math.cos(angle) + random.uniform(-0.5, 0.5)
            self.vy = base_speed * math.sin(angle) + random.uniform(3, 5)  # 主要向下
        elif direction == "left":
            self.vx = -base_speed * 0.6 * math.cos(angle) + random.uniform(-0.5, 0.5)
            self.vy = base_speed * math.sin(angle) + random.uniform(3, 5)  # 主要向下
        else:
            self.vx = base_speed * 0.3 * math.cos(angle)
            self.vy = base_speed * 1.2 * math.sin(angle) + random.uniform(3, 5)
        
        self.life = 1.0
        self.decay = random.uniform(0.012, 0.025)  # 生命周期更长
        self.size = random.uniform(40, 70)  # 更大的火焰尺寸
        
        # 更丰富的火焰颜色渐变：白→黄→橙→红→深红→烟
        self.colors = [
            (255, 255, 240),  # 核心 - 近白
            (255, 245, 200),  # 亮黄
            (255, 220, 100),  # 金黄
            (255, 170, 50),   # 橙黄
            (255, 120, 40),   # 橙红
            (255, 70, 30),    # 红色
            (220, 50, 20),    # 深红
            (180, 40, 20),    # 暗红
        ]
        
        self.wobble = random.uniform(0, 2 * math.pi)
        self.grow_factor = 0  # 火焰先长大再缩小

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # 火焰向下飘动 + 重力加速
        self.vy += 0.08 * dt * 60  # 向下加速
        self.vy += 0.03 * dt * 60  # 轻微重力
        
        # 火焰摆动
        self.wobble += 0.15 * dt * 60
        self.x += math.sin(self.wobble) * 0.8 * dt * 60
        
        # 火焰水平扩散
        self.vx += random.uniform(-0.1, 0.1) * dt * 60
        
        # 速度衰减
        self.vx *= 0.96
        self.vy *= 0.98
        
        # 生命周期衰减
        self.life -= self.decay * dt * 60
        
        # 火焰先长大再缩小
        if self.life > 0.7:
            self.size *= 1.02  # 膨胀阶段
        else:
            self.size *= 0.94  # 收缩阶段

    def draw(self, screen):
        if self.life <= 0:
            return
        
        size = max(3, int(self.size))
        surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        
        # 绘制多层火焰 - 从外到内
        num_layers = len(self.colors)
        for i, color in enumerate(reversed(self.colors)):
            layer_idx = num_layers - 1 - i
            # 外层更大，内层更小
            layer_scale = 1.0 - (num_layers - 1 - layer_idx) * 0.12
            layer_size = max(2, int(size * layer_scale))
            
            # 透明度：内层更亮，外层更淡；后期整体变暗
            alpha_factor = self.life * (1.0 - layer_idx * 0.12)
            # 初期更亮
            if self.life > 0.5:
                alpha_factor *= 1.2
            alpha = min(255, int(alpha_factor * 220))
            
            if alpha <= 0 or layer_size <= 0:
                continue
            
            # 火焰形状 - 狭长的水滴形
            # 外层更宽更短，内层更细更长
            width = layer_size * 1.5
            height = layer_size * 2.2
            
            # 位置居中偏下（火焰根部）
            x_pos = size * 1.5 - width // 2
            y_pos = size * 1.5 - height // 2 + layer_size * 0.3
            
            pygame.draw.ellipse(surface, (*color, alpha),
                              (int(x_pos), int(y_pos), int(width), int(height)))
        
        screen.blit(surface, (int(self.x) - size * 1.5, int(self.y) - size * 1.5))


class WaterParticle:
    """玄武喷水粒子 - 向左下扩散的水柱/水花效果"""

    def __init__(self, x, y, direction="right"):
        self.x = x
        self.y = y
        
        # 喷水以向左下扩散为主
        angle = random.uniform(-0.5, 0.5)  # 垂直扩散角度
        base_speed = random.uniform(4, 7)
        
        # 主要向左下，带垂直分量
        # direction参数控制水平方向，但整体向左下喷
        self.vx = -base_speed * 0.8 * math.cos(angle) + random.uniform(-1, 1)  # 向左
        self.vy = base_speed * math.sin(angle) + random.uniform(3, 5)  # 向下
        
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.02)  # 生命周期
        self.size = random.uniform(20, 45)  # 水滴尺寸
        
        # 水的颜色渐变：白→浅蓝→蓝→深蓝
        self.colors = [
            (240, 248, 255),  # 核心 - 近白
            (200, 230, 255),  # 浅蓝白
            (150, 200, 255),  # 浅蓝
            (100, 180, 240),  # 淡蓝
            (60, 150, 220),   # 中蓝
            (30, 120, 200),   # 蓝色
            (20, 80, 160),    # 深蓝
        ]
        
        self.wobble = random.uniform(0, 2 * math.pi)

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        
        # 喷水向左下，受重力影响继续下落
        self.vy += 0.15 * dt * 60  # 重力使其下落
        self.vx -= 0.02 * dt * 60  # 继续向左加速
        
        # 水花摆动
        self.wobble += 0.2 * dt * 60
        self.y += math.sin(self.wobble) * 1.0 * dt * 60
        
        # 水滴扩散
        self.vx += random.uniform(-0.15, 0.15) * dt * 60
        self.vy += random.uniform(-0.1, 0.1) * dt * 60
        
        # 速度衰减
        self.vx *= 0.95
        self.vy *= 0.99
        
        # 生命周期衰减
        self.life -= self.decay * dt * 60
        
        # 水滴逐渐变小
        self.size *= 0.96

    def draw(self, screen):
        if self.life <= 0:
            return
        
        size = max(2, int(self.size))
        surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        
        # 绘制多层水滴 - 从外到内
        num_layers = len(self.colors)
        for i, color in enumerate(reversed(self.colors)):
            layer_idx = num_layers - 1 - i
            # 外层更大，内层更小
            layer_scale = 1.0 - (num_layers - 1 - layer_idx) * 0.12
            layer_size = max(2, int(size * layer_scale))
            
            # 透明度：内层更亮，外层更淡
            alpha_factor = self.life * (1.0 - layer_idx * 0.1)
            if self.life > 0.5:
                alpha_factor *= 1.3
            alpha = min(255, int(alpha_factor * 200))
            
            if alpha <= 0 or layer_size <= 0:
                continue
            
            # 水滴形状 - 椭圆形
            width = layer_size * 1.3
            height = layer_size * 1.8
            
            # 位置居中
            x_pos = size * 1.5 - width // 2
            y_pos = size * 1.5 - height // 2
            
            pygame.draw.ellipse(surface, (*color, alpha),
                              (int(x_pos), int(y_pos), int(width), int(height)))
        
        screen.blit(surface, (int(self.x) - size * 1.5, int(self.y) - size * 1.5))


class ParticleManager:
    """粒子系统统一管理器"""

    CREATURE_COLORS = {
        "zhuque": (255, 180, 160),
        "yinglong": (255, 220, 150),
        "qilin": (100, 100, 110),
        "xuanwu": (160, 220, 180),
    }

    def __init__(self, screen_width, screen_height, cloud_images=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.cloud_images = cloud_images if cloud_images else []
        
        self.burst_particles = []
        self.trail_particles = []
        self.cloud_particles = []
        self.fire_particles = []
        self.water_particles = []  # 新增喷水粒子
        self.thunder_particles = []  # 打雷粒子
        self.screen_flash = None  # 全屏闪光效果
        
        self.cloud_enabled = True
        self.trail_enabled = False
        self.burst_enabled = False
        self.fire_enabled = False
        self.water_enabled = False
        self.thunder_enabled = False
        self.last_trail_time = 0
        self.last_cloud_time = 0
        self.last_fire_time = 0
        self.last_water_time = 0
        self.last_thunder_time = 0
        
        self.trail_interval = 0.12
        self.cloud_interval = 2.0  # 减少云生成频率
        self.fire_interval = 0.015  # 更密集的火焰
        self.water_interval = 0.02  # 喷水间隔
        
        self.current_creature_id = None
        self.current_color = (230, 245, 240)
        self.fire_direction = "right"  # 火焰喷出方向
        self.water_direction = "right"  # 喷水方向
        self.creature_cloud_spawned = False  # 标记是否已为当前神兽生成祥云布局

    def spawn_cloud_layout(self, center_x, center_y):
        """根据布局配置生成所有祥云"""
        if not self.cloud_enabled:
            return
        self.cloud_particles.clear()
        # 按z_index排序：yun7在最底层，yun5在最顶层
        # 顺序：yun7(后面), yun2, yun4, yun1, yun6, yun3, yun5(前面)
        render_order = [6, 1, 3, 0, 5, 2, 4]
        for idx in render_order:
            if idx < len(self.cloud_images):
                cloud_img = self.cloud_images[idx]
                config = CLOUD_LAYOUT[idx]
                p = CloudParticle(center_x, center_y, cloud_img, config, self.current_color)
                p.z_index = idx
                self.cloud_particles.append(p)

    def spawn_random_cloud(self, center_x, center_y):
        """生成一个随机祥云（新云出现时旧云消失）"""
        if len(self.cloud_images) == 0:
            return
        # 自动开启祥云
        self.cloud_enabled = True
        # 清除旧云
        self.cloud_particles.clear()
        idx = random.randint(0, min(len(self.cloud_images), len(CLOUD_LAYOUT)) - 1)
        cloud_img = self.cloud_images[idx]
        config = CLOUD_LAYOUT[idx]
        p = CloudParticle(center_x, center_y, cloud_img, config, self.current_color)
        p.z_index = idx
        self.cloud_particles.append(p)
        # 限制云数量
        if len(self.cloud_particles) > 15:
            self.cloud_particles.pop(0)

    def spawn_burst(self, center_x, center_y, count=50):
        """生成召唤爆发祥光"""
        if not self.burst_enabled:
            return
        for _ in range(count):
            self.burst_particles.append(AuraBurstParticle(center_x, center_y))

    def spawn_fire(self, x, y, direction="right", count=1):
        """生成火焰粒子"""
        for _ in range(count):
            self.fire_particles.append(FireParticle(x, y, direction))

    def set_fire_enabled(self, enabled):
        """开启/关闭火焰"""
        self.fire_enabled = enabled
        if not enabled:
            self.fire_particles.clear()

    def set_fire_direction(self, direction):
        """设置火焰喷出方向"""
        self.fire_direction = direction

    def set_water_enabled(self, enabled):
        """开启/关闭喷水"""
        self.water_enabled = enabled
        if not enabled:
            self.water_particles.clear()

    def set_water_direction(self, direction):
        """设置喷水方向"""
        self.water_direction = direction

    def set_thunder_enabled(self, enabled):
        """开启/关闭打雷"""
        self.thunder_enabled = enabled
        if not enabled:
            self.thunder_particles.clear()

    def spawn_thunder(self, x, y):
        """生成打雷粒子效果"""
        # 闪电：从上方垂直下来的白光
        self.thunder_particles.append(ThunderParticle(x, y))
        # 同时生成大量闪光粒子
        for _ in range(60):
            self.thunder_particles.append(ThunderFlashParticle(x, y))
        # 触发全屏闪光（更亮更持久）
        self.screen_flash = ScreenFlash(duration=0.5)

    def toggle_cloud(self):
        """开启/关闭祥云生成"""
        self.cloud_enabled = not self.cloud_enabled
        if not self.cloud_enabled:
            self.cloud_particles.clear()

    def update(self, dt, beast_pos=None, creature_id=None):
        """更新所有粒子"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        if creature_id and creature_id != self.current_creature_id:
            self.current_creature_id = creature_id
            self.current_color = self.CREATURE_COLORS.get(creature_id, (230, 245, 240))
        
        if beast_pos and self.trail_enabled and current_time - self.last_trail_time > self.trail_interval:
            self.trail_particles.append(TrailParticle(beast_pos[0], beast_pos[1], self.current_color))
            self.last_trail_time = current_time
        
        if beast_pos:
            for p in self.cloud_particles:
                p.update(dt, beast_pos[0], beast_pos[1])
        else:
            for p in self.cloud_particles:
                p.update(dt, self.screen_width // 2, self.screen_height // 2)
        self.cloud_particles = [p for p in self.cloud_particles if p.life > 0]
        
        for p in self.trail_particles:
            p.update(dt)
        self.trail_particles = [p for p in self.trail_particles if p.life > 0]
        
        for p in self.burst_particles:
            p.update(dt)
        self.burst_particles = [p for p in self.burst_particles if p.life > 0]
        
        # 持续喷火效果 - 每次生成多个火焰粒子
        if beast_pos and self.fire_enabled and current_time - self.last_fire_time > self.fire_interval:
            # 朱雀嘴部位置 - 向左移一点
            fire_offset_x = -self.screen_width * 0.02  # 向左移动
            fire_base_x = beast_pos[0] + fire_offset_x
            fire_base_y = beast_pos[1] - self.screen_height * 0.02  # 中间高度
            
            # 每次生成5-8个火焰粒子
            num_fires = random.randint(5, 8)
            for _ in range(num_fires):
                # 添加随机偏移模拟火焰扩散
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-15, 10)
                self.fire_particles.append(FireParticle(
                    fire_base_x + offset_x,
                    fire_base_y + offset_y,
                    self.fire_direction
                ))
            self.last_fire_time = current_time
        
        # 更新火焰粒子
        for p in self.fire_particles:
            p.update(dt)
        self.fire_particles = [p for p in self.fire_particles if p.life > 0]
        
        # 持续喷水效果 - 每次生成多个水滴粒子
        if beast_pos and self.water_enabled and current_time - self.last_water_time > self.water_interval:
            # 玄武嘴部位置 - 向左移一点
            water_offset_x = -self.screen_width * 0.07  # 更向左
            water_base_x = beast_pos[0] + water_offset_x
            water_base_y = beast_pos[1] - self.screen_height * 0.08  # 上方
            
            # 每次生成4-7个水滴粒子
            num_waters = random.randint(4, 7)
            for _ in range(num_waters):
                # 添加随机偏移模拟水花扩散
                offset_x = random.uniform(-10, 10)
                offset_y = random.uniform(-15, 10)
                self.water_particles.append(WaterParticle(
                    water_base_x + offset_x,
                    water_base_y + offset_y,
                    self.water_direction
                ))
            self.last_water_time = current_time
        
        # 更新水滴粒子
        for p in self.water_particles:
            p.update(dt)
        self.water_particles = [p for p in self.water_particles if p.life > 0]
        
        # 更新打雷粒子
        for p in self.thunder_particles:
            p.update(dt)
        self.thunder_particles = [p for p in self.thunder_particles if p.life > 0]
        
        # 更新屏幕闪光
        if self.screen_flash:
            self.screen_flash.update(dt)
            if self.screen_flash.life <= 0:
                self.screen_flash = None

    def draw(self, screen):
        """绘制所有粒子"""
        # 祥云按z_index排序：yun7(后面)先画，yun5(前面)后画
        sorted_clouds = sorted(self.cloud_particles, key=lambda p: p.z_index)
        for p in sorted_clouds:
            p.draw(screen)
        
        for p in self.trail_particles:
            p.draw(screen)
        
        for p in self.burst_particles:
            p.draw(screen)
        
        # 绘制火焰粒子（在最上层）
        for p in self.fire_particles:
            p.draw(screen)
        
        # 绘制喷水粒子（在最上层）
        for p in self.water_particles:
            p.draw(screen)
        
        # 绘制打雷粒子（在最上层）
        for p in self.thunder_particles:
            p.draw(screen)
    
    def draw_cloud_behind(self, screen):
        """只绘制神兽后面的云（yun7）"""
        behind_clouds = [p for p in self.cloud_particles if p.behind]
        for p in behind_clouds:
            p.draw(screen)
    
    def draw_cloud_front(self, screen):
        """只绘制神兽前面的云（yun1-6）"""
        front_clouds = sorted([p for p in self.cloud_particles if not p.behind], key=lambda p: p.z_index)
        for p in front_clouds:
            p.draw(screen)
    
    def draw_screen_flash(self, screen):
        """绘制屏幕闪光效果"""
        if self.screen_flash:
            self.screen_flash.draw(screen)

    def draw_cloud_only(self, screen):
        """只绘制云粒子"""
        sorted_clouds = sorted(self.cloud_particles, key=lambda p: p.z_index)
        for p in sorted_clouds:
            p.draw(screen)

    def draw_effects_only(self, screen):
        """只绘制拖尾和爆发粒子"""
        for p in self.trail_particles:
            p.draw(screen)
        
        for p in self.burst_particles:
            p.draw(screen)

class ThunderParticle:
    """闪电粒子 - 从上方垂直下来的白光"""
    
    def __init__(self, target_x, target_y):
        self.start_x = target_x + random.uniform(-50, 50)
        self.start_y = -30  # 稍微在屏幕外
        self.target_x = target_x
        self.target_y = target_y
        self.progress = 0
        self.life = 1.0
        self.max_life = 0.6  # 总生命周期0.6秒
        self.speed = 3.0  # 闪电下落速度（降低，让动画更慢）
        # 闪电路径（之字形）- 更多段数让闪电更曲折
        self.segments = []
        num_segments = 12
        for i in range(num_segments + 1):
            t = i / num_segments
            x = self.start_x + (self.target_x - self.start_x) * t + random.uniform(-30, 30)
            y = self.start_y + (self.target_y - self.start_y) * t
            self.segments.append((x, y))
    
    def update(self, dt):
        self.progress += self.speed * dt
        self.life -= dt / self.max_life  # 按总生命周期衰减
        if self.progress > 1.0:
            self.progress = 1.0
    
    def draw(self, screen):
        if self.life <= 0:
            return
        # 绘制闪电 - 使用更高的alpha和更粗的线条
        alpha = int(min(1.0, self.progress) * min(1.0, self.life * 2) * 255)
        if alpha <= 0:
            return
        pts = []
        max_seg = int(len(self.segments) * min(1.0, self.progress))
        for i in range(min(max_seg + 1, len(self.segments))):
            pts.append((int(self.segments[i][0]), int(self.segments[i][1])))
        if len(pts) >= 2:
            # 外发光层（更粗）
            pygame.draw.lines(screen, (180, 200, 255, alpha), False, pts, 16)
            # 中发光层
            pygame.draw.lines(screen, (200, 220, 255, alpha), False, pts, 10)
            # 内发光层
            pygame.draw.lines(screen, (230, 240, 255, alpha), False, pts, 6)
            # 核心白线
            pygame.draw.lines(screen, (255, 255, 255, alpha), False, pts, 3)

class ThunderFlashParticle:
    """打雷闪光粒子"""
    
    def __init__(self, target_x, target_y):
        self.x = target_x + random.uniform(-20, 20)
        self.y = target_y + random.uniform(-20, 20)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 300)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(0.3, 0.8)
        self.max_life = self.life
        self.size = random.uniform(3, 8)
        self.color = (200, 220, 255)  # 蓝白色闪电
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= dt
    
    def draw(self, screen):
        if self.life <= 0:
            return
        alpha = int((self.life / self.max_life) * 255)
        r = max(1, int(self.size * (self.life / self.max_life)))
        pygame.draw.circle(screen, (self.color[0], self.color[1], self.color[2], alpha), (int(self.x), int(self.y)), r)

class ScreenFlash:
    """全屏闪光效果 - 模拟闪电瞬间照亮整个屏幕"""
    
    def __init__(self, duration=0.5):
        self.life = duration
        self.max_life = duration
        self.color = (255, 255, 255)
    
    def update(self, dt):
        self.life -= dt
    
    def draw(self, screen):
        if self.life <= 0:
            return
        # 快速衰减的白色闪光
        t = self.life / self.max_life
        alpha = int(t * 255)  # 最大透明度（更亮）
        if alpha <= 0:
            return
        # 整个屏幕覆盖白色半透明
        flash_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        flash_surface.fill((230, 240, 255, alpha))  # 略带蓝色的白光
        screen.blit(flash_surface, (0, 0))
