# AI视频生成

个人用AI视频生成服务（文生视频、图生视频）

## 本地开发

### 启动后端
```bash
cd backend
python dev.py
```
> 自动清理旧进程，启动在 http://127.0.0.1:8002

### 启动前端（另开终端）
```bash
cd frontend
pnpm dev
```
> 启动在 http://localhost:3000

### 图生视频配置
需要配置 GitHub 图床：
1. 创建 GitHub 仓库 `image-bed`
2. 生成 Token: https://github.com/settings/tokens (勾选 repo)
3. 编辑 `backend/routes/generate.py` 填入 GITHUB_TOKEN

---

## 服务器部署

### 首次部署
```bash
cd scripts
python deploy_first.py
```

### 更新代码
```bash
cd scripts
python update_all.py
```
> 自动: 本地 commit/push → 服务器 pull → 重启

### 服务器访问
http://115.120.15.8:8002

### 手动操作
```bash
ssh root@115.120.15.8
tail -f /root/video-gen/server.log          # 查看日志
cd /root/video-gen && ./scripts/server/restart.sh  # 重启
```
