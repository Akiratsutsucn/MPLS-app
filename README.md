# 等级保护项目管理系统 (MLPS-PM)

等保项目全生命周期管理工具，覆盖定级、备案、建设整改、等级测评、监督检查五个阶段。

## 功能

- 看板视图：拖拽切换项目阶段
- 列表视图：筛选、排序、搜索
- 检查清单：每阶段预置检查项 + 自定义项
- 文档管理：按阶段上传/下载文件
- 操作日志：系统自动记录 + 手动备忘
- 提醒管理：设置到期提醒
- Word 导出：一键生成项目报告
- JWT 认证

## 技术栈

- 后端：FastAPI + SQLAlchemy (async) + MySQL
- 前端：Vue 3 + Element Plus + Pinia + Vue Router

## 快速开始

### Docker Compose

```bash
docker compose up -d
```

访问 http://localhost

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
cp ../.env.example .env  # 修改数据库配置
uvicorn app.main:app --port 9001 --reload

# 前端
cd frontend
npm install
npm run dev
```

API 文档：http://localhost:9001/docs
