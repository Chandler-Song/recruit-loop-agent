# loop-agent-cli

> Typer + Rich CLI for [recruit-loop-agent](https://github.com/Chandler-Song/recruit-loop-agent) — 在终端中完成招聘循环的全部操作，无需启动 FastAPI Web 服务。

## 功能特性

- **零服务依赖**：不启动 uvicorn，直接在进程内调用核心引擎
- **完整功能覆盖**：职位管理、候选人查看、管道操作、循环执行、调度控制、仪表盘
- **终端友好**：Rich 彩色表格/面板，结构化输出

## 安装

```bash
# 从 PyPI 安装（正式发布后）
pip install loop-agent-cli

# 开发模式安装（从项目根目录）
cd recruit-loop-agent
pip install -e .
```

## 前置条件

- Python >= 3.9
- `.env` 文件需存在于项目根目录（配置 `GITHUB_TOKEN`、`SMTP_*`、`LLM_*` 等）
- 项目根目录需包含 `app/` 核心引擎包

## 大模型（LLM）配置

项目的 Agent 节点（评分、邮件生成、循环判断）通过 LLM 驱动，支持所有 **OpenAI 兼容接口**。

### 配置方式

在项目根目录的 `.env` 文件中设置以下环境变量：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `LLM_API_BASE_URL` | API 地址（OpenAI 兼容 endpoint） | 无（必填） |
| `LLM_API_KEY` | API 密钥 / Token | 无（必填） |
| `LLM_MODEL_NAME` | 模型名称 | `gpt-4o` |
| `LLM_TEMPERATURE` | 生成温度 | `0.7` |
| `LLM_MAX_TOKENS` | 最大输出 token 数 | `2048` |
| `LLM_TIMEOUT` | 请求超时时间（秒） | `60` |

### 支持的服务商

只需更换 `LLM_API_BASE_URL` 和 `LLM_API_KEY` 即可切换，代码无需修改：

| 服务商 | `LLM_API_BASE_URL` | `LLM_MODEL_NAME` 示例 |
|-------|-------------------|----------------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o`, `gpt-4o-mini` |
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat`, `deepseek-reasoner` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus`, `qwen-max` |
| 智谱 AI | `https://open.bigmodel.cn/api/paas/v4` | `glm-4`, `glm-4-flash` |
| Moonshot | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
| Ollama（本地） | `http://localhost:11434/v1` | `llama3`, `qwen2:7b` |

### 配置示例

```bash
# .env 文件（以 DeepSeek 为例）
LLM_API_BASE_URL=https://api.deepseek.com
LLM_API_KEY=sk-your-deepseek-api-key
LLM_MODEL_NAME=deepseek-chat
```

> **注意**：如果未配置 LLM，Agent 节点会自动回退到规则引擎（技能匹配评分、模板邮件等），核心流程不受影响。

## 使用示例

### 查看帮助

```bash
loop-agent --help
```

### 职位管理

```bash
# 列出所有职位
loop-agent position list

# 创建新职位
loop-agent position create -t "Senior Backend Engineer" -c "Tech Corp" \
  -s "Python,FastAPI,PostgreSQL" -k "backend,python,remote"

# 查看职位详情
loop-agent position show <position_id>

# 关闭职位
loop-agent position close <position_id>
```

### 执行招聘循环

```bash
# 对已有职位执行一次循环
loop-agent run position <position_id>

# 创建职位并立即执行循环
loop-agent run create-and-run -t "Python Developer" -c "Startup Inc" \
  -s "Python,Django" -i 30
```

### 候选人管理

```bash
# 列出候选人（默认 20 条）
loop-agent candidate list -n 10

# 查看候选人详情
loop-agent candidate show <candidate_id>
```

### 管道管理

```bash
# 列出所有管道
loop-agent pipeline list

# 按职位过滤
loop-agent pipeline list -p <position_id>

# 更新管道状态
loop-agent pipeline update-status <pipeline_id> contacted
```

### 调度管理

```bash
# 启动后台调度器（Ctrl+C 退出）
loop-agent schedule start

# 列出调度任务
loop-agent schedule list
```

### 仪表盘

```bash
# 查看仪表盘摘要
loop-agent dashboard
```

### 其他

```bash
# 显示 LangGraph 图结构
loop-agent graph

# 显示版本信息
loop-agent version
```

### 全局选项

```bash
# 覆盖数据库路径
loop-agent --db sqlite+aiosqlite:///./custom.db position list
```

## 命令树

```
loop-agent
├── run                          执行招聘循环
│   ├── position <position_id>   对已有职位执行一次循环
│   └── create-and-run           创建职位并立即执行循环
├── position                     职位管理
│   ├── list                     列出所有职位
│   ├── create                   创建新职位
│   ├── show <position_id>       查看职位详情
│   └── close <position_id>      关闭职位
├── candidate                    候选人管理
│   ├── list                     列出候选人
│   └── show <candidate_id>      查看候选人详情
├── pipeline                     招聘管道管理
│   ├── list                     列出管道
│   └── update-status            更新管道状态
├── schedule                     调度管理
│   ├── start                    启动后台调度器
│   └── list                     列出调度任务
├── dashboard                    查看仪表盘摘要
├── graph                        显示 LangGraph 图结构
└── version                      显示版本信息
```

## 开发

```bash
# 克隆项目
git clone git@github.com:Chandler-Song/recruit-loop-agent.git
cd recruit-loop-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -e .

# 运行测试
pytest app/tests/ -v
```

## 许可证

MIT License
