"""孪生看板统计路由"""
from fastapi import APIRouter

try:
    from base.plugins.digital_twin.services.digital_twin_service import TwinDashboardService
    from base.common.response import success_response
except ImportError:
    class APIRouter:
        def __init__(self, prefix="", tags=None): pass
        def get(self, p, **kw):
            def d(f): return f
            return d
    class TwinDashboardService: pass
    def success_response(**kw): return {}

twin_dashboard_router = APIRouter(prefix="/dashboard", tags=["孪生看板"])


@twin_dashboard_router.get("/overview", summary="看板总览")
async def dashboard_overview():
    data = await TwinDashboardService.get_overview()
    return success_response(data=data)


@twin_dashboard_router.get("/status-distribution", summary="实体状态分布")
async def dashboard_status_distribution():
    data = await TwinDashboardService.get_status_distribution()
    return success_response(data=data)


@twin_dashboard_router.get("/alarm-summary", summary="告警事件汇总")
async def dashboard_alarm_summary():
    data = await TwinDashboardService.get_alarm_summary()
    return success_response(data=data)
