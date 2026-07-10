# 《山海灵识》

## 项目简介

《山海灵识》是一款实时体感交互艺术装置，以中国上古神话《山海经》为文化载体，通过手部动作召唤和操控上古神兽，实现传统东方美学与实时计算机视觉技术的完美结合。

## 创作背景

以《山海经》中国上古神话为文化载体，结合实时人体视觉追踪，打造沉浸式国风体感交互装置；通过手部动作驱动上古神兽动画，实现传统东方美学与实时计算机视觉技术结合，适合交互式艺术展区展出。

## 技术栈

- **感知识别**: MediaPipe (Hand手势识别 + FaceMesh 面部468关键点)
- **摄像头采集**: OpenCV
- **实时国风画面渲染**: OpenCV + PIL (支持中文文字渲染)
- **语言**: Python 3.9+

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/yourusername/ShanhaiSpirit.git
cd ShanhaiSpirit

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python shanhai_main.py
```

## 环境要求

- Python 3.9 或更高版本
- 摄像头设备（内置或外接）
- Windows / macOS / Linux
- 至少 2GB 内存

## 依赖安装

```bash
# 使用 requirements.txt（推荐）
pip install -r requirements.txt

# 或手动安装核心依赖
pip install numpy opencv-python mediapipe pillow
```

## 运行方式

### 方式一：直接运行主程序（推荐）

```bash
python shanhai_main.py
```

### 方式二：测试追踪模块

```bash
python tracker.py
```

## 项目结构

```
ShanhaiSpirit/
├── tracker.py              # 追踪模块：MediaPipe手部+面部追踪
├── shanhai_main.py         # 主渲染程序：OpenCV实时画面渲染
├── requirements.txt        # 依赖清单
├── pyproject.toml          # 项目配置
├── assets/                 # 资源文件
│   ├── backgrounds/        # 国风背景素材
│   │   ├── sea.png         # 沧海
│   │   ├── desert.png      # 沙漠
│   │   └── kunlun.png      # 昆仑
│   └── creatures/          # 神兽素材
│       ├── zhuque/         # 朱雀
│       │   └── zhuque.png
│       ├── yinglong/       # 应龙
│       │   └── yinglong.png
│       ├── qilin/          # 麒麟
│       │   └── qilin.png
│       └── xuanwu/         # 玄武
│           └── xuanwu.png
├── src/                    # 源代码目录
│   └── shanhai/
│       └── __init__.py
├── tests/                  # 测试文件
│   ├── test_config.py
│   ├── test_creature.py
│   └── test_tracker.py
├── .github/                # GitHub配置
│   ├── workflows/          # CI/CD工作流
│   ├── ISSUE_TEMPLATE/     # Issue模板
│   └── PULL_REQUEST_TEMPLATE/  # PR模板
├── LICENSE                 # MIT许可证
├── CONTRIBUTING.md         # 贡献指南
├── SIGGRAPH_CLASSIFICATION.md  # SIGGRAPH分类说明
└── README.md               # 项目说明
```

## 代码架构

### 核心文件拆分

**① tracker.py** - 独立封装 MediaPipe 手部+面部追踪类

- `HandTracker`: 手部21关键点追踪，手势识别（五指张开、1-4指）
- `FaceTracker`: 面部468关键点追踪，嘴部开合状态检测
- `CombinedTracker`: 整合手部和面部追踪的统一接口

**② shanhai_main.py** - OpenCV主渲染程序

- 接收追踪数据，完成画面绘制
- 实现分层渲染逻辑
- 处理交互逻辑和神兽动画驱动
- 手势调试面板显示

### 分层渲染逻辑

背景层 → 神兽层 → 文字面板层 → 调试信息层

## 交互操作说明

### 手势1：切换背景
- **动作**: 五指完全摊开，手掌向前
- **效果**: 循环切换三种国风背景（沧海 → 沙漠 → 昆仑）

### 手势2：召唤神兽
- **动作**: 单手比出数字1/2/3/4
- **对应神兽**:
  - 1指（仅食指） → 朱雀（《山海经·南次二经》）
  - 2指（食指+中指） → 应龙（《山海经·大荒东经》）
  - 3指（食指+中指+无名指） → 麒麟（《山海经·海内经》）
  - 4指（食指+中指+无名指+小指） → 玄武（《山海经·北山经》）

### 手势3：神兽跟随
- **动作**: 移动手部
- **效果**: 召唤的神兽会跟随手部位置（食指根部关键点）实时移动，采用平滑插值确保流畅

### 神兽简介显示
- 召唤神兽后，在神兽下方弹出古籍样式文字面板
- 包含神兽名称、《山海经》原文介绍（每行17字，最多4行）
- 右下角印有"山海"印章

### 调试面板
- 左下角显示手势检测状态面板
- 实时显示五个手指的状态（伸=绿色，屈=红色）
- 显示当前识别的手势名称

### 键盘操作
- **Q**: 退出程序

## 神兽图鉴

| 神兽 | 手势 | 属性 | 方位 | 原文引用 |
|------|------|------|------|---------|
| 朱雀 | 1指 | 火 | 南 | 《山海经·南次二经》 |
| 应龙 | 2指 | 水 | 中 | 《山海经·大荒东经》 |
| 麒麟 | 3指 | 土 | 东 | 《山海经·海内经》 |
| 玄武 | 4指 | 水 | 北 | 《山海经·北山经》 |

## 性能优化

- **帧速率控制**: 稳定30FPS以上
- **检测置信度优化**: MIN_DETECTION_CONFIDENCE=0.5，降低识别卡顿
- **平滑插值**: 神兽位置采用指数插值（系数0.15），画面流畅
- **手势防抖**: 手势切换有1.5秒冷却期，防止误操作
- **摄像头优化**: 使用 CAP_DSHOW 后端（Windows），避免帧读取延迟

## 国风视觉风格

- **青绿山水**: 低饱和度传统国画色调背景
- **古籍样式**: 文字面板采用传统书籍设计风格，米色宣纸底色
- **印章装饰**: 文字面板右下角"山海"印章
- **角落装饰**: 文字面板四角传统装饰线条

## 退出程序

- 按下键盘 `Q` 键退出
- 或点击窗口关闭按钮

## 开发指南

### 代码风格

项目使用以下工具进行代码质量保证：

```bash
# 代码格式化
black .

# 代码检查
ruff check .

# 类型检查
mypy .

# 运行测试
pytest tests/ -v
```

### 添加新功能

1. 在 `tracker.py` 中添加新的手势识别逻辑
2. 在 `shanhai_main.py` 中添加对应的渲染和交互逻辑
3. 在 `assets/` 目录下添加对应的素材文件

## 常见问题

### Q: 无法打开摄像头
A: 请确保摄像头已正确连接，并且没有被其他程序占用。当前程序使用 CAP_DSHOW 后端（Windows）。

### Q: 手势识别不准确
A: 请确保在光线充足的环境下使用，手部与摄像头保持适当距离（约30-60cm）。可以调整 `tracker.py` 中的 `MIN_DETECTION_CONFIDENCE` 参数（当前为0.5）。

### Q: 帧率过低
A: 请关闭其他占用摄像头或GPU资源的程序。

### Q: 神兽不显示
A: 请确保 `assets/creatures/` 目录下存在对应神兽的PNG图片。

### Q: 中文显示为乱码
A: 程序使用 PIL 加载系统中文字体（黑体、微软雅黑等），请确保系统安装了中文字体。

## 版本说明

### v3.0.0（SIGGRAPH 投稿版本）
- 切换为 OpenCV + PIL 渲染引擎，移除 py5 依赖
- 优化手势识别逻辑，改进无名指和小指检测
- 添加手势调试面板，实时显示手指状态
- 古籍样式文字面板，支持中文渲染
- 平滑插值神兽跟随效果

### v2.0.0
- 重构为 py5 实时渲染引擎
- 独立封装 tracker.py 追踪模块
- 分层渲染架构

### v1.0.0
- 初始版本
- 基于 OpenCV 渲染

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE)。

## 贡献

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献流程。

## 联系方式

如有问题或建议，可以通过以下方式联系：

- 创建 [Issue](https://github.com/yourusername/ShanhaiSpirit/issues)
- 发送邮件到：your@email.com

---

*《山海灵识》- SIGGRAPH 2026 实时人机交互艺术作品*
