"""孪生数据采点路由"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException

try:
    from base.plugins.digital_twin.services.digital_twin_service import TwinDataService
    from base.plugins.digital_twin.schemas.digital_twin_schema import (
        TwinDataPointCreate, TwinDataPointBatchIngest,
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
    class TwinDataService: pass
    class TwinDataPointCreate: pass
    class TwinDataPointBatchIngest: pass
    def success_response(**kw): return {}

twin_data_router = APIRouter(prefix="/data", tags=["孪生数据"])


@twin_data_router.get("/realtime", summary="获取实时数据（最新值）")
async def get_realtime(entity_code: str, metric_code: Optional[str] = None):
    points = await TwinDataService.get_realtime(entity_code, metric_code)
    return success_response(data={"entity_code": entity_code, "points": points})


@twin_data_router.get("/history", summary="获取历史数据")
async def get_history(
    entity_code: str,
    metric_code: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 500,
):
    points = await TwinDataService.get_history(
        entity_code=entity_code, metric_code=metric_code,
        start_time=start_time, end_time=end_time, limit=limit,
    )
    return success_response(data={"entity_code": entity_code, "metric_code": metric_code, "points": points, "count": len(points)})


@twin_data_router.post("/ingest", summary="写入单个数据点")
async def ingest_single(data: TwinDataPointCreate):
    point = await TwinDataService.ingest_single(data)
    return success_response(data=await point.to_dict(), msg="数据已写入")


@twin_data_router.post("/ingest/batch", summary="批量写入数据点")
async def ingest_batch(data: TwinDataPointBatchIngest):
    count = await TwinDataService.ingest_batch(data)
    return success_response(data={"count": count}, msg=f"成功写入 {count} 条数据")
