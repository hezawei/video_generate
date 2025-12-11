"""
视频生成服务抽象基类
不同的中转商只需继承此类并实现具体方法
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TaskState(Enum):
    """任务状态枚举"""
    QUEUED = 0      # 排队中
    SUCCESS = 1     # 成功
    FAILED = 2      # 失败
    PROCESSING = 3  # 生成中


@dataclass
class TaskResult:
    """任务查询结果"""
    state: TaskState
    video_url: Optional[str] = None
    error_message: Optional[str] = None


class BaseVideoProvider(ABC):
    """
    视频生成服务抽象基类
    
    更换中转商时，只需：
    1. 创建新的Provider类继承此基类
    2. 实现submit_task和query_task方法
    3. 在config.py中添加配置
    4. 在get_provider()中注册
    """

    @abstractmethod
    def submit_task(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        aspect_ratio: str = "9:16",
        duration: str = "10",
        **kwargs
    ) -> str:
        """
        提交视频生成任务
        
        Args:
            prompt: 生成提示词
            image_url: 参考图片URL（图生视频时使用）
            aspect_ratio: 视频比例，如 "9:16" 或 "16:9"
            duration: 视频时长，如 "10" 或 "15"
            
        Returns:
            任务ID
            
        Raises:
            Exception: 提交失败时抛出异常
        """
        pass

    @abstractmethod
    def query_task(self, task_id: str) -> TaskResult:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            TaskResult对象，包含状态和结果
        """
        pass
