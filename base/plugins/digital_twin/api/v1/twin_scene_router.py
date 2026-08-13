"""孪生场景路由"""
from typing import Optional
from fastapi import APIRouter, HTTPException

try:
    from base.plugins.digital_twin.services.digital_twin_service import TwinSceneService
    from base.plugins.digital_twin.schemas.digital_twin_schema import (
        TwinSceneCreate, TwinSceneUpdate, SceneEntitiesUpdate,
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
    class TwinSceneService: pass
    class TwinSceneCreate: pass
    class TwinSceneUpdate: pass
    class SceneEntitiesUpdate: pass
    def success_response(**kw): return {}

twin_scene_router = APIRouter(prefix="/scene", tags=["孪生场景"])


@twin_scene_router.get("/", summary="获取孪生场景列表")
async def list_scenes(
    page: int = 1,
    page_size: int = 10,
    scene_code: Optional[str] = None,
    scene_name: Optional[str] = None,
    scene_type: Optional[str] = None,
):
    items, total = await TwinSceneService.get_list(
        page=page, page_size=page_size,
        scene_code=scene_code, scene_name=scene_name, scene_type=scene_type,
    )
    data = [await i.to_dict() for i in items]
    return success_response(data={"items": data, "total": total, "page": page, "page_size": page_size})


@twin_scene_router.get("/{scene_id}", summary="获取孪生场景详情")
async def get_scene(scene_id: int):
    scene = await TwinSceneService.get_by_id(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="孪生场景不存在")
    return success_response(data=await scene.to_dict())


@twin_scene_router.post("/", summary="创建孪生场景")
async def create_scene(data: TwinSceneCreate):
    try:
        scene = await TwinSceneService.create_scene(data)
        return success_response(data=await scene.to_dict(), msg="创建成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@twin_scene_router.put("/{scene_id}", summary="更新孪生场景")
async def update_scene(scene_id: int, data: TwinSceneUpdate):
    scene = await TwinSceneService.update_scene(scene_id, data)
    if not scene:
        raise HTTPException(status_code=404, detail="孪生场景不存在")
    return success_response(data=await scene.to_dict(), msg="更新成功")


@twin_scene_router.delete("/{scene_id}", summary="删除孪生场景")
async def delete_scene(scene_id: int):
    ok = await TwinSceneService.delete_scene(scene_id)
    if not ok:
        raise HTTPException(status_code=404, detail="孪生场景不存在")
    return success_response(msg="删除成功")


@twin_scene_router.post("/{scene_id}/entities", summary="设置场景关联实体")
async def set_scene_entities(scene_id: int, data: SceneEntitiesUpdate):
    scene = await TwinSceneService.set_entities(scene_id, data.entity_ids)
    if not scene:
        raise HTTPException(status_code=404, detail="孪生场景不存在")
    return success_response(data=await scene.to_dict(), msg="场景实体已更新")
