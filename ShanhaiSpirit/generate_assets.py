from PIL import Image, ImageDraw
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "creatures")

CREATURES = {
    "fenghuang": {
        "name": "凤凰",
        "colors": {
            "body": (255, 120, 50),
            "head": (255, 150, 80),
            "tail": (255, 180, 100),
            "limb": (200, 100, 50),
            "mouth": (255, 80, 40),
            "eye": (20, 20, 30),
            "white": (255, 255, 255),
            "wing": (255, 200, 120)
        },
        "num_tails": 3
    },
    "yinglong": {
        "name": "应龙",
        "colors": {
            "body": (100, 150, 255),
            "head": (120, 170, 255),
            "tail": (80, 130, 230),
            "limb": (80, 120, 220),
            "mouth": (40, 60, 120),
            "eye": (20, 30, 60),
            "white": (255, 255, 255),
            "wing": (140, 190, 255)
        },
        "num_tails": 1
    },
    "qilin": {
        "name": "麒麟",
        "colors": {
            "body": (255, 215, 0),
            "head": (255, 230, 100),
            "tail": (200, 180, 50),
            "limb": (220, 190, 60),
            "mouth": (180, 150, 40),
            "eye": (30, 25, 10),
            "white": (255, 255, 255),
            "horn": (255, 255, 255)
        },
        "num_tails": 1
    },
    "baize": {
        "name": "白泽",
        "colors": {
            "body": (240, 240, 240),
            "head": (255, 255, 255),
            "tail": (200, 200, 200),
            "limb": (220, 220, 220),
            "mouth": (100, 90, 80),
            "eye": (30, 30, 40),
            "white": (255, 255, 255)
        },
        "num_tails": 1
    }
}

SIZE = 200
CENTER = SIZE // 2

def create_head(creature_id):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = CREATURES[creature_id]["colors"]
    
    draw.ellipse([CENTER-45, CENTER-50, CENTER+45, CENTER+30], fill=c["head"], outline=(0,0,0,100), width=2)
    
    draw.ellipse([CENTER-25, CENTER-35, CENTER-10, CENTER-15], fill=c["white"], outline=(0,0,0,80))
    draw.ellipse([CENTER+10, CENTER-35, CENTER+25, CENTER-15], fill=c["white"], outline=(0,0,0,80))
    
    draw.ellipse([CENTER-22, CENTER-30, CENTER-13, CENTER-20], fill=c["eye"])
    draw.ellipse([CENTER+13, CENTER-30, CENTER+22, CENTER-20], fill=c["eye"])
    
    draw.ellipse([CENTER-20, CENTER-32, CENTER-16, CENTER-27], fill=c["white"])
    draw.ellipse([CENTER+16, CENTER-32, CENTER+20, CENTER-27], fill=c["white"])
    
    if creature_id == "fenghuang":
        draw.polygon([(CENTER, CENTER-70), (CENTER-5, CENTER-55), (CENTER+5, CENTER-55)], fill=c["body"], outline=(0,0,0,80))
        draw.polygon([(CENTER-15, CENTER-65), (CENTER-20, CENTER-50), (CENTER-10, CENTER-55)], fill=c["body"], outline=(0,0,0,80))
        draw.polygon([(CENTER+15, CENTER-65), (CENTER+20, CENTER-50), (CENTER+10, CENTER-55)], fill=c["body"], outline=(0,0,0,80))
    
    if creature_id == "qilin":
        draw.line([(CENTER, CENTER-65), (CENTER, CENTER-90)], fill=c["horn"], width=6)
        draw.polygon([(CENTER-8, CENTER-90), (CENTER+8, CENTER-90), (CENTER, CENTER-100)], fill=c["horn"], outline=(0,0,0,80))
    
    if creature_id == "baize":
        draw.polygon([(CENTER-45, CENTER-50), (CENTER-65, CENTER-70), (CENTER-30, CENTER-45)], fill=c["head"], outline=(0,0,0,80))
        draw.polygon([(CENTER+45, CENTER-50), (CENTER+65, CENTER-70), (CENTER+30, CENTER-45)], fill=c["head"], outline=(0,0,0,80))
    
    return img

def create_mouth_open(creature_id):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = CREATURES[creature_id]["colors"]
    
    if creature_id == "taotie":
        draw.ellipse([CENTER-30, CENTER-5, CENTER+30, CENTER+25], fill=c["mouth"])
        draw.polygon([(CENTER-25, CENTER), (CENTER-20, CENTER+5), (CENTER-25, CENTER+10)], fill="red")
        draw.polygon([(CENTER-15, CENTER), (CENTER-10, CENTER+5), (CENTER-15, CENTER+10)], fill="red")
        draw.polygon([(CENTER-5, CENTER), (CENTER, CENTER+5), (CENTER-5, CENTER+10)], fill="red")
        draw.polygon([(CENTER+5, CENTER), (CENTER+10, CENTER+5), (CENTER+5, CENTER+10)], fill="red")
        draw.polygon([(CENTER+15, CENTER), (CENTER+20, CENTER+5), (CENTER+15, CENTER+10)], fill="red")
        draw.polygon([(CENTER+25, CENTER), (CENTER+30, CENTER+5), (CENTER+25, CENTER+10)], fill="red")
        draw.line([CENTER-28, CENTER+5, CENTER+28, CENTER+5], fill=(255,255,255), width=2)
    else:
        draw.arc([CENTER-15, CENTER-5, CENTER+15, CENTER+20], 0, 3.14, fill=c["mouth"], width=3)
        draw.line([CENTER-12, CENTER+5, CENTER+12, CENTER+5], fill=c["mouth"], width=2)
        draw.ellipse([CENTER-14, CENTER+5, CENTER+14, CENTER+20], fill=c["mouth"])
    
    return img

def create_mouth_closed(creature_id):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = CREATURES[creature_id]["colors"]
    
    draw.line([CENTER-15, CENTER+5, CENTER+15, CENTER+5], fill=c["mouth"], width=3)
    
    return img

def create_body(creature_id):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = CREATURES[creature_id]["colors"]
    
    draw.ellipse([CENTER-50, CENTER-20, CENTER+50, CENTER+50], fill=c["body"], outline=(0,0,0,100), width=2)
    
    return img

def create_limb(creature_id, position):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = CREATURES[creature_id]["colors"]
    
    if position.startswith("front"):
        draw.line([CENTER-5, CENTER-10, CENTER-5, CENTER+40], fill=c["limb"], width=8)
        draw.ellipse([CENTER-10, CENTER+35, CENTER, CENTER+45], fill=c["limb"], outline=(0,0,0,80))
    else:
        draw.line([CENTER-5, CENTER-10, CENTER-5, CENTER-50], fill=c["limb"], width=8)
        draw.ellipse([CENTER-10, CENTER-55, CENTER, CENTER-45], fill=c["limb"], outline=(0,0,0,80))
    
    if position.endswith("left"):
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    
    return img

def create_tail(creature_id):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = CREATURES[creature_id]["colors"]
    
    if creature_id == "jiuweihu":
        for i in range(9):
            angle_offset = (i - 4) * 0.2
            start_x = CENTER + math.sin(angle_offset) * 10
            start_y = CENTER - 40 + math.cos(angle_offset) * 5
            end_x = CENTER + math.sin(angle_offset + 1.5) * 60
            end_y = CENTER - 40 + math.cos(angle_offset + 1.5) * 60
            tail_color = (
                c["tail"][0] - i*8,
                c["tail"][1] - i*6,
                c["tail"][2] - i*4
            )
            draw.line([start_x, start_y, end_x, end_y], fill=tail_color, width=6 - i//2)
    elif creature_id == "yinglong":
        draw.line([CENTER, CENTER-40, CENTER-30, CENTER-90], fill=c["tail"], width=12)
        draw.line([CENTER-30, CENTER-90, CENTER-50, CENTER-80], fill=c["tail"], width=8)
        draw.line([CENTER-30, CENTER-90, CENTER-20, CENTER-100], fill=c["tail"], width=8)
    else:
        draw.line([CENTER, CENTER-40, CENTER, CENTER-80], fill=c["tail"], width=10)
        draw.ellipse([CENTER-20, CENTER-90, CENTER+20, CENTER-70], fill=c["tail"], outline=(0,0,0,80))
    
    return img

def create_wing(creature_id, side):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = CREATURES[creature_id]["colors"]
    
    if side == "left":
        draw.polygon([
            (CENTER, CENTER),
            (CENTER-80, CENTER-30),
            (CENTER-60, CENTER+20),
            (CENTER-20, CENTER+10)
        ], fill=c["wing"], outline=(0,0,0,60))
    else:
        draw.polygon([
            (CENTER, CENTER),
            (CENTER+80, CENTER-30),
            (CENTER+60, CENTER+20),
            (CENTER+20, CENTER+10)
        ], fill=c["wing"], outline=(0,0,0,60))
    
    return img

if __name__ == "__main__":
    import math
    
    for creature_id, info in CREATURES.items():
        creature_dir = os.path.join(ASSETS_DIR, creature_id)
        os.makedirs(creature_dir, exist_ok=True)
        
        print(f"正在生成 {info['name']} 素材...")
        
        head = create_head(creature_id)
        head.save(os.path.join(creature_dir, f"{creature_id}_head.png"))
        
        mouth_open = create_mouth_open(creature_id)
        mouth_open.save(os.path.join(creature_dir, f"{creature_id}_mouth_open.png"))
        
        mouth_closed = create_mouth_closed(creature_id)
        mouth_closed.save(os.path.join(creature_dir, f"{creature_id}_mouth_closed.png"))
        
        body = create_body(creature_id)
        body.save(os.path.join(creature_dir, f"{creature_id}_body.png"))
        
        limb_fl = create_limb(creature_id, "front_left")
        limb_fl.save(os.path.join(creature_dir, f"{creature_id}_limb_front_left.png"))
        
        limb_fr = create_limb(creature_id, "front_right")
        limb_fr.save(os.path.join(creature_dir, f"{creature_id}_limb_front_right.png"))
        
        limb_bl = create_limb(creature_id, "back_left")
        limb_bl.save(os.path.join(creature_dir, f"{creature_id}_limb_back_left.png"))
        
        limb_br = create_limb(creature_id, "back_right")
        limb_br.save(os.path.join(creature_dir, f"{creature_id}_limb_back_right.png"))
        
        tail = create_tail(creature_id)
        tail.save(os.path.join(creature_dir, f"{creature_id}_tail.png"))
        
        if creature_id == "yinglong":
            wing_left = create_wing(creature_id, "left")
            wing_left.save(os.path.join(creature_dir, f"{creature_id}_wing_left.png"))
            
            wing_right = create_wing(creature_id, "right")
            wing_right.save(os.path.join(creature_dir, f"{creature_id}_wing_right.png"))
        
        print(f"  ✓ {info['name']} 素材生成完成")
    
    print("\n所有素材生成完毕！")