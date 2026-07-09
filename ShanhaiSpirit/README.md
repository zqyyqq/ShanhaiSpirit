# 《山海灵识》- SIGGRAPH 实时人机交互艺术作品

[![CI/CD](https://github.com/yourusername/ShanhaiSpirit/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/ShanhaiSpirit/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/yourusername/ShanhaiSpirit)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](pyproject.toml)

## 项目简介

《山海灵识》是一款基于计算机视觉技术的实时体感交互艺术装置，以中国上古神话《山海经》为文化载体，通过手部动作召唤和操控上古神兽，实现传统东方美学与实时计算机视觉技术的完美结合。

## 技术栈

- **感知识别**: MediaPipe (Hand手势识别, FaceMesh 468 keypoints)
- **摄像头采集**: OpenCV
- **实时渲染**: OpenCV + PIL (中文文本渲染)
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
pip install -e ".[dev]"

# 运行程序
python -m shanhai.main
```

## 环境要求

- Python 3.9 或更高版本
- 摄像头设备（内置或外接）
- Windows / macOS / Linux
- 至少 2GB 内存
- 支持 OpenGL 3.0+ 的显卡

## 依赖安装

### 使用 pyproject.toml（推荐）

```bash
# 安装核心依赖
pip install -e .

# 安装开发依赖（测试、代码检查等）
pip install -e ".[dev]"
```

### 使用 requirements.txt（兼容方式）

```bash
pip install -r requirements.txt
```

## 运行方式

### 方式一：作为模块运行（推荐）

```bash
python -m shanhai.main
```

### 方式二：直接运行入口脚本

```bash
python src/shanhai/main.py
```

### 方式三：使用命令行工具

```bash
# 安装后可用
shanhai-spirit
```

## 项目结构

```
ShanhaiSpirit/
├── src/                    # 源代码目录
│   └── shanhai/            # 主包
│       ├── __init__.py     # 包初始化
│       ├── config.py       # 配置模块
│       ├── tracker.py      # 追踪器模块（手部+面部）
│       ├── creature.py     # 神兽渲染模块
│       └── main.py         # 主程序入口
├── tests/                  # 测试目录
│   ├── test_tracker.py     # 追踪器测试
│   ├── test_creature.py    # 神兽模块测试
│   └── test_config.py      # 配置测试
├── assets/                 # 资源文件
│   ├── backgrounds/        # 国风背景素材
│   │   ├── kunlun.png      # 昆仑
│   │   ├── desert.png      # 沙漠
│   │   └── sea.png         # 大海
│   └── creatures/          # 神兽素材
│       ├── zhuque/         # 朱雀
│       ├── yinglong/       # 应龙
│       ├── qilin/          # 麒麟
│       └── xuanwu/         # 玄武
├── .github/                # GitHub配置
│   ├── workflows/          # CI/CD工作流
│   │   └── ci.yml          # GitHub Actions配置
│   ├── ISSUE_TEMPLATE/     # Issue模板
│   └── PULL_REQUEST_TEMPLATE/  # PR模板
├── pyproject.toml          # 项目配置（依赖、工具配置）
├── requirements.txt        # 依赖清单（兼容方式）
├── LICENSE                 # MIT许可证
├── CONTRIBUTING.md         # 贡献指南
├── SIGGRAPH_CLASSIFICATION.md  # SIGGRAPH标准分类文档
└── README.md               # 项目说明
```

### SIGGRAPH 标准分类

项目文件按照 SIGGRAPH 计算机图形学会议的标准分类体系进行组织，详见 [SIGGRAPH_CLASSIFICATION.md](SIGGRAPH_CLASSIFICATION.md)。

| 类别 | 描述 | 包含文件 |
|-----|------|---------|
| Core Algorithms | 核心算法模块 | tracker.py（手势识别、运动分析） |
| Rendering | 渲染模块 | creature.py（生物渲染）、main.py（UI渲染） |
| Configuration | 配置模块 | config.py（参数配置、资源路径） |
| Application | 应用框架 | main.py（事件循环、主程序入口） |
| Data | 数据模块 | config.py（生物数据、手势映射） |
| Utilities | 工具模块 | main.py（TextRenderer、InfoBoxRenderer） |
| Infrastructure | 基础设施 | pyproject.toml、CI/CD、测试文件 |

## 交互操作说明

### 手势1：切换背景
- **动作**: 五指完全摊开，手掌向前
- **效果**: 循环切换三种国风背景（昆仑 → 沙漠 → 大海）

### 手势2：召唤神兽
- **动作**: 单手比出数字1/2/3/4
- **对应神兽**:
  - 1指 → 朱雀（《山海经·南次二经》）
  - 2指 → 应龙（《山海经·大荒东经》）
  - 3指 → 麒麟（《山海经·海内经》）
  - 4指 → 玄武（《山海经·北山经》）

### 手势3：神兽跟随
- **动作**: 移动手部
- **效果**: 召唤的神兽会跟随手部位置实时移动，神兽下方会显示简介信息框

### 神兽简介显示
- 召唤神兽后，信息框会自动显示在神兽下方
- 包含神兽名称、《山海经》描述及来源引用

## 神兽图鉴

| 神兽 | 手势 | 描述 | 来源 |
|------|------|------|------|
| 朱雀 | 1指 | 南方有鸟，其名曰朱雀，丹身而赤目，六足四翼，见则天下大旱。 | 《山海经·南次二经》 |
| 应龙 | 2指 | 应龙处南极，杀蚩尤与夸父，不得复上，故下数旱。旱而为应龙之状，乃得大雨。 | 《山海经·大荒东经》 |
| 麒麟 | 3指 | 麟，仁兽也。麇身牛尾，狼额马蹄，有五彩，腹下黄，高丈二。 | 《山海经·海内经》 |
| 玄武 | 4指 | 北方有神龟，其名曰玄武，龟蛇相缠，能通幽冥，知未来之事。 | 《山海经·北山经》 |

## 配置说明

主要配置项位于 `src/shanhai/config.py`：

- **RENDER_WIDTH/HEIGHT**: 窗口分辨率（默认1920×1080）
- **CREATURE_SIZE**: 神兽显示尺寸（默认350px）
- **CREATURE_SPEED_FACTOR**: 神兽跟随速度（默认0.3）
- **GESTURE_COOLDOWN_MS**: 手势冷却时间（默认800ms）
- **CAMERA_INDEX**: 摄像头索引（默认0）
- **MIN_DETECTION_CONFIDENCE**: 检测置信度阈值（默认0.5）

## 性能优化

- **帧速率控制**: 稳定30FPS，使用time.sleep(1/30)控制
- **手势防抖**: 手势切换有1秒冷却期，防止误操作
- **平滑插值**: 神兽位置采用线性插值，画面流畅

## 退出程序

- 按下键盘 `Q` 键退出

## 开发指南

### 代码风格

项目使用以下工具进行代码质量保证：

```bash
# 代码格式化
black .

# 代码检查
ruff check .

# 类型检查
mypy src/

# 运行测试
pytest tests/ -v

# 测试覆盖率
pytest --cov=src tests/
```

### 添加新功能

1. 在 `src/shanhai/` 目录下创建新模块或修改现有模块
2. 在 `tests/` 目录下添加对应的测试文件
3. 确保通过所有代码检查和测试
4. 提交代码时遵循 [贡献指南](CONTRIBUTING.md)

## 常见问题

### Q: 无法打开摄像头
A: 请确保摄像头已正确连接，并且没有被其他程序占用。可以尝试修改 `config.py` 中的 `CAMERA_INDEX` 值（通常为0或1）。

### Q: 手势识别不准确
A: 请确保在光线充足的环境下使用，手部与摄像头保持适当距离（约30-60cm）。可以调整 `MIN_DETECTION_CONFIDENCE` 和 `MIN_TRACKING_CONFIDENCE` 参数。

### Q: 帧率过低
A: 请关闭其他占用摄像头或GPU资源的程序。可以尝试降低 `RENDER_WIDTH` 和 `RENDER_HEIGHT` 分辨率。

### Q: 中文显示乱码
A: 程序会自动查找系统中的中文字体（微软雅黑、黑体、宋体）。如果在非Windows系统上运行，请确保已安装中文字体。

## 版本说明

### v1.0.0
- 初始版本
- 支持四种神兽（朱雀、应龙、麒麟、玄武）
- 支持三种背景切换
- 基于 MediaPipe 的手势识别
- OpenCV 实时渲染

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE)。

## 贡献

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献流程。

## 联系方式

如有问题或建议，可以通过以下方式联系：

- 创建 [Issue](https://github.com/yourusername/ShanhaiSpirit/issues)
- 发送邮件到：your@email.com
