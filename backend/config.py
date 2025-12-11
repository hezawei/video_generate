"""
AI生成服务配置文件
便于更换中转商，只需修改此文件或添加新的Provider配置
"""
import os

# 当前使用的视频生成服务商
CURRENT_PROVIDER = "wuyin"

# 悟隐科技配置（视频生成）
WUYIN_CONFIG = {
    "api_key": "Kp2Awh23NjJeIrLTkZANHhFDWw",
    "submit_url": "https://api.wuyinkeji.com/api/sora2/submit",
    "detail_url": "https://api.wuyinkeji.com/api/sora2/detail",
    "default_aspect_ratio": "1:1",
    "default_duration": "10",
    "default_size": "small",
}

# Gemini 图片生成配置（通过 OpenRouter）
GEMINI_IMAGE_CONFIG = {
    "api_key": "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",
    "base_url": "https://openrouter.ai/api/v1",
    "model": "google/gemini-2.5-flash-image",
    "proxy": "http://127.0.0.1:7890",  # 本地代理，服务器设为 None
    "timeout": 120,
}

# 轮询配置
POLL_CONFIG = {
    "max_attempts": 120,  # 最大轮询次数
    "interval_seconds": 5,  # 轮询间隔（秒）
}

# 服务器配置
SERVER_CONFIG = {
    "host": "0.0.0.0",  # 生产环境绑定所有IP
    "port": 8002,
    "uploads_dir": os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"),
    "downloads_dir": os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads"),
}

# 数据库配置
DATABASE_CONFIG = {
    "url": "sqlite:///./video_gen.db",
}
