# Recruiting Loop Agent Frontend

这是一个为Recruiting Loop Agent v3.0 MVP项目构建的现代化前端应用，使用React和Ant Design技术栈。

## 功能特性

- **Dashboard**：实时监控招聘代理系统的运行状态
- **Position管理**：创建、编辑、暂停/恢复招聘职位
- **Candidate管理**：查看和管理候选人信息
- **Pipeline管理**：可视化招聘管道（discovered → contacted → replied → interview → offer → rejected）
- **Scheduler监控**：监控和控制系统调度任务
- **日志查看**：查看系统运行日志
- **系统设置**：配置GitHub API、SMTP等系统参数

## 技术栈

- React 18
- Ant Design 5.x
- React Router v6
- Axios
- @ant-design/plots (用于数据可视化)

## 项目结构

```
src/
├── components/           # 可复用UI组件
├── pages/               # 页面组件
│   ├── Dashboard/       # Dashboard页面
│   ├── Positions/       # 职位管理页面
│   ├── Candidates/      # 候选人管理页面
│   ├── Scheduler/       # 调度监控页面
│   ├── Logs/            # 日志查看页面
│   └── Settings/        # 系统设置页面
├── services/            # API服务
├── hooks/               # 自定义hooks
├── App.js               # 主应用组件
└── index.js             # 应用入口
```

## 安装和运行

1. 安装依赖：
```bash
npm install
```

2. 启动开发服务器：
```bash
npm start
```

3. 在浏览器中访问 `http://localhost:3000`

## 环境变量

如果需要自定义API端点，请创建 `.env` 文件并添加以下内容：

```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## 构建生产版本

```bash
npm run build
```

## API集成

前端与后端API通过 `src/services/api.js` 进行通信，支持以下功能：

- 位置管理（CRUD操作）
- 候选人管理
- 招聘管道管理
- 调度控制
- 日志查询
- 系统配置

## 设计理念

- **监控优先**：强调实时监控和状态跟踪
- **响应式设计**：适配各种屏幕尺寸
- **用户体验**：简洁直观的界面设计
- **性能优化**：高效的组件渲染和数据加载