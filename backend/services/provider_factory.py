"""
Provider工厂
根据配置返回对应的视频生成服务
"""
from config import CURRENT_PROVIDER
from services.base_provider import BaseVideoProvider
from services.wuyin_provider import WuyinProvider


def get_provider() -> BaseVideoProvider:
    """
    获取当前配置的视频生成服务
    
    更换中转商时，只需在此添加新的Provider映射
    """
    providers = {
        "wuyin": WuyinProvider,
        # 未来添加其他中转商:
        # "other_provider": OtherProvider,
    }
    
    provider_class = providers.get(CURRENT_PROVIDER)
    if not provider_class:
        raise ValueError(f"未知的Provider: {CURRENT_PROVIDER}")
    
    return provider_class()
