#!/usr/bin/env python3
"""
OpenRouter Nano-Banana 图片生成测试
用法: python test_gemini_image.py
"""

import os
import time
import base64
import httpx
from pathlib import Path
from openai import OpenAI

# ================= 配置 =================
PROXY_URL = "http://127.0.0.1:7890"
API_KEY = "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"
MODEL_NAME = "google/gemini-2.5-flash-image"
OUTPUT_DIR = Path(__file__).parent / "output"
# ========================================

# 设置代理环境变量
os.environ['http_proxy'] = PROXY_URL
os.environ['https_proxy'] = PROXY_URL
os.environ['HTTP_PROXY'] = PROXY_URL
os.environ['HTTPS_PROXY'] = PROXY_URL

# 全局客户端（复用连接池，走代理）
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    http_client=httpx.Client(
        proxy=PROXY_URL,
        timeout=httpx.Timeout(120.0, connect=10.0),
    ),
)


def generate_image(prompt: str) -> str:
    print(f"🚀 正在请求生成图片...")
    print(f"📝 提示词: {prompt}")
    
    start = time.time()
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            extra_headers={
                "HTTP-Referer": "http://115.120.15.8:8000",
                "X-Title": "Rebirth Game",
            },
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return ""
    
    total_time = time.time() - start
    msg_dict = completion.choices[0].message.model_dump()
    images = msg_dict.get("images", [])
    
    if not images:
        print("⚠️ 响应中没有图片")
        print(f"📨 返回内容: {msg_dict.get('content', '(空)')[:200]}")
        return ""
        
    image_data = images[0].get("image_url", {}).get("url", "")
    
    header, b64_data = image_data.split(",", 1)
    img_bytes = base64.b64decode(b64_data)
    data_size_mb = len(b64_data) / 1024 / 1024
    
    print(f"⏱️  总耗时: {total_time:.2f}秒")
    print(f"📦 数据量: {data_size_mb:.2f} MB | 图片: {len(img_bytes)/1024:.0f} KB")
    print(f"🚀 传输速度: {data_size_mb / total_time * 8:.2f} Mbps (含生成时间)")

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / "openrouter_image.png"
    output_path.write_bytes(img_bytes)
    
    print(f"✅ 已保存: {output_path}")
    return str(output_path)
    

if __name__ == "__main__":
    print("=" * 50)
    print("🎨 OpenRouter Nano-Banana 图片生成测试")
    print("=" * 50)
    print(f"模型: {MODEL_NAME}")
    print(f"代理: {PROXY_URL}")
    print(f"Key: {API_KEY[:15]}...{API_KEY[-4:]}")
    print()
    
    try:
        # 明确要求生成图片
        result = generate_image("生成一个项羽的角色形象，羽扇纶巾，身穿旗袍，五官像王力宏，正脸")
        if result:
            print("\n🎉 测试成功！")
        else:
            print("\n❌ 未生成图片")
    except Exception as e:
        print(f"\n❌ 出错了: {e}")
