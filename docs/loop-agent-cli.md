# spec.md — loop-agent-cli

> 规格说明文档：定义 `loop_agent_cli` 包的功能边界、接口契约、数据流与约束。

---

## 1. 项目概述

### 1.1 定位

`loop-agent-cli` 是 `recruit-loop-agent` 项目的命令行前端，基于 Typer + Rich 构建，让用户无需启动 FastAPI Web 服务即可在终端中完成招聘循环的全部操作。

### 1.2 核心价值

- **零服务依赖**：不启动 uvicorn，直接在进程内调用核心引擎
- **完整功能覆盖**：职位管理、候选人查看、管道操作、循环执行、调度控制、仪表盘
- **终端友好**：Rich 彩色表格/面板/进度条，结构化输出

### 1.3 边界

| 属于 | 不属于 |
|------|--------|
| CLI 命令定义与参数解析 | 核心业务逻辑（由 `app/` 提供） |
| 终端输出格式化（Rich） | HTTP API 层 |
| 依赖注入容器（Container） | 数据库 Schema / ORM 模型 |
| 异步协程到同步 CLI 的桥接 | LangGraph 图定义 |

---

## 2. 文件结构

```
loop_agent_cli/
├── __init__.py       # 包标识，版本声明
├── cli.py            # Typer CLI 主入口，所有命令定义
└── container.py      # DI 容器，统一构建 Service / Repository
```

| 文件 | 行数 | 职责 |
|------|------|------|
| `__init__.py` | 3 | 包标识 |
| `cli.py` | ~700 | 15 个命令 + 3 个辅助函数 |
| `container.py` | ~168 | Container 类，7 个 Repository 属性 + 7 个 Service 属性 |

---

## 3. 依赖关系

### 3.1 外部依赖

| 包 | 版本要求 | 用途 |
|----|---------|------|
| `typer` | >=0.9.0 | CLI 框架，命令定义与参数解析 |
| `rich` | >=13.0.0 | 终端输出格式化（Table/Panel/Progress） |
| `fastapi` | >=0.104.0 | 间接依赖（app 层需要） |
| `sqlalchemy[asyncio]` | >=2.0.23 | 异步数据库引擎 |
| `aiosqlite` | >=0.19.0 | SQLite 异步驱动 |
| `pydantic` | >=2.5.0 | 数据校验 |
| `pydantic-settings` | >=2.1.0 | 环境变量配置 |
| `httpx` | >=0.25.0 | GitHub API HTTP 客户端 |
| `langgraph` | >=0.0.40 | 招聘循环图引擎 |
| `apscheduler` | >=3.10.0 | 定时调度 |
| `python-dotenv` | >=1.0.0 | .env 文件加载 |
| `cryptography` | >=41.0.0 | SMTP TLS |

### 3.2 内部依赖（`app/` 包）

Container 通过 `sys.path` 注入项目根目录，直接导入 `app` 包中的模块：

```
container.py 导入链:
  app.core.config          → settings
  app.database.base        → Base
  app.database.session     → AsyncSessionLocal
  app.repositories.*       → 7 个 Repository
  app.services.*           → 7 个 Service
  app.schemas.position     → PositionCreate (cli.py 中延迟导入)
```

### 3.3 依赖注入图

```
Container
  │
  ├── _db (AsyncSession)
  │     ↑
  │     ├── PositionRepository(db)
  │     ├── CandidateRepository(db)
  │     ├── PipelineRepository(db)
  │     ├── OutreachLogRepository(db)
  │     ├── AgentRunRepository(db)
  │     ├── NodeLogRepository(db)
  │     └── SchedulerJobRepository(db)
  │
  ├── CandidateService(candidate_repo)
  │     └── SearchService(candidate_service)
  ├── ScoreService()
  ├── PipelineService(pipeline_repo)
  ├── EmailService(outreach_log_repo)
  ├── PositionService(position_repo)
  ├── DashboardService(5 repos)
  ├── RunnerService(4 services + 5 repos)
  └── SchedulerService(position_repo, scheduler_job_repo, runner)
```

---

## 4. Container 类规格

### 4.1 类签名

```python
class Container:
    def __init__(self, db_url: Optional[str] = None): ...
    async def __aenter__(self) -> Container: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...
```

### 4.2 生命周期

| 阶段 | 操作 |
|------|------|
| `__aenter__` | 1. 根据 `db_url` 或 `settings.database_url` 创建异步引擎<br>2. `Base.metadata.create_all` 确保表存在<br>3. 创建 `AsyncSession` 实例 |
| 使用中 | 通过 property 按需创建 Repository / Service 实例 |
| `__aexit__` | 1. 关闭 `AsyncSession`<br>2. 销毁引擎 |

### 4.3 Property 清单

**Repositories（7 个）**：

| Property | 返回类型 | 构造参数 |
|----------|---------|---------|
| `position_repo` | `PositionRepository` | `db` |
| `candidate_repo` | `CandidateRepository` | `db` |
| `pipeline_repo` | `PipelineRepository` | `db` |
| `outreach_log_repo` | `OutreachLogRepository` | `db` |
| `agent_run_repo` | `AgentRunRepository` | `db` |
| `node_log_repo` | `NodeLogRepository` | `db` |
| `scheduler_job_repo` | `SchedulerJobRepository` | `db` |

**Services（7 个）**：

| Property | 返回类型 | 构造参数 |
|----------|---------|---------|
| `candidate_service` | `CandidateService` | `candidate_repo` |
| `search_service` | `SearchService` | `candidate_service` |
| `score_service` | `ScoreService` | 无 |
| `pipeline_service` | `PipelineService` | `pipeline_repo` |
| `email_service` | `EmailService` | `outreach_log_repo` |
| `position_service` | `PositionService` | `position_repo` |
| `dashboard_service` | `DashboardService` | `position_repo`, `agent_run_repo`, `pipeline_repo`, `candidate_repo`, `node_log_repo` |
| `runner` | `RunnerService` | `search_service`, `score_service`, `pipeline_service`, `email_service`, `candidate_repo`, `position_repo`, `pipeline_repo`, `outreach_log_repo`, `agent_run_repo`, `node_log_repo` |
| `scheduler` | `SchedulerService` | `position_repo`, `scheduler_job_repo`, `runner` |

### 4.4 约束

- 每次 `property` 访问都创建新实例（无缓存），适用于 CLI 单次执行场景
- `db_url` 为 `None` 时回退到 `settings.database_url`
- 引擎 `echo=False`，不输出 SQL 日志

---

## 5. CLI 命令规格

### 5.1 命令树

```
loop-agent
├── run                          [命令组] 执行招聘循环
│   ├── position <position_id>   对已有职位执行一次循环
│   └── create-and-run           创建职位并立即执行循环
├── position                     [命令组] 职位管理
│   ├── list                     列出所有职位
│   ├── create                   创建新职位
│   ├── show <position_id>       查看职位详情
│   └── close <position_id>      关闭职位
├── candidate                    [命令组] 候选人管理
│   ├── list                     列出候选人
│   └── show <candidate_id>      查看候选人详情
├── pipeline                     [命令组] 招聘管道管理
│   ├── list                     列出管道
│   └── update-status <id> <status>  更新管道状态
├── schedule                     [命令组] 调度管理
│   ├── start                    启动后台调度器
│   └── list                     列出调度任务
├── dashboard                    查看仪表盘摘要
├── graph                        显示 LangGraph 图结构
└── version                      显示版本信息
```

### 5.2 全局选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--db` | `Optional[str]` | `None` | 覆盖数据库 URL，所有命令通用 |

### 5.3 各命令详细规格

---

#### `run position`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent run position <position_id> [--db URL]` |
| 参数 | `position_id: str` (必填，UUID 格式) |
| 选项 | `--db` |
| 前置校验 | UUID 格式校验、职位存在性校验 |
| 核心调用 | `Container.runner.run_recruiting_loop(position_id)` |
| 输出 | Rich Panel（成功/失败） |

**输出字段**：

| 字段 | 来源 |
|------|------|
| Candidates found | `result["results"]["candidates_found"]` |
| Candidates added | `result["results"]["candidates_added"]` |
| Emails sent | `result["results"]["emails_sent"]` |
| Duration | `result["duration_ms"]` |
| Continue loop | `result["results"]["continue_loop"]` |
| Errors | `result["results"]["errors"]` |

---

#### `run create-and-run`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent run create-and-run -t TITLE -c COMPANY [OPTIONS]` |
| 必填选项 | `--title/-t`, `--company/-c` |
| 可选选项 | `--desc/-d`, `--location/-l`, `--skills/-s`, `--keywords/-k`, `--interval/-i` (默认 60), `--db` |
| 核心调用 | 1. `PositionRepository.create(PositionCreate(...))`<br>2. `Container.runner.run_recruiting_loop(position.id)` |
| 输出 | 创建确认 + Rich Panel（运行结果） |

**`--skills` / `--keywords` 解析规则**（`_parse_json_or_file`）：

1. 尝试 `json.loads(value)` → 如果是 list 则返回
2. 尝试 `os.path.isfile(value)` → 读取文件内容
   - 文件内容尝试 JSON 解析
   - 失败则按行分割
3. 按 `,` 分割

---

#### `position list`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent position list [--db URL]` |
| 核心调用 | `Container.position_repo.get_all()` |
| 输出 | Rich Table |

**表格列**：

| 列 | 字段 | 样式 |
|----|------|------|
| ID | `position.id` | dim, max_width=36 |
| Title | `position.title` | cyan |
| Company | `position.company` | green |
| Status | `position.status` | active=green, paused=yellow, closed=red |
| Skills | `position.required_skills_list` (截断 40 字符) | - |
| Loop | `loop_interval + "m"` 或 `"off"` | 居中 |

---

#### `position create`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent position create -t TITLE -c COMPANY [OPTIONS]` |
| 必填选项 | `--title/-t`, `--company/-c` |
| 可选选项 | `--desc/-d`, `--location/-l`, `--skills/-s`, `--keywords/-k`, `--interval/-i` (默认 60), `--db` |
| 核心调用 | `Container.position_repo.create(PositionCreate(...))` |
| 输出 | 创建确认（标题 + ID） |

---

#### `position show`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent position show <position_id> [--db URL]` |
| 参数 | `position_id: str` (必填，UUID) |
| 核心调用 | `Container.position_repo.get_by_id(pid)` |
| 输出 | Rich Panel |

**面板字段**：ID, Status, Location, Description, Skills, Keywords, Loop (enabled/disabled + interval), Created

---

#### `position close`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent position close <position_id> [--db URL]` |
| 参数 | `position_id: str` (必填，UUID) |
| 核心调用 | `Container.position_service.close_position(pid)` |
| 输出 | 关闭确认 |

---

#### `candidate list`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent candidate list [--limit N] [--db URL]` |
| 选项 | `--limit/-n` (默认 20), `--db` |
| 核心调用 | `Container.candidate_repo.get_all()` → 截取前 N 条 |
| 输出 | Rich Table |

**表格列**：ID, Name, GitHub, Company, Followers, Repos, Source

---

#### `candidate show`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent candidate show <candidate_id> [--db URL]` |
| 参数 | `candidate_id: str` (必填，UUID) |
| 核心调用 | `Container.candidate_repo.get_by_id(cid)` |
| 输出 | Rich Panel |

**面板字段**：ID, GitHub, Email, Company, Title, Location, Bio (截断 80 字符), Skills, Followers, Public Repos, Source, Appearances

---

#### `pipeline list`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent pipeline list [--position ID] [--status STATUS] [--db URL]` |
| 选项 | `--position/-p` (按职位过滤), `--status/-s` (按状态过滤), `--db` |
| 核心调用 | `pipeline_repo.get_by_position(pid)` / `pipeline_repo.get_by_status(status)` / `pipeline_repo.get_all()` |
| 输出 | Rich Table |

**表格列**：ID, Position, Candidate, Status (颜色编码), Score, Notes

**状态颜色映射**：

| 状态 | 颜色 |
|------|------|
| discovered | dim |
| contacted | yellow |
| replied | green |
| interview | cyan |
| offer | bold green |
| rejected | red |

---

#### `pipeline update-status`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent pipeline update-status <pipeline_id> <status> [--db URL]` |
| 参数 | `pipeline_id: str` (UUID), `status: str` |
| 前置校验 | UUID 格式、status 枚举值校验 |
| 合法 status 值 | `discovered`, `contacted`, `replied`, `interview`, `offer`, `rejected` |
| 核心调用 | `Container.pipeline_service.update_pipeline_status(pid, status)` |
| 输出 | 更新确认 |

---

#### `schedule start`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent schedule start [--db URL]` |
| 核心调用 | `Container.scheduler.start()` → `while True: await asyncio.sleep(1)` |
| 退出方式 | `Ctrl+C` → `scheduler.stop()` |
| 输出 | 启动/停止提示 |

**行为**：启动 APScheduler 后台调度器，每 60 秒扫描活跃职位，按 `loop_interval` 间隔自动执行招聘循环。进程持续运行直到用户中断。

---

#### `schedule list`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent schedule list [--db URL]` |
| 核心调用 | `Container.scheduler_job_repo.get_all()` |
| 输出 | Rich Table |

**表格列**：ID, Position ID, Enabled, Interval, Total Runs, Status, Next Run

---

#### `dashboard`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent dashboard [--db URL]` |
| 核心调用 | `Container.dashboard_service.get_dashboard_summary()` |
| 输出 | Rich Panel |

**面板字段**：Running Positions, Today Loops, Today Candidates, Today Emails, Today Replies, Today Errors

---

#### `graph`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent graph` |
| 核心调用 | 无（纯静态 ASCII 图） |
| 输出 | LangGraph 6 节点流程图 |

---

#### `version`

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent version` |
| 核心调用 | 无 |
| 输出 | `loop-agent-cli v0.1.0` + `Based on recruit-loop-agent core engine` |

---

## 6. 辅助函数规格

### 6.1 `_run(coro)`

```python
def _run(coro) -> Any:
    """在事件循环中运行异步协程。"""
    return asyncio.run(coro)
```

- 用途：将 `async def _do()` 协程桥接到 Typer 同步命令函数
- 约束：不能在已有事件循环中调用（CLI 场景下不会出现）

### 6.2 `_parse_json_or_file(value)`

```python
def _parse_json_or_file(value: Optional[str]) -> Optional[list]:
```

- 输入：`None` / JSON 字符串 / 文件路径 / 逗号分隔字符串
- 输出：`None` / `list[str]`
- 解析优先级：JSON 解析 → 文件读取 → 逗号分割

### 6.3 `_print_result(result)`

```python
def _print_result(result: dict) -> None:
```

- 输入：`RunnerService.run_recruiting_loop()` 返回的 dict
- 输出：Rich Panel（成功=绿色边框，失败=红色边框）
- 成功时额外打印 errors 列表（如有）

---

## 7. 异步桥接模式

所有 CLI 命令遵循统一模式：

```python
def sync_command(...):           # Typer 入口（同步）
    # 1. 同步参数校验（UUID 格式等）
    # 2. 定义异步闭包
    async def _do():
        async with Container(db_url) as c:
            # 3. 异步业务逻辑
            result = await c.xxx.yyy(...)
            # 4. 同步输出（Rich）
            console.print(...)
    # 5. 桥接到事件循环
    _run(_do())
```

**关键约束**：
- `Container` 必须在 `async with` 内使用
- Rich 输出在异步闭包内同步调用（Rich 是同步库）
- 每个命令独立创建和销毁 Container（无跨命令状态）

---

## 8. 错误处理

### 8.1 参数校验错误

| 场景 | 处理 |
|------|------|
| UUID 格式无效 | `[red]无效的 UUID: ...[/]` + `typer.Exit(1)` |
| Pipeline status 无效 | `[red]无效状态: ...[/]` + 列出合法值 + `typer.Exit(1)` |

### 8.2 数据不存在

| 场景 | 处理 |
|------|------|
| 职位不存在 | `[red]职位不存在: ...[/]` + return |
| 候选人不存在 | `[red]候选人不存在: ...[/]` + return |
| 列表为空 | `[dim]没有找到任何...[/]` + return |

### 8.3 运行时错误

| 场景 | 处理 |
|------|------|
| `run_recruiting_loop` 返回 `status=failed` | 红色 Panel 显示 error |
| `run_recruiting_loop` 返回 `status=completed` 但有 errors | 绿色 Panel + 红色 errors 列表 |
| GitHub API SSL/网络错误 | 由 SearchService 内部捕获，记入 errors 列表 |
| Scheduler Ctrl+C | 捕获 `KeyboardInterrupt`，调用 `scheduler.stop()` |

---

## 9. PyPI 包配置

### 9.1 元数据

| 字段 | 值 |
|------|-----|
| name | `loop-agent-cli` |
| version | `0.1.0` |
| license | MIT |
| requires-python | >=3.11 |
| entry point | `loop-agent = "loop_agent_cli.cli:app"` |

### 9.2 安装方式

```bash
# 开发模式
pip install -e .

# 正式发布后
pip install loop-agent-cli
```

### 9.3 前置条件

- `recruit-loop-agent` 的 `app/` 包必须在 Python 路径中（Container 通过 `sys.path` 注入项目根目录）
- `.env` 文件需存在于项目根目录（`GITHUB_TOKEN` 等）

---

## 10. 与 Web API 的关系

```
                    ┌─────────────────────┐
                    │   recruit-loop-agent │
                    │     (核心引擎)        │
                    │                     │
                    │  RunnerService      │
                    │  LangGraph 图       │
                    │  SearchService      │
                    │  ScoreService       │
                    │  PipelineService    │
                    │  EmailService       │
                    │  SchedulerService   │
                    └──────┬──────┬───────┘
                           │      │
                    ┌──────▼──┐ ┌─▼──────────┐
                    │ FastAPI  │ │ loop-agent  │
                    │ Web API  │ │ CLI (Typer) │
                    │          │ │             │
                    │ get_db() │ │ Container   │
                    └─────────┘ └────────────┘
```

- 两者共享同一个 SQLite 数据库，数据互通
- Web API 使用 `get_db()` 依赖注入，CLI 使用 `Container` 依赖注入
- 可以同时运行（CLI 不启动 HTTP 服务，不占端口）

---

## 11. 已知限制与未来扩展

### 11.1 当前限制

#### 限制 1：Container 无实例缓存

**现状**：Container 的每个 `property` 每次访问都 `return XxxRepository(self._db)` / `return XxxService(...)`，创建新实例。

**影响**：
- 单次 CLI 命令内，同一 property 被多次访问时产生冗余实例
- 例如 `c.runner` 内部依赖 `c.search_service`、`c.score_service` 等，而 `c.scheduler` 又依赖 `c.runner`，若同一命令内同时使用 `c.runner` 和 `c.scheduler`，则 `c.runner` 被创建两次
- CLI 单次执行场景下影响可忽略（毫秒级），但批量操作或交互式 REPL 场景下会累积

**根因**：`property` 无缓存机制，Python `@property` 每次调用都执行函数体

**修复方案**：

```python
# 方案 A：lazy_property 装饰器（推荐）
def _lazy_property(fn):
    attr_name = f"_cached_{fn.__name__}"
    @property
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return wrapper

@_lazy_property
def search_service(self) -> SearchService:
    return SearchService(self.candidate_service)

# 方案 B：__init__ 中预创建
def __init__(self, ...):
    self._search_service = None

@property
def search_service(self):
    if self._search_service is None:
        self._search_service = SearchService(self.candidate_service)
    return self._search_service
```

**注意事项**：缓存后 `Container` 不再是无状态的，`__aexit__` 需确保清理所有缓存实例持有的资源

---

#### 限制 2：无分页

**现状**：所有 `list` 命令调用 `repo.get_all()` 获取全量数据，然后在 Python 层截取前 N 条

```python
# 当前实现
candidates = await c.candidate_repo.get_all()  # 全量查询
candidates = candidates[:limit]                 # 内存截取
```

**影响**：
- 数据量 > 1000 条时，SQL 查询耗时增加，内存占用上升
- `--limit 20` 仍需加载全量数据到内存
- 无法实现"下一页"功能

**修复方案**：

```python
# 方案：Repository 层分页
candidates = await c.candidate_repo.get_all(skip=offset, limit=limit)

# CLI 层增加 --page 选项
@cand_app.command("list")
def candidate_list(
    limit: int = typer.Option(20, "--limit", "-n"),
    page: int = typer.Option(1, "--page", "-p"),
    db_url: Optional[str] = typer.Option(None, "--db"),
):
    offset = (page - 1) * limit
    candidates = await c.candidate_repo.get_all(skip=offset, limit=limit)
    total = await c.candidate_repo.count()
    # 显示分页信息: Page 1/5 (total: 100)
```

**依赖**：需在 Repository 层添加 `count()` 方法和 `get_all(skip, limit)` 支持

---

#### 限制 3：无配置文件

**现状**：所有配置通过两种方式传入：
1. `.env` 文件（`GITHUB_TOKEN`、`SMTP_*`、`DATABASE_URL`）
2. `--db` 命令行选项（仅覆盖数据库 URL）

**影响**：
- 无法为 CLI 设置专属默认值（如默认 `--limit`、默认 `--output` 格式）
- 多环境切换需手动修改 `.env` 或每次传 `--db`
- 无法定义命令别名或快捷方式

**修复方案**：

```toml
# ~/.loop-agent.toml
[defaults]
limit = 50
output = "rich"
db_url = "sqlite+aiosqlite:///./recruiting_agent.db"

[profiles.production]
db_url = "sqlite+aiosqlite:///./prod.db"

[aliases]
ls = "position list"
run = "run create-and-run"
```

```python
# 加载逻辑
import tomllib  # Python 3.11+

def load_config() -> dict:
    config_path = Path.home() / ".loop-agent.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    return {}

# Typer callback 中注入默认值
@app.callback()
def main(ctx: typer.Context, config: Optional[str] = typer.Option(None, "--config", "-C")):
    ctx.ensure_object(dict)
    if config:
        ctx.obj.update(load_config(config))
```

**新增依赖**：无（`tomllib` 为 Python 3.11+ 标准库）

---

#### 限制 4：schedule start 阻塞

**现状**：`schedule start` 在前台运行 `while True: await asyncio.sleep(1)`，占用终端

**影响**：
- 无法在同一个终端执行其他 CLI 命令
- 关闭终端则调度器停止
- 无法开机自启

**修复方案**：

```python
# 方案 A：--daemon 模式（使用 python-daemon 或 systemd）
@sched_app.command("start")
def schedule_start(
    daemon: bool = typer.Option(False, "--daemon", "-d", help="后台守护进程模式"),
    pid_file: str = typer.Option("/tmp/loop-agent.pid", "--pid-file"),
    log_file: str = typer.Option("/tmp/loop-agent.log", "--log-file"),
):
    if daemon:
        # fork 后台进程，写入 PID 文件
        import daemon as python_daemon
        with python_daemon.DaemonContext(
            pidfile=pid_file,
            stdout=open(log_file, "a"),
            stderr=open(log_file, "a"),
        ):
            _run(_scheduler_loop(db_url))
    else:
        # 前台模式（当前行为）
        _run(_scheduler_loop(db_url))

# 方案 B：systemd service 文件
# /etc/systemd/system/loop-agent.service
# [Unit]
# Description=Recruiting Loop Agent Scheduler
# [Service]
# ExecStart=/usr/bin/loop-agent schedule start
# Restart=always
# [Install]
# WantedBy=multi-user.target

# 方案 C：schedule stop / schedule status 命令
@sched_app.command("stop")
def schedule_stop(pid_file: str = typer.Option("/tmp/loop-agent.pid", "--pid-file")):
    """停止后台调度器"""
    pid = int(Path(pid_file).read_text())
    os.kill(pid, signal.SIGTERM)

@sched_app.command("status")
def schedule_status(pid_file: str = typer.Option("/tmp/loop-agent.pid", "--pid-file")):
    """查看调度器运行状态"""
    pid_path = Path(pid_file)
    if pid_path.exists():
        pid = int(pid_path.read_text())
        try:
            os.kill(pid, 0)  # 检查进程是否存活
            console.print(f"[green]Scheduler running (PID: {pid})[/]")
        except ProcessLookupError:
            console.print("[red]Scheduler not running (stale PID file)[/]")
    else:
        console.print("[dim]Scheduler not running[/]")
```

**新增依赖**：`python-daemon`（方案 A），或无（方案 B/C）

---

#### 限制 5：无输出格式选项

**现状**：所有输出通过 Rich 格式化（Table/Panel），仅适合终端阅读

**影响**：
- 无法将结果管道到其他命令（`loop-agent candidate list | jq .`）
- 无法导入到电子表格或数据库
- 脚本集成需解析 Rich ANSI 转义序列

**修复方案**：

```python
# 全局 --output 选项
from enum import Enum

class OutputFormat(str, Enum):
    rich = "rich"      # 默认，Rich 格式化
    json = "json"      # JSON 数组
    csv = "csv"        # CSV 表格
    tsv = "tsv"        # TSV（适合粘贴到 Excel）

@app.callback()
def main(
    ctx: typer.Context,
    output: OutputFormat = typer.Option(OutputFormat.rich, "--output", "-o"),
):
    ctx.ensure_object(dict)
    ctx.obj["output"] = output

# 输出适配器
class OutputAdapter:
    def __init__(self, fmt: OutputFormat):
        self.fmt = fmt

    def table(self, title: str, columns: list[str], rows: list[list]):
        if self.fmt == OutputFormat.rich:
            # 当前 Rich 逻辑
            ...
        elif self.fmt == OutputFormat.json:
            data = [dict(zip(columns, row)) for row in rows]
            print(json.dumps(data, ensure_ascii=False, indent=2))
        elif self.fmt == OutputFormat.csv:
            import csv, sys
            writer = csv.writer(sys.stdout)
            writer.writerow(columns)
            writer.writerows(rows)
        elif self.fmt == OutputFormat.tsv:
            import csv, sys
            writer = csv.writer(sys.stdout, delimiter="\t")
            writer.writerow(columns)
            writer.writerows(rows)

    def panel(self, title: str, content: str):
        if self.fmt == OutputFormat.rich:
            console.print(Panel(content, title=title))
        else:
            # JSON/CSV 模式下，panel 退化为 key-value 输出
            print(f"# {title}")
            print(content)
```

**使用示例**：

```bash
# JSON 输出，管道到 jq
loop-agent -o json candidate list | jq '.[0].name'

# CSV 输出，导入 Excel
loop-agent -o csv pipeline list > pipelines.csv

# TSV 输出，粘贴到剪贴板
loop-agent -o tsv position list | clip
```

---

### 11.2 未来扩展方向

#### 扩展 1：`--output json/csv` — 结构化输出

**优先级**：高

**目标**：所有 `list` 和 `show` 命令支持 `--output json|csv|tsv|rich`，默认 `rich`

**实现要点**：
- 在 Typer `callback` 中注册全局 `--output` 选项，存入 `ctx.obj`
- 创建 `OutputAdapter` 类，统一处理 Table/Panel 两种输出模式
- `rich` 模式保持当前行为；`json`/`csv`/`tsv` 模式输出纯文本，无 ANSI 转义
- `run position` 和 `run create-and-run` 的结果 Panel 在非 rich 模式下输出 JSON

**影响范围**：`cli.py` 全部命令的输出逻辑

**详细规格**：

| 命令 | JSON 输出格式 |
|------|-------------|
| `position list` | `[{"id": "...", "title": "...", ...}, ...]` |
| `position show` | `{"id": "...", "title": "...", ...}` |
| `candidate list` | `[{"id": "...", "name": "...", ...}, ...]` |
| `candidate show` | `{"id": "...", "name": "...", ...}` |
| `pipeline list` | `[{"id": "...", "status": "...", ...}, ...]` |
| `dashboard` | `{"running_positions": 3, "today_loops": 0, ...}` |
| `run position` | `{"status": "completed", "results": {...}, "duration_ms": 1234}` |

---

#### 扩展 2：`position update` — 修改已有职位

**优先级**：高

**目标**：支持修改职位的技能、关键词、间隔等字段，无需删除重建

**命令规格**：

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent position update <position_id> [OPTIONS]` |
| 参数 | `position_id: str` (必填，UUID) |
| 可选选项 | `--title/-t`, `--company/-c`, `--desc/-d`, `--location/-l`, `--skills/-s`, `--keywords/-k`, `--interval/-i`, `--status` (active/paused/closed), `--loop-enabled/--no-loop-enabled`, `--db` |
| 核心调用 | `Container.position_repo.update(pid, PositionUpdate(...))` |
| 输出 | 更新确认 + 变更字段列表 |

**实现要点**：
- 使用 `PositionUpdate` schema（所有字段 `Optional`，仅更新传入的字段）
- `--skills` 和 `--keywords` 使用 `_parse_json_or_file` 解析
- `--loop-enabled/--no-loop-enabled` 使用 Typer 布尔选项语法
- 输出变更前后的 diff

```bash
# 修改技能和间隔
loop-agent position update 42e1d822 -s "Python,Go,Rust" -i 30

# 暂停职位循环
loop-agent position update 42e1d822 --no-loop-enabled

# 恢复并修改关键词
loop-agent position update 42e1d822 --loop-enabled -k "golang,backend"
```

---

#### 扩展 3：`candidate search` — 手动触发搜索

**优先级**：中

**目标**：单独执行搜索节点，不经过完整循环，用于快速探索候选人池

**命令规格**：

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent candidate search <position_id> [OPTIONS]` |
| 参数 | `position_id: str` (必填，UUID) |
| 可选选项 | `--keywords/-k` (覆盖职位关键词), `--max-results/-m` (默认 30), `--db` |
| 核心调用 | `Container.search_service.generate_search_keywords()` + `Container.search_service.search_candidates()` |
| 输出 | 搜索结果列表（Rich Table 或 JSON） |

**与 `run position` 的区别**：

| 对比项 | `run position` | `candidate search` |
|--------|---------------|-------------------|
| 执行范围 | 完整 6 节点循环 | 仅 search 节点 |
| 是否评分 | 是 | 否 |
| 是否创建管道 | 是 | 否 |
| 是否发送邮件 | 是 | 否 |
| 用途 | 生产执行 | 探索/调试 |

---

#### 扩展 4：`run status <run_id>` — 查看运行详情

**优先级**：中

**目标**：查看某次 AgentRun 的详细结果，包括各节点的执行日志

**命令规格**：

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent run status <run_id> [--db URL]` |
| 参数 | `run_id: str` (必填，UUID) |
| 核心调用 | `Container.agent_run_repo.get_by_id(run_id)` + `Container.node_log_repo.get_by_run(run_id)` |
| 输出 | AgentRun 摘要 Panel + NodeLog 列表 Table |

**输出示例**：

```
┌─────────────── AgentRun Detail ───────────────┐
│  ID:              abc-123                      │
│  Position:        Backend Engineer @ TestCo    │
│  Status:          completed                    │
│  Duration:        5230 ms                      │
│  Candidates:      found=47, added=12           │
│  Emails:          8                            │
│  Started:         2026-07-01 10:00:00          │
│  Finished:        2026-07-01 10:00:05          │
└───────────────────────────────────────────────┘

Node Logs:
┌──────┬─────────┬──────────┬─────────┐
│ Node │ Status  │ Duration │ Detail  │
├──────┼─────────┼──────────┼─────────┤
│ search   │ success │ 3200 ms  │ 47 found  │
│ dedup    │ success │ 5 ms     │ 3 removed │
│ score    │ success │ 1800 ms  │ 12 passed │
│ pipeline │ success │ 120 ms   │ 12 created│
│ outreach │ success │ 95 ms    │ 8 sent    │
│ evaluate │ success │ 10 ms    │ loop=false│
└──────┴─────────┴──────────┴─────────┘
```

**依赖**：需在 `NodeLogRepository` 中添加 `get_by_run(run_id)` 方法

---

#### 扩展 5：`schedule start --daemon` — 后台守护进程

**优先级**：中

**目标**：调度器以后台守护进程运行，不占用终端

**命令规格**：

| 项 | 值 |
|----|-----|
| 用法 | `loop-agent schedule start [--daemon] [--pid-file PATH] [--log-file PATH]` |
| 新增选项 | `--daemon/-d` (后台模式), `--pid-file` (默认 `/tmp/loop-agent.pid`), `--log-file` (默认 `/tmp/loop-agent.log`) |
| 配套命令 | `schedule stop` (停止守护进程), `schedule status` (查看运行状态) |

**实现要点**：
- `--daemon` 模式使用 `python-daemon` 或 `os.fork()` 创建后台进程
- PID 文件用于 `stop` 和 `status` 命令
- 日志输出到文件而非终端
- 提供 systemd service 文件模板

**新增依赖**：`python-daemon`（可选）

---

#### 扩展 6：Container 实例缓存

**优先级**：低（当前 CLI 场景下影响可忽略）

**目标**：避免同一 Container 内重复创建 Service/Repository 实例

**实现方案**：

```python
class Container:
    def __init__(self, db_url=None):
        self._db_url = db_url
        self._db = None
        self._cache: dict[str, Any] = {}

    def _cached(self, key: str, factory: Callable) -> Any:
        if key not in self._cache:
            self._cache[key] = factory()
        return self._cache[key]

    @property
    def search_service(self) -> SearchService:
        return self._cached("search_service", lambda: SearchService(self.candidate_service))

    @property
    def runner(self) -> RunnerService:
        return self._cached("runner", lambda: RunnerService(
            search_service=self.search_service,  # 复用缓存实例
            ...
        ))
```

**注意事项**：
- 缓存后 `runner` 和 `scheduler` 共享同一个 `search_service` 实例
- `__aexit__` 需清理缓存中持有 DB 会话的实例
- 对 CLI 单次执行场景性能提升有限，主要收益在交互式 REPL 场景

---

#### 扩展 7：`--config` 选项 — 配置文件支持

**优先级**：低

**目标**：支持 YAML/TOML 配置文件，定义 CLI 默认值和环境 profile

**配置文件格式**（TOML，Python 3.11+ 标准库原生支持）：

```toml
# ~/.loop-agent.toml

[defaults]
limit = 50
output = "rich"
db_url = "sqlite+aiosqlite:///./recruiting_agent.db"

[profiles.staging]
db_url = "sqlite+aiosqlite:///./staging.db"

[profiles.production]
db_url = "sqlite+aiosqlite:///./prod.db"
github_token = "ghp_..."   # 覆盖 .env 中的值

[aliases]
ls = "position list"
ps = "pipeline list --status discovered"
```

**命令规格**：

| 项 | 值 |
|----|-----|
| 全局选项 | `--config/-C <path>` (指定配置文件路径) |
| 环境选项 | `--profile/-P <name>` (选择配置 profile) |
| 查找顺序 | `--config` 指定 → `./.loop-agent.toml` → `~/.loop-agent.toml` → 内置默认值 |
| 优先级 | 命令行参数 > 配置文件 > `.env` > 内置默认值 |

**实现要点**：
- 在 Typer `callback` 中加载配置，注入 `ctx.obj`
- 各命令从 `ctx.obj` 读取默认值
- `aliases` 需自定义 Typer 命令解析逻辑

---

### 11.3 扩展优先级矩阵

| 扩展 | 优先级 | 复杂度 | 影响范围 | 新增依赖 |
|------|--------|--------|---------|---------|
| `--output json/csv` | 高 | 中 | cli.py 全部输出 | 无 |
| `position update` | 高 | 低 | cli.py 新增命令 | 无 |
| `candidate search` | 中 | 低 | cli.py 新增命令 | 无 |
| `run status` | 中 | 低 | cli.py + repo 层 | 无 |
| `schedule --daemon` | 中 | 中 | cli.py + 新进程管理 | python-daemon (可选) |
| Container 缓存 | 低 | 低 | container.py | 无 |
| `--config` 选项 | 低 | 中 | cli.py callback + 新模块 | 无 (tomllib 标准库) |

### 11.4 扩展后的完整命令树

```
loop-agent
├── run                              [命令组] 执行招聘循环
│   ├── position <position_id>       对已有职位执行一次循环
│   ├── create-and-run               创建职位并立即执行循环
│   └── status <run_id>     [新增]   查看某次运行详情与 NodeLog
├── position                         [命令组] 职位管理
│   ├── list                         列出所有职位
│   ├── create                       创建新职位
│   ├── show <position_id>           查看职位详情
│   ├── update <position_id> [新增]  修改职位字段
│   └── close <position_id>          关闭职位
├── candidate                        [命令组] 候选人管理
│   ├── list                         列出候选人
│   ├── show <candidate_id>          查看候选人详情
│   └── search <position_id> [新增]  手动触发搜索
├── pipeline                         [命令组] 招聘管道管理
│   ├── list                         列出管道
│   └── update-status <id> <status>  更新管道状态
├── schedule                         [命令组] 调度管理
│   ├── start [--daemon]    [增强]   启动调度器（支持后台模式）
│   ├── stop                [新增]   停止后台调度器
│   ├── status              [新增]   查看调度器运行状态
│   └── list                         列出调度任务
├── dashboard                        查看仪表盘摘要
├── graph                            显示 LangGraph 图结构
└── version                          显示版本信息

全局选项:
  --db URL          数据库 URL
  --output FORMAT   [新增] 输出格式 (rich|json|csv|tsv)
  --config PATH     [新增] 配置文件路径
  --profile NAME    [新增] 配置 profile
```