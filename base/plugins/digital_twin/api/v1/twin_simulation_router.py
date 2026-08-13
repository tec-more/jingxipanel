"""孪生仿真路由"""
from typing import Optional
from fastapi import APIRouter, HTTPException

try:
    from base.plugins.digital_twin.services.digital_twin_service import TwinSimulationService
    from base.plugins.digital_twin.schemas.digital_twin_schema import TwinSimulationCreate
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
    class TwinSimulationService: pass
    class TwinSimulationCreate: pass
    def success_response(**kw): return {}

twin_simulation_router = APIRouter(prefix="/simulation", tags=["孪生仿真"])


@twin_simulation_router.get("/", summary="获取仿真任务列表")
async def list_simulations(
    page: int = 1,
    page_size: int = 10,
    sim_code: Optional[str] = None,
    sim_name: Optional[str] = None,
    sim_type: Optional[str] = None,
    status: Optional[str] = None,
    created_by: Optional[str] = None,
):
    items, total = await TwinSimulationService.get_list(
        page=page, page_size=page_size,
        sim_code=sim_code, sim_name=sim_name,
        sim_type=sim_type, status=status, created_by=created_by,
    )
    data = [await i.to_dict() for i in items]
    return success_response(data={"items": data, "total": total, "page": page, "page_size": page_size})


@twin_simulation_router.get("/{sim_id}", summary="获取仿真任务详情")
async def get_simulation(sim_id: int):
    sim = await TwinSimulationService.get_by_id(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail="仿真任务不存在")
    return success_response(data=await sim.to_dict())


@twin_simulation_router.post("/", summary="创建仿真任务")
async def create_simulation(data: TwinSimulationCreate):
    sim = await TwinSimulationService.create_simulation(data)
    # 异步启动仿真执行（后台任务，非阻塞）
    try:
        from base.plugins.digital_twin.services.simulation_runner import schedule_simulation
        await schedule_simulation(sim.id)
    except Exception:
        # 调度失败不影响创建结果
        pass
    return success_response(data=await sim.to_dict(), msg="仿真任务已创建")


@twin_simulation_router.post("/{sim_id}/cancel", summary="取消仿真任务")
async def cancel_simulation(sim_id: int):
    try:
        sim = await TwinSimulationService.cancel_simulation(sim_id)
        if not sim:
            raise HTTPException(status_code=404, detail="仿真任务不存在")
        return success_response(data=await sim.to_dict(), msg="仿真已取消")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
