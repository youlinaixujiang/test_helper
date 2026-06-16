# AI 测试 Agent 平台 - 需求文档

## 一、项目概述

构建一个基于大模型的 AI 测试 Agent 平台，通过 Prompt Engineering 驱动多个专业 Agent 协同工作，覆盖测试全流程：需求解析 → 用例生成 → 脚本生成 → 缺陷分析，目标将测试设计效率提升 50% 以上。

---

## 二、技术栈

| 类别 | 技术选型 |
|------|----------|
| 后端框架 | Python 3.10+ / FastAPI |
| 大模型接入 | Agnes-AI（OpenAI API 兼容格式） |
| Prompt 管理 | YAML 模板 + Jinja2 渲染 |
| 接口测试 | requests + pytest |
| UI 自动化 | Selenium WebDriver |
| 性能测试 | JMeter（JMX 生成 + CLI 执行） |
| 数据存储 | 本地文件存储（JSON/Markdown），用户自主选择保存，云端不存储 |
| 前端 | Web UI（FastAPI + Jinja2 模板） |

---

## 三、核心 Agent 模块

### 3.1 需求解析 Agent（Requirement Agent）

**功能描述：**
- 接收用户输入的自然语言测试需求
- 自动拆解为可测试的功能点列表
- 识别测试范围、优先级、依赖关系
- 输出结构化的测试需求文档

**输入示例：**
> "请测试用户登录功能，包括正常登录、密码错误、账号不存在、验证码错误等场景，并验证登录后的 token 有效性"

**输出示例：**
```json
{
  "feature": "用户登录",
  "test_points": [
    {"id": "TP-001", "scene": "正常登录", "priority": "P0", "precondition": "已有注册账号"},
    {"id": "TP-002", "scene": "密码错误", "priority": "P1", "precondition": "已有注册账号"},
    {"id": "TP-003", "scene": "账号不存在", "priority": "P1", "precondition": "无"},
    {"id": "TP-004", "scene": "验证码错误", "priority": "P1", "precondition": "已获取验证码"},
    {"id": "TP-005", "scene": "Token有效性验证", "priority": "P0", "precondition": "已成功登录"}
  ]
}
```

### 3.2 测试用例生成 Agent（Test Case Agent）

**功能描述：**
- 基于需求解析结果自动生成标准化测试用例
- 包含：用例编号、前置条件、测试步骤、预期结果、优先级
- 支持导出为 Excel/CSV/JSON 格式
- 支持人工审阅与编辑

**输出格式：**
| 字段 | 说明 |
|------|------|
| case_id | 用例编号 |
| module | 所属模块 |
| title | 用例标题 |
| precondition | 前置条件 |
| steps | 测试步骤（编号列表） |
| expected | 预期结果 |
| priority | P0/P1/P2/P3 |
| type | 功能/接口/性能/安全 |

### 3.3 脚本生成 Agent（Script Agent）

**功能描述：**
- **接口测试脚本**：基于用例自动生成 pytest + requests 接口测试代码
- **UI 自动化脚本**：基于用例自动生成 Selenium WebDriver 测试代码
- **性能测试脚本**：自动生成 JMeter JMX 配置文件
- 生成的代码可直接运行，包含断言、数据驱动、前置清理

**接口测试脚本示例：**
```python
import pytest
import requests

class TestUserLogin:
    """用户登录 - 接口测试"""
    
    BASE_URL = "http://localhost:8080"
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
    
    def test_normal_login(self):
        """TC-001: 正常登录"""
        resp = self.session.post(f"{self.BASE_URL}/api/login", json={
            "username": "test_user",
            "password": "correct_password"
        })
        assert resp.status_code == 200
        assert "token" in resp.json()
    
    def test_wrong_password(self):
        """TC-002: 密码错误"""
        resp = self.session.post(f"{self.BASE_URL}/api/login", json={
            "username": "test_user",
            "password": "wrong_password"
        })
        assert resp.status_code == 401
        assert "密码错误" in resp.json()["message"]
```

### 3.4 缺陷分析 Agent（Defect Agent）

**功能描述：**
- 接收测试执行结果（失败用例、错误日志）
- 自动进行缺陷分类（功能缺陷/性能缺陷/安全缺陷/兼容性缺陷）
- 输出根因分析报告
- 建议修复方向

**分类标签：**
- `functional` - 功能缺陷
- `performance` - 性能缺陷  
- `security` - 安全缺陷
- `compatibility` - 兼容性缺陷
- `data` - 数据问题
- `environment` - 环境问题

---

## 四、系统架构

```
┌─────────────────────────────────────────────────┐
│                   Web UI / CLI                    │
├─────────────────────────────────────────────────┤
│                  API Layer (FastAPI)              │
├──────────┬──────────┬──────────┬────────────────┤
│ 需求解析  │ 用例生成  │ 脚本生成  │  缺陷分析       │
│  Agent   │  Agent   │  Agent   │   Agent        │
├──────────┴──────────┴──────────┴────────────────┤
│              Prompt Engine (模板 + LLM)           │
├─────────────────────────────────────────────────┤
│              LLM API (OpenAI 兼容)                │
├─────────────────────────────────────────────────┤
│         输出管理 (文件/报告/数据库)                 │
└─────────────────────────────────────────────────┘
```

---

## 五、模块划分与文件结构

```
test_helper/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 入口
│   ├── config.py                  # 配置管理（LLM Key、模型参数）
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Agent 基类
│   │   ├── requirement_agent.py   # 需求解析 Agent
│   │   ├── testcase_agent.py      # 用例生成 Agent
│   │   ├── script_agent.py        # 脚本生成 Agent
│   │   └── defect_agent.py        # 缺陷分析 Agent
│   ├── prompts/
│   │   ├── requirement.yaml       # 需求解析 Prompt 模板
│   │   ├── testcase.yaml          # 用例生成 Prompt 模板
│   │   ├── script_api.yaml        # 接口脚本 Prompt 模板
│   │   ├── script_ui.yaml         # UI脚本 Prompt 模板
│   │   ├── script_jmeter.yaml     # JMeter脚本 Prompt 模板
│   │   └── defect.yaml            # 缺陷分析 Prompt 模板
│   ├── core/
│   │   ├── __init__.py
│   │   ├── llm_client.py          # LLM API 调用封装
│   │   └── prompt_engine.py       # Prompt 模板引擎
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── script_generator.py    # 脚本生成器（pytest/selenium/jmeter）
│   │   └── report_generator.py    # 报告生成器
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requirement.py         # 需求模型
│   │   ├── testcase.py            # 用例模型
│   │   └── defect.py              # 缺陷模型
│   └── api/
│       ├── __init__.py
│       ├── requirement_api.py     # 需求解析接口
│       ├── testcase_api.py        # 用例生成接口
│       ├── script_api.py          # 脚本生成接口
│       └── defect_api.py          # 缺陷分析接口
├── outputs/                       # 输出目录
│   ├── testcases/                 # 生成的测试用例
│   ├── scripts/                   # 生成的测试脚本
│   └── reports/                   # 分析报告
├── tests/                         # 平台自身测试
├── requirements.txt
└── .env.example
```

---

## 六、API 接口设计

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/requirement/parse | 解析测试需求 |
| POST | /api/v1/testcase/generate | 生成测试用例 |
| POST | /api/v1/script/generate | 生成测试脚本 |
| POST | /api/v1/defect/analyze | 缺陷分类与根因分析 |
| GET  | /api/v1/health | 健康检查 |

---

## 七、Prompts 设计要点

- 采用 **Few-shot + Chain of Thought** 策略引导 LLM 推理
- 设置 `temperature=0.3` 保证输出稳定性
- 使用 **System Prompt** 定义角色，**User Prompt** 承载业务数据
- 输出格式统一要求 JSON，便于程序解析
- 对每个 Agent 预设 2-3 个 Few-shot 示例

---

## 八、已确认的技术决策

1. **大模型选型**：Agnes-AI，API Key 通过环境变量 `AGNES_API_KEY` 配置
2. **前端形态**：Web UI（FastAPI + Jinja2 模板），提供完整的可视化操作界面
3. **JMeter 集成**：先生成 JMX 文件，询问用户是否自动运行。若运行，完成后自动生成缺陷分析文档
4. **数据持久化**：所有数据存于本地 outputs 目录，用户可自主选择保存。云端不保存任何记录
5. **多轮对话**：所有 Agent 均支持多轮交互式调整，用户可对生成结果提出修改意见，Agent 根据反馈重新生成
6. **被测系统**：通用型设计，用户通过配置提供 API Base URL / 页面 URL 等目标系统信息
