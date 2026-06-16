# AI 测试 Agent 平台

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于大语言模型的智能测试平台，通过 Prompt Engineering 驱动多个专业 Agent 协同工作，覆盖测试全流程：**需求解析 → 用例生成 → 脚本生成 → 缺陷分析**，目标将测试设计效率提升 50% 以上。

## ✨ 核心特性

- 🎯 **需求智能解析** - 自动拆解自然语言需求为结构化测试点，识别优先级和依赖关系
- 📋 **测试用例生成** - 基于需求自动生成标准化测试用例，支持 Excel/CSV/JSON 导出
- 💻 **多类型脚本生成** - 一键生成接口测试（pytest）、UI 自动化（Selenium）、性能测试（JMeter）脚本
- 🔍 **缺陷智能分析** - 自动分类缺陷类型，输出根因分析报告和修复建议
- 🔄 **多轮交互调整** - 支持对生成结果提出修改意见，Agent 根据反馈重新生成
- 🔒 **本地数据存储** - 所有数据存储在本地，云端不保存任何记录，保障数据安全
- 🌐 **Web UI 界面** - 提供友好的可视化操作界面，开箱即用

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────┐
│                   Web UI / API                    │
├─────────────────────────────────────────────────┤
│              API Layer (FastAPI)                  │
├──────────┬──────────┬──────────┬────────────────┤
│ 需求解析  │ 用例生成  │ 脚本生成  │  缺陷分析       │
│  Agent   │  Agent   │  Agent   │   Agent        │
├──────────┴──────────┴──────────┴────────────────┤
│          Prompt Engine (YAML + LLM)               │
├─────────────────────────────────────────────────┤
│          LLM API (OpenAI Compatible)              │
├─────────────────────────────────────────────────┤
│        输出管理 (本地文件/报告)                     │
└─────────────────────────────────────────────────┘
```

## 📦 技术栈

| 类别 | 技术选型 |
|------|----------|
| 后端框架 | Python 3.10+ / FastAPI |
| 大模型接入 | Agnes-AI（OpenAI API 兼容格式）|
| Prompt 管理 | YAML 模板 + Prompt Engine |
| 接口测试 | requests + pytest |
| UI 自动化 | Selenium WebDriver |
| 性能测试 | JMeter（JMX 生成 + CLI 执行）|
| 数据存储 | 本地文件存储（JSON/Markdown）|
| 前端界面 | FastAPI + Jinja2 模板 |

## 🚀 快速开始

### 环境要求

- Python 3.10 或更高版本
- Agnes-AI API Key（或其他兼容 OpenAI API 的大模型服务）
- JMeter 5.6+（可选，用于性能测试脚本执行）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/youlinaixujiang/test_helper.git
cd test_helper
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：
```env
# Agnes-AI 配置
AGNES_API_KEY=your_api_key_here
AGNES_BASE_URL=https://api.agnes-ai.com/v1
AGNES_MODEL=agnes-ai-latest

# JMeter 配置（可选）
JMETER_HOME=apache-jmeter-5.6.3
```

4. **启动服务**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. **访问应用**

打开浏览器访问：http://localhost:8000

## 📖 使用指南

### API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/requirement/parse | 解析测试需求 |
| POST | /api/v1/testcase/generate | 生成测试用例 |
| POST | /api/v1/script/generate | 生成测试脚本 |
| POST | /api/v1/defect/analyze | 缺陷分类与根因分析 |
| GET | /api/v1/health | 健康检查 |

### 使用流程

#### 1. 需求解析

输入自然语言测试需求，Agent 会自动拆解为结构化的测试点：

**示例输入：**
> "请测试用户登录功能，包括正常登录、密码错误、账号不存在、验证码错误等场景，并验证登录后的 token 有效性"

**输出：** 结构化的测试点列表，包含优先级、前置条件等信息

#### 2. 测试用例生成

基于需求解析结果，自动生成标准化测试用例：
- 用例编号、模块、标题
- 前置条件、测试步骤、预期结果
- 优先级（P0/P1/P2/P3）
- 类型（功能/接口/性能/安全）

#### 3. 脚本生成

根据测试用例自动生成可执行的测试脚本：

**接口测试脚本（pytest + requests）：**
```python
import pytest
import requests

class TestUserLogin:
    BASE_URL = "http://localhost:8080"
    
    def test_normal_login(self):
        resp = requests.post(f"{self.BASE_URL}/api/login", json={
            "username": "test_user",
            "password": "correct_password"
        })
        assert resp.status_code == 200
        assert "token" in resp.json()
```

**UI 自动化脚本（Selenium）** 和 **性能测试脚本（JMeter JMX）** 同样支持一键生成

#### 4. 缺陷分析

输入测试执行结果，Agent 自动进行缺陷分类和根因分析：
- 功能缺陷（functional）
- 性能缺陷（performance）
- 安全缺陷（security）
- 兼容性缺陷（compatibility）
- 数据问题（data）
- 环境问题（environment）

## 📁 项目结构

```
test_helper/
├── app/
│   ├── main.py                    # FastAPI 入口
│   ├── config.py                  # 配置管理
│   ├── agents/                    # Agent 模块
│   │   ├── base_agent.py          # Agent 基类
│   │   ├── requirement_agent.py   # 需求解析 Agent
│   │   ├── testcase_agent.py      # 用例生成 Agent
│   │   ├── script_agent.py        # 脚本生成 Agent
│   │   └── defect_agent.py        # 缺陷分析 Agent
│   ├── prompts/                   # Prompt 模板
│   │   ├── requirement.yaml
│   │   ├── testcase.yaml
│   │   ├── script_api.yaml
│   │   ├── script_ui.yaml
│   │   ├── script_jmeter.yaml
│   │   └── defect.yaml
│   ├── core/                      # 核心组件
│   │   ├── llm_client.py          # LLM API 调用封装
│   │   └── prompt_engine.py       # Prompt 模板引擎
│   ├── generators/                # 生成器
│   │   ├── script_generator.py
│   │   └── report_generator.py
│   ├── models/                    # 数据模型
│   ├── api/                       # API 路由
│   ├── static/                    # 静态文件
│   └── templates/                 # HTML 模板
├── outputs/                       # 输出目录
│   ├── testcases/                 # 生成的测试用例
│   ├── scripts/                   # 生成的测试脚本
│   ├── reports/                   # 分析报告
│   └── jmeter_results/            # JMeter 执行结果
├── apache-jmeter-5.6.3/           # JMeter 安装目录
├── docs/                          # 文档
├── requirements.txt
└── .env.example
```

## 🔧 配置说明

### 大模型配置

平台默认使用 Agnes-AI，也支持其他兼容 OpenAI API 的服务：

```env
AGNES_API_KEY=your_api_key
AGNES_BASE_URL=https://your-api-endpoint/v1
AGNES_MODEL=your-model-name
```

### JMeter 配置

如果需要执行性能测试脚本，需要配置 JMeter：

```env
JMETER_HOME=/path/to/apache-jmeter-5.6.3
```

平台会自动检测项目根目录下的 `apache-jmeter-5.6.3` 目录。

## 💡 Prompt 设计策略

- **Few-shot + Chain of Thought** - 引导 LLM 进行深度推理
- **temperature=0.3** - 保证输出结果的稳定性
- **System Prompt** - 定义 Agent 角色和专业领域
- **JSON 格式输出** - 统一输出格式，便于程序解析
- **多示例引导** - 每个 Agent 预设 2-3 个 Few-shot 示例

## 🔒 数据安全

- ✅ 所有数据存储于本地 `outputs` 目录
- ✅ 用户自主选择保存位置
- ✅ 云端不保存任何测试数据
- ✅ 支持手动清理历史数据

## 📊 输出示例

所有生成的文件都保存在 `outputs/` 目录下：

- `outputs/testcases/` - 测试用例文件（JSON/Excel）
- `outputs/scripts/` - 测试脚本（Python/JMX）
- `outputs/reports/` - 分析报告（Markdown）
- `outputs/jmeter_results/` - 性能测试结果（JTL/HTML 报告）

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📝 开发计划

- [ ] 支持更多大模型（通义千问、文心一言等）
- [ ] 增加测试用例管理界面
- [ ] 支持团队协作功能
- [ ] 集成 CI/CD  pipeline
- [ ] 增加测试报告可视化
- [ ] 支持更多测试类型（安全测试、兼容性测试等）

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📧 联系方式

- 项目地址：https://github.com/youlinaixujiang/test_helper
- 问题反馈：提交 Issue 或联系作者

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代高效的 Python Web 框架
- [OpenAI Python SDK](https://github.com/openai/openai-python) - LLM API 调用
- [Apache JMeter](https://jmeter.apache.org/) - 性能测试工具
- [pytest](https://docs.pytest.org/) - Python 测试框架

---

⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！
