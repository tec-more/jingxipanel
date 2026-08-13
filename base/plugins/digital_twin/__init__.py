"""
数字孪生插件
提供孪生实体建模、实时数据同步、仿真预测和可视化能力
"""
from base.common.log import log


async def on_enable(app) -> bool:
    """插件启用时调用"""
    log.info("数字孪生插件已启用")
    return True


async def on_disable() -> bool:
    """插件禁用时调用"""
    log.info("数字孪生插件已禁用")
    return True


async def on_startup() -> None:
    """应用启动时调用"""
    log.info("数字孪生插件启动完成")


async def on_shutdown() -> None:
    """应用关闭时调用"""
    log.info("数字孪生插件已关闭")
