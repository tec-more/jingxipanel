from fastapi import APIRouter
from pydantic import BaseModel
from base.common.setting import settings

router = APIRouter(prefix="/v1/common", tags=["公共配置"])


class SystemConfigResponse(BaseModel):
    """系统配置响应"""
    app_name: str
    app_version: str
    app_description: str
    frontend_name: str
    backend_name: str
    debug: bool


@router.get("/system-config", summary="获取系统公共配置", response_model=SystemConfigResponse)
async def get_system_config():
    """获取前端可公开的系统配置（无需登录）"""
    return SystemConfigResponse(
        app_name=settings.app_name,
        app_version=settings.app_version,
        app_description=settings.app_description,
        frontend_name=settings.frontend_name,
        backend_name=settings.backend_name,
        debug=settings.debug,
    )
