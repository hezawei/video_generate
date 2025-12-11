"""
悟隐科技 Sora2 视频生成服务实现
"""
import requests
from typing import Optional

from config import WUYIN_CONFIG
from services.base_provider import BaseVideoProvider, TaskResult, TaskState


class WuyinProvider(BaseVideoProvider):
    """悟隐科技Sora2接口实现"""

    def __init__(self):
        self.api_key = WUYIN_CONFIG["api_key"]
        self.submit_url = WUYIN_CONFIG["submit_url"]
        self.detail_url = WUYIN_CONFIG["detail_url"]
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }

    def submit_task(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        aspect_ratio: str = "9:16",
        duration: str = "10",
        **kwargs
    ) -> str:
        """提交视频生成任务到悟隐科技"""
        params = {"key": self.api_key}
        
        data = {
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
            "duration": duration,
            "size": WUYIN_CONFIG.get("default_size", "small"),
        }
        
        # 图生视频：添加参考图片
        if image_url:
            data["url"] = image_url

        response = requests.post(
            self.submit_url,
            headers=self.headers,
            params=params,
            data=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") != 200:
            raise Exception(f"提交失败: {result.get('msg', '未知错误')}")
        
        task_id = result.get("data", {}).get("id")
        if not task_id:
            raise Exception("未获取到任务ID")
        
        return task_id

    def query_task(self, task_id: str) -> TaskResult:
        """查询悟隐科技任务状态"""
        params = {
            "key": self.api_key,
            "id": task_id,
        }

        response = requests.get(
            self.detail_url,
            headers=self.headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") != 200:
            return TaskResult(
                state=TaskState.FAILED,
                error_message=f"查询失败: {result.get('msg', '未知错误')}"
            )

        data = result.get("data", {})
        status = data.get("status")
        
        # 状态映射: 0=排队中, 1=成功, 2=失败, 3=生成中
        state_map = {
            0: TaskState.QUEUED,
            1: TaskState.SUCCESS,
            2: TaskState.FAILED,
            3: TaskState.PROCESSING,
        }
        
        state = state_map.get(status, TaskState.QUEUED)
        
        return TaskResult(
            state=state,
            video_url=data.get("remote_url") if state == TaskState.SUCCESS else None,
            error_message=data.get("fail_reason") if state == TaskState.FAILED else None,
        )
