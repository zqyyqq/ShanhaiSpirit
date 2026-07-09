# 贡献指南

欢迎你为《山海灵识》项目做出贡献！无论是代码改进、Bug 修复、文档完善还是新功能建议，都非常感谢你的参与。

## 贡献方式

### 1. 提交问题 (Issues)

如果你发现了 Bug 或者有新功能建议，请按照以下步骤操作：

1. 先查看 [已有 Issues](https://github.com/yourusername/ShanhaiSpirit/issues)，确认问题尚未被提交
2. 使用提供的 [Issue 模板](.github/ISSUE_TEMPLATE/bug_report.md) 提交问题
3. 清晰描述问题现象、复现步骤和预期行为

### 2. 提交代码 (Pull Requests)

我们欢迎所有类型的代码贡献：

1. Fork 本仓库到你的 GitHub 账户
2. 创建一个新的分支用于你的修改：
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. 编写代码并确保通过所有测试
4. 提交代码并创建 Pull Request
5. 使用 [PR 模板](.github/PR_TEMPLATE/pull_request_template.md) 填写描述

## 开发规范

### 代码风格

- 使用 `black` 进行代码格式化
- 使用 `ruff` 进行代码检查
- 使用 `mypy` 进行类型检查
- 保持代码简洁，避免不必要的复杂性

### 测试规范

- 为新增功能编写单元测试
- 确保所有测试通过后再提交
- 测试文件应放在 `tests/` 目录下

### 提交规范

提交信息应遵循以下格式：

```
类型: 简短描述

详细描述（可选）

Closes #issue_number（如果关联了 issue）
```

类型包括：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 开发环境设置

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

# 运行测试
pytest

# 代码检查
ruff check .
black .
mypy .
```

## 项目结构

```
ShanhaiSpirit/
├── src/                    # 源代码目录
│   ├── shanhai/            # 主包
│   │   ├── __init__.py
│   │   ├── config.py       # 配置模块
│   │   ├── tracker.py      # 追踪器模块
│   │   ├── creature.py     # 神兽渲染模块
│   │   └── main.py         # 主程序入口
│   └── __init__.py
├── tests/                  # 测试目录
│   ├── test_tracker.py
│   └── test_creature.py
├── assets/                 # 资源文件
├── pyproject.toml          # 项目配置
├── LICENSE                 # 许可证
└── README.md               # 项目说明
```

## 联系我们

如有任何问题或建议，可以通过以下方式联系：

- 创建 [Issue](https://github.com/yourusername/ShanhaiSpirit/issues)
- 发送邮件到：your@email.com

再次感谢你的贡献！
