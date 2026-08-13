"""孪生实体路由"""
from typing import Optional
from fastapi import APIRouter, HTTPException

try:
    from base.plugins.digital_twin.services.digital_twin_service import TwinEntityService
    from base.plugins.digital_twin.schemas.digital_twin_schema import (
        TwinEntityCreate, TwinEntityUpdate, EntityStatusUpdate, EntityPropertiesUpdate,
    )
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
        def put(self, p, **kw):
            def d(f): return f
            return d
        def delete(self, p, **kw):
            def d(f): return f
            return d
    class HTTPException(Exception):
        def __init__(self, status_code, detail): pass
    class TwinEntityService:
        pass
    class TwinEntityCreate: pass
    class TwinEntityUpdate: pass
    class EntityStatusUpdate: pass
    class EntityPropertiesUpdate: pass
    def success_response(**kw): return {}

twin_entity_router = APIRouter(prefix="/entity", tags=["孪生实体"])


@twin_entity_router.get("/", summary="获取孪生实体列表")
async def list_entities(
    page: int = 1,
    page_size: int = 10,
    entity_code: Optional[str] = None,
    entity_name: Optional[str] = None,
    entity_type: Optional[str] = None,
    current_status: Optional[str] = None,
    parent_code: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    items, total = await TwinEntityService.get_list(
        page=page, page_size=page_size,
        entity_code=entity_code, entity_name=entity_name,
        entity_type=entity_type, current_status=current_status,
        parent_code=parent_code, is_active=is_active,
    )
    data = [await i.to_dict() for i in items]
    return success_response(data={"items": data, "total": total, "page": page, "page_size": page_size})


@twin_entity_router.get("/{entity_id}", summary="获取孪生实体详情")
async def get_entity(entity_id: int):
    entity = await TwinEntityService.get_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="孪生实体不存在")
    return success_response(data=await entity.to_dict())


@twin_entity_router.post("/", summary="创建孪生实体")
async def create_entity(data: TwinEntityCreate):
    try:
        entity = await TwinEntityService.create_entity(data)
        return success_response(data=await entity.to_dict(), msg="创建成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@twin_entity_router.put("/{entity_id}", summary="更新孪生实体")
async def update_entity(entity_id: int, data: TwinEntityUpdate):
    entity = await TwinEntityService.update_entity(entity_id, data)
    if not entity:
        raise HTTPException(status_code=404, detail="孪生实体不存在")
    return success_response(data=await entity.to_dict(), msg="更新成功")


@twin_entity_router.delete("/{entity_id}", summary="删除孪生实体")
async def delete_entity(entity_id: int):
    ok = await TwinEntityService.delete_entity(entity_id)
    if not ok:
        raise HTTPException(status_code=404, detail="孪生实体不存在")
    return success_response(msg="删除成功")


@twin_entity_router.post("/{entity_id}/status", summary="更新孪生实体状态")
async def update_entity_status(entity_id: int, data: EntityStatusUpdate):
    entity = await TwinEntityService.change_status(entity_id, data.status, data.reason)
    if not entity:
        raise HTTPException(status_code=404, detail="孪生实体不存在")
    return success_response(data=await entity.to_dict(), msg="状态已更新")


@twin_entity_router.post("/{entity_id}/properties", summary="更新孪生实体属性")
async def update_entity_properties(entity_id: int, data: EntityPropertiesUpdate):
    entity = await TwinEntityService.update_properties(entity_id, data.properties)
    if not entity:
        raise HTTPException(status_code=404, detail="孪生实体不存在")
    return success_response(data=await entity.to_dict(), msg="属性已更新")
