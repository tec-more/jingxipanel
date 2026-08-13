"""孪生集成路由 - 与其他模块的数据同步"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

try:
    from base.plugins.digital_twin.services.integration_service import TwinIntegrationService
    from base.common.response import success_response
except ImportError:
    class APIRouter:
        def __init__(self, prefix="", tags=None): pass
        def get(self, p, **kw):
            def d(f): return f
            return d
        def post(self, p, **kw):
            def d(f): return f
            return d
    class HTTPException(Exception):
        def __init__(self, status_code, detail): pass
    class TwinIntegrationService: pass
    class BaseModel:
        pass
    def success_response(**kw): return {}

twin_integration_router = APIRouter(prefix="/integration", tags=["孪生集成"])


class EquipmentSyncRequest(BaseModel):
    equipment_codes: Optional[List[str]] = Field(None, description="指定设备编码列表，留空则同步全部")


@twin_integration_router.post("/sync/equipment", summary="从设备模块同步到孪生实体")
async def sync_equipment(data: EquipmentSyncRequest = EquipmentSyncRequest()):
    result = await TwinIntegrationService.sync_from_equipment(data.equipment_codes)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "同步失败"))
    return success_response(data=result, msg=f"同步完成：新增 {result['created']}，更新 {result['updated']}")


@twin_integration_router.post("/sync/mes-workcenter", summary="从 MES 工作中心同步到孪生实体")
async def sync_mes_workcenter():
    result = await TwinIntegrationService.sync_from_mes_workcenter()
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "同步失败"))
    return success_response(data=result, msg=f"同步完成：新增 {result['created']}，更新 {result['updated']}")


@twin_integration_router.get("/status-mapping", summary="获取设备状态映射关系")
async def get_status_mapping():
    """返回 equipment 状态 → 孪生实体状态的映射表，供前端展示"""
    from base.plugins.digital_twin.services.integration_service import EQUIPMENT_STATUS_MAP
    return success_response(data={"equipment_to_twin": EQUIPMENT_STATUS_MAP})
