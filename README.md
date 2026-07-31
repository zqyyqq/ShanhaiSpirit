# 《山海异兽》

《山海异兽》是一个基于计算机视觉的实时体感交互艺术项目，通过手势与摄像头识别，用户可以召唤《山海经》中的神兽并与国风场景进行互动。

## 项目简介

本项目以中国古代神话为创作载体，结合 MediaPipe 手部追踪、OpenCV 图像渲染以及实时动画效果，展示一款适合展览与演示的交互式艺术装置。

## 核心功能

- 基于 MediaPipe 的手部关键点追踪与手势识别
- 通过不同手势切换背景、召唤神兽、控制神兽跟随手部移动
- 实时渲染国风背景、神兽动画与古籍样式信息面板
- 支持摄像头输入并提供简洁的交互反馈

## 本地运行 / 部署步骤

### 1. 环境要求

- Python 3.9 或更高
- 可用摄像头
- Windows / macOS / Linux

### 2. 安装依赖

```bash
git clone <your-repo-url>
cd ShanhaiSpirit
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. 启动程序

```bash
python shanhai_main.py
```

### 4. 交互说明

程序通过摄像头识别手势来驱动画面，以下是主要操作方式：

- 展开五指并将手掌朝向摄像头：切换背景场景
- 伸出 1 指：召唤朱雀
- 伸出 2 指：召唤青龙
- 伸出 3 指：召唤白虎
- 伸出 4 指：召唤玄武
- 保持手部在画面中移动：神兽会跟随手部位置实时移动
- 双手握拳：显示当前神兽的简介说明
- 当朱雀已被召唤时，伸出大拇指：朱雀喷火
- 当青龙已被召唤时，伸出大拇指：青龙打雷
- 当玄武已被召唤时，伸出大拇指：玄武喷水
- 张开嘴巴：神兽会发出叫声
- 识别到两只手，并且两手都伸出食指和中指：随机出现祥云图案
- 轻微收拢手掌或切换到其他手势：可切换当前神兽或取消当前状态
- 按下 Q 键：退出程序

> 说明：建议在光线充足、背景干净的环境中使用，手势识别效果会更稳定。

## 技术栈

- Python 3.9+
- OpenCV：摄像头采集与实时画面渲染
- MediaPipe：手部关键点检测与手势识别
- NumPy：数值计算与图像处理
- Pillow：中文文字与图像处理
- pygame：音效播放与简单交互支持
- 粒子系统：基于 pygame 的火焰、喷水、雷电、祥云特效渲染

## 项目结构

```text
ShanhaiSpirit/
├── tracker.py           # 手部与面部追踪逻辑
├── shanhai_main.py      # 主程序入口
├── particle.py          # 粒子特效相关逻辑
├── assets/              # 背景、神兽、音效与启动资源
├── tests/               # 单元测试
├── requirements.txt     # Python 依赖
└── pyproject.toml       # 项目配置
```

## 贡献说明

欢迎对项目提出建议或提交改进。你可以先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献方式。

## 许可证

本项目采用 MIT 许可证，详情请查看 [LICENSE](LICENSE)。
