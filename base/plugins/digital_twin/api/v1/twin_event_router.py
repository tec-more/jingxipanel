"""孪生事件路由"""
from typing import Optional
from fastapi import APIRouter, HTTPException

try:
    from base.plugins.digital_twin.services.digital_twin_service import TwinEventService
    from base.plugins.digital_twin.schemas.digital_twin_schema import (
        TwinEventCreate, TwinEventResolve,
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
    class HTTPException(Exception):
        def __init__(self, status_code, detail): pass
    class TwinEventService: pass
    class TwinEventCreate: pass
    class TwinEventResolve: pass
    def success_response(**kw): return {}

twin_event_router = APIRouter(prefix="/event", tags=["孪生事件"])


@twin_event_router.get("/", summary="获取孪生事件列表")
async def list_events(
    page: int = 1,
    page_size: int = 10,
    event_code: Optional[str] = None,
    entity_code: Optional[str] = None,
    event_type: Optional[str] = None,
    event_level: Optional[str] = None,
    is_resolved: Optional[bool] = None,
):
    items, total = await TwinEventService.get_list(
        page=page, page_size=page_size,
        event_code=event_code, entity_code=entity_code,
        event_type=event_type, event_level=event_level, is_resolved=is_resolved,
    )
    data = [await i.to_dict() for i in items]
    return success_response(data={"items": data, "total": total, "page": page, "page_size": page_size})


@twin_event_router.get("/{event_id}", summary="获取事件详情")
async def get_event(event_id: int):
    event = await TwinEventService.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="孪生事件不存在")
    return success_response(data=await event.to_dict())


@twin_event_router.post("/", summary="创建孪生事件")
async def create_event(data: TwinEventCreate):
    event = await TwinEventService.create_event(data)
    return success_response(data=await event.to_dict(), msg="事件已创建")


@twin_event_router.post("/{event_id}/resolve", summary="处理孪生事件")
async def resolve_event(event_id: int, data: TwinEventResolve):
    try:
        event = await TwinEventService.resolve_event(event_id, data)
        if not event:
            raise HTTPException(status_code=404, detail="孪生事件不存在")
        return success_response(data=await event.to_dict(), msg="事件已处理")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
