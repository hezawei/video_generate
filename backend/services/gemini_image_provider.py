"""
Gemini 图片生成服务（通过 OpenRouter）
支持文生图和图生图
"""
import os
import base64
import httpx
from typing import Optional
from openai import OpenAI

from config import GEMINI_IMAGE_CONFIG


class GeminiImageProvider:
    """Gemini 图片生成服务"""

    def __init__(self):
        self.api_key = GEMINI_IMAGE_CONFIG["api_key"]
        self.base_url = GEMINI_IMAGE_CONFIG["base_url"]
        self.model = GEMINI_IMAGE_CONFIG["model"]
        self.proxy = GEMINI_IMAGE_CONFIG.get("proxy")
        self.timeout = GEMINI_IMAGE_CONFIG.get("timeout", 120)
        
        # 配置代理
        if self.proxy:
            os.environ['http_proxy'] = self.proxy
            os.environ['https_proxy'] = self.proxy
            os.environ['HTTP_PROXY'] = self.proxy
            os.environ['HTTPS_PROXY'] = self.proxy
            
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                http_client=httpx.Client(
                    proxy=self.proxy,
                    timeout=httpx.Timeout(self.timeout, connect=10.0),
                ),
            )
        else:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=self.timeout,
            )

    def generate_image(
        self,
        prompt: str,
        reference_image_base64: Optional[str] = None,
    ) -> dict:
        """
        生成图片
        
        Args:
            prompt: 生成提示词
            reference_image_base64: 参考图片的 base64 编码（图生图时使用）
            
        Returns:
            {"image_base64": "...", "content": "..."}
        """
        print(f"[Gemini图片] 开始生成，提示词: {prompt[:50]}...")
        
        # 构建消息
        if reference_image_base64:
            # 图生图：发送图片和提示词
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{reference_image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        else:
            # 文生图：只发送提示词
            messages = [{"role": "user", "content": prompt}]
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                extra_headers={
                    "HTTP-Referer": "http://115.120.15.8:8002",
                    "X-Title": "AI Video Generator",
                },
                messages=messages,
                stream=False,
            )
        except Exception as e:
            print(f"[Gemini图片] 请求失败: {e}")
            raise Exception(f"图片生成请求失败: {e}")
        
        # 解析响应
        msg_dict = completion.choices[0].message.model_dump()
        images = msg_dict.get("images", [])
        content = msg_dict.get("content", "")
        
        if not images:
            print(f"[Gemini图片] 响应中没有图片，内容: {content[:100]}")
            raise Exception("生成失败：响应中没有图片")
        
        # 提取图片数据
        image_data = images[0].get("image_url", {}).get("url", "")
        if not image_data:
            raise Exception("生成失败：图片数据为空")
        
        # 分离 base64 数据
        if "," in image_data:
            _, b64_data = image_data.split(",", 1)
        else:
            b64_data = image_data
        
        print(f"[Gemini图片] 生成成功，数据大小: {len(b64_data) / 1024:.1f} KB")
        
        return {
            "image_base64": b64_data,
            "content": content,
        }


# 单例
_provider = None

def get_image_provider() -> GeminiImageProvider:
    global _provider
    if _provider is None:
        _provider = GeminiImageProvider()
    return _provider
