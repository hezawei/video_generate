# AI视频生成

## 本地开发

```bash
# 后端
cd backend && pip install -r requirements.txt && python main.py

# 前端
cd frontend && npm install && npm run dev
```

本地访问: http://localhost:3000

## 服务器部署

服务器: root@115.120.15.8
访问地址: http://115.120.15.8:8002

```bash
cd scripts
python deploy_first.py   # 首次部署
python update_all.py      # 完整更新
python update_backend.py  # 仅更新后端（最快）
python restart.py         # 重启服务
python logs.py            # 查看日志
python ssh.py             # SSH连接
```

## API配置

`backend/config.py` - 悟隐科技Sora2
- API Key: Kp2Awh23NjJeIrLTkZANHhFDWw
- 更换中转商: 继承`BaseVideoProvider`，改`CURRENT_PROVIDER`
