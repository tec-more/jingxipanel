"""
数字孪生业务服务层
包含孪生实体、场景、数据采点、事件、仿真的业务逻辑
"""
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from uuid import uuid4

try:
    from tortoise.expressions import Q
    from base.plugins.digital_twin.models.digital_twin import (
        TwinEntity, TwinScene, TwinDataPoint, TwinEvent, TwinSimulation
    )
    from base.plugins.digital_twin.schemas.digital_twin_schema import (
        TwinEntityCreate, TwinEntityUpdate,
        TwinSceneCreate, TwinSceneUpdate,
        TwinDataPointCreate, TwinDataPointBatchIngest,
        TwinEventCreate, TwinEventResolve,
        TwinSimulationCreate,
    )
except ImportError:
    # 静态导入失败的兜底（与 equipment 模块保持一致）
    Q = None

    class _Dummy:
        @classmethod
        async def filter(cls, **kw): return _QS()
        @classmethod
        async def all(cls): return _QS()
        @classmethod
        async def create(cls, **kw): return None
        @classmethod
        async def get_or_none(cls, **kw): return None

    class _QS:
        async def first(self): return None
        async def count(self): return 0
        async def exists(self): return False
        async def delete(self): return 0
        async def offset(self, n): return self
        async def limit(self, n): return self
        async def order_by(self, s): return self
        def filter(self, **kw): return self
        def exclude(self, **kw): return self

    TwinEntity = TwinScene = TwinDataPoint = TwinEvent = TwinSimulation = _Dummy


async def _broadcast(event_type: str, data: Dict[str, Any]) -> None:
    """向所有在线用户推送孪生事件（失败静默）"""
    try:
        from base.plugins.digital_twin.services.twin_ws_manager import broadcast_twin_event
        await broadcast_twin_event(event_type, data)
    except Exception:
        pass


# ==================== 孪生实体服务 ====================

class TwinEntityService:
    """孪生实体服务"""

    @staticmethod
    async def get_by_id(entity_id: int) -> Optional[TwinEntity]:
        return await TwinEntity.filter(id=entity_id).first()

    @staticmethod
    async def get_by_code(entity_code: str) -> Optional[TwinEntity]:
        return await TwinEntity.filter(entity_code=entity_code).first()

    @staticmethod
    async def create_entity(data: TwinEntityCreate) -> TwinEntity:
        if await TwinEntityService.check_code_exists(data.entity_code):
            raise ValueError("实体编码已存在")
        payload = data.model_dump()
        return await TwinEntity.create(**payload)

    @staticmethod
    async def update_entity(entity_id: int, data: TwinEntityUpdate) -> Optional[TwinEntity]:
        entity = await TwinEntity.filter(id=entity_id).first()
        if not entity:
            return None
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return entity
        await entity.update_from_dict(update_data).save()
        return entity

    @staticmethod
    async def delete_entity(entity_id: int) -> bool:
        deleted = await TwinEntity.filter(id=entity_id).delete()
        return deleted > 0

    @staticmethod
    async def change_status(entity_id: int, status: str, reason: Optional[str] = None) -> Optional[TwinEntity]:
        entity = await TwinEntity.filter(id=entity_id).first()
        if not entity:
            return None
        old_status = entity.current_status
        if old_status == status:
            return entity
        entity.current_status = status
        entity.last_sync_time = datetime.now()
        await entity.save()

        # 自动产生状态变更事件
        await TwinEventService.create_event(TwinEventCreate(
            event_code=f"EVT-{uuid4().hex[:12].upper()}",
            entity_code=entity.entity_code,
            entity_name=entity.entity_name,
            event_type="state_change",
            event_level="info" if status == "normal" else "warning",
            from_status=old_status,
            to_status=status,
            title=f"实体状态变更：{old_status} -> {status}",
            description=reason or f"实体 {entity.entity_name} 状态由 {old_status} 变更为 {status}",
            payload={"reason": reason} if reason else None,
        ))
        # 推送 WebSocket 通知
        await _broadcast("entity.status.changed", await entity.to_dict())
        return entity

    @staticmethod
    async def update_properties(entity_id: int, properties: Dict[str, Any]) -> Optional[TwinEntity]:
        entity = await TwinEntity.filter(id=entity_id).first()
        if not entity:
            return None
        current = entity.properties or {}
        current.update(properties)
        entity.properties = current
        entity.last_sync_time = datetime.now()
        await entity.save()
        return entity

    @staticmethod
    async def get_list(
        page: int = 1, page_size: int = 10,
        entity_code: Optional[str] = None,
        entity_name: Optional[str] = None,
        entity_type: Optional[str] = None,
        current_status: Optional[str] = None,
        parent_code: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[TwinEntity], int]:
        query = TwinEntity.all()
        if entity_code:
            query = query.filter(entity_code__icontains=entity_code)
        if entity_name:
            query = query.filter(entity_name__icontains=entity_name)
        if entity_type:
            query = query.filter(entity_type=entity_type)
        if current_status:
            query = query.filter(current_status=current_status)
        if parent_code:
            query = query.filter(parent_code=parent_code)
        if is_active is not None:
            query = query.filter(is_active=is_active)
        total = await query.count()
        offset = (page - 1) * page_size
        items = await query.offset(offset).limit(page_size).order_by("-created_at")
        return items, total

    @staticmethod
    async def check_code_exists(code: str, exclude_id: Optional[int] = None) -> bool:
        query = TwinEntity.filter(entity_code=code)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        return await query.exists()


# ==================== 孪生场景服务 ====================

class TwinSceneService:
    """孪生场景服务"""

    @staticmethod
    async def get_by_id(scene_id: int) -> Optional[TwinScene]:
        return await TwinScene.filter(id=scene_id).first()

    @staticmethod
    async def get_by_code(scene_code: str) -> Optional[TwinScene]:
        return await TwinScene.filter(scene_code=scene_code).first()

    @staticmethod
    async def create_scene(data: TwinSceneCreate) -> TwinScene:
        if await TwinSceneService.check_code_exists(data.scene_code):
            raise ValueError("场景编码已存在")
        return await TwinScene.create(**data.model_dump())

    @staticmethod
    async def update_scene(scene_id: int, data: TwinSceneUpdate) -> Optional[TwinScene]:
        scene = await TwinScene.filter(id=scene_id).first()
        if not scene:
            return None
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return scene
        await scene.update_from_dict(update_data).save()
        return scene

    @staticmethod
    async def delete_scene(scene_id: int) -> bool:
        deleted = await TwinScene.filter(id=scene_id).delete()
        return deleted > 0

    @staticmethod
    async def set_entities(scene_id: int, entity_ids: List[int]) -> Optional[TwinScene]:
        scene = await TwinScene.filter(id=scene_id).first()
        if not scene:
            return None
        scene.entity_ids = entity_ids
        await scene.save()
        return scene

    @staticmethod
    async def get_list(
        page: int = 1, page_size: int = 10,
        scene_code: Optional[str] = None,
        scene_name: Optional[str] = None,
        scene_type: Optional[str] = None,
    ) -> Tuple[List[TwinScene], int]:
        query = TwinScene.all()
        if scene_code:
            query = query.filter(scene_code__icontains=scene_code)
        if scene_name:
            query = query.filter(scene_name__icontains=scene_name)
        if scene_type:
            query = query.filter(scene_type=scene_type)
        total = await query.count()
        offset = (page - 1) * page_size
        items = await query.offset(offset).limit(page_size).order_by("-created_at")
        return items, total

    @staticmethod
    async def check_code_exists(code: str, exclude_id: Optional[int] = None) -> bool:
        query = TwinScene.filter(scene_code=code)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        return await query.exists()


# ==================== 孪生数据采点服务 ====================

class TwinDataService:
    """孪生数据采点服务"""

    @staticmethod
    async def ingest_single(data: TwinDataPointCreate) -> TwinDataPoint:
        point = await TwinDataPoint.create(**data.model_dump())
        # 同步更新实体的最新属性与同步时间
        await TwinDataService._sync_entity_property(data.entity_code, data.metric_code, data.value, data.unit)
        await _broadcast("data.ingested", {"entity_code": data.entity_code, "metric_code": data.metric_code, "value": data.value, "unit": data.unit})
        return point

    @staticmethod
    async def ingest_batch(payload: TwinDataPointBatchIngest) -> int:
        points = payload.points
        # 批量构造
        records = [TwinDataPoint(**p.model_dump()) for p in points]
        await TwinDataPoint.bulk_create(records)
        # 同步实体属性（按 entity_code 分组取最新值）
        entity_metrics: Dict[str, Dict[str, Any]] = {}
        for p in points:
            entity_metrics.setdefault(p.entity_code, {})[p.metric_code] = (p.value, p.unit)
        for entity_code, metrics in entity_metrics.items():
            entity = await TwinEntity.filter(entity_code=entity_code).first()
            if entity:
                props = entity.properties or {}
                for code, (val, unit) in metrics.items():
                    props[code] = {"value": val, "unit": unit}
                entity.properties = props
                entity.last_sync_time = datetime.now()
                await entity.save()
        return len(records)

    @staticmethod
    async def get_realtime(entity_code: str, metric_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取实体最新数据点（每个指标取最新一条）"""
        query = TwinDataPoint.filter(entity_code=entity_code)
        if metric_code:
            query = query.filter(metric_code=metric_code)
        # 取近 N 条用于聚合
        recent = await query.order_by("-collected_at").limit(200)
        # 按 metric_code 取最新
        latest_map: Dict[str, TwinDataPoint] = {}
        for p in recent:
            if p.metric_code not in latest_map:
                latest_map[p.metric_code] = p
        return [await p.to_dict() for p in latest_map.values()]

    @staticmethod
    async def get_history(
        entity_code: str,
        metric_code: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        query = TwinDataPoint.filter(entity_code=entity_code)
        if metric_code:
            query = query.filter(metric_code=metric_code)
        if start_time:
            query = query.filter(collected_at__gte=start_time)
        if end_time:
            query = query.filter(collected_at__lte=end_time)
        items = await query.order_by("-collected_at").limit(limit)
        # 返回时间升序便于绘图
        result = [await p.to_dict() for p in items]
        result.reverse()
        return result

    @staticmethod
    async def _sync_entity_property(entity_code: str, metric_code: str, value: float, unit: Optional[str]):
        """同步最新数据点到实体属性"""
        entity = await TwinEntity.filter(entity_code=entity_code).first()
        if not entity:
            return
        props = entity.properties or {}
        props[metric_code] = {"value": value, "unit": unit, "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        entity.properties = props
        entity.last_sync_time = datetime.now()
        await entity.save()


# ==================== 孪生事件服务 ====================

class TwinEventService:
    """孪生事件服务"""

    @staticmethod
    async def get_by_id(event_id: int) -> Optional[TwinEvent]:
        return await TwinEvent.filter(id=event_id).first()

    @staticmethod
    async def create_event(data: TwinEventCreate) -> TwinEvent:
        # 自动补充实体名称
        if not data.entity_name:
            entity = await TwinEntity.filter(entity_code=data.entity_code).first()
            if entity:
                data.entity_name = entity.entity_name
        event = await TwinEvent.create(**data.model_dump())
        await _broadcast("event.created", await event.to_dict())
        return event

    @staticmethod
    async def resolve_event(event_id: int, payload: TwinEventResolve) -> Optional[TwinEvent]:
        event = await TwinEvent.filter(id=event_id).first()
        if not event:
            return None
        if event.is_resolved:
            raise ValueError("事件已处理，无法重复处理")
        event.is_resolved = True
        event.resolved_at = datetime.now()
        event.resolved_by = payload.resolved_by
        event.resolve_remark = payload.resolve_remark
        await event.save()
        return event

    @staticmethod
    async def get_list(
        page: int = 1, page_size: int = 10,
        event_code: Optional[str] = None,
        entity_code: Optional[str] = None,
        event_type: Optional[str] = None,
        event_level: Optional[str] = None,
        is_resolved: Optional[bool] = None,
    ) -> Tuple[List[TwinEvent], int]:
        query = TwinEvent.all()
        if event_code:
            query = query.filter(event_code__icontains=event_code)
        if entity_code:
            query = query.filter(entity_code=entity_code)
        if event_type:
            query = query.filter(event_type=event_type)
        if event_level:
            query = query.filter(event_level=event_level)
        if is_resolved is not None:
            query = query.filter(is_resolved=is_resolved)
        total = await query.count()
        offset = (page - 1) * page_size
        items = await query.offset(offset).limit(page_size).order_by("-created_at")
        return items, total


# ==================== 孪生仿真服务 ====================

class TwinSimulationService:
    """孪生仿真服务"""

    @staticmethod
    async def get_by_id(sim_id: int) -> Optional[TwinSimulation]:
        return await TwinSimulation.filter(id=sim_id).first()

    @staticmethod
    async def create_simulation(data: TwinSimulationCreate) -> TwinSimulation:
        return await TwinSimulation.create(**data.model_dump())

    @staticmethod
    async def update_result(sim_id: int, result: Dict[str, Any], progress: float = 100) -> Optional[TwinSimulation]:
        sim = await TwinSimulation.filter(id=sim_id).first()
        if not sim:
            return None
        sim.output_result = result
        sim.progress = progress
        if progress >= 100:
            sim.status = "completed"
            sim.completed_at = datetime.now()
        await sim.save()
        return sim

    @staticmethod
    async def cancel_simulation(sim_id: int) -> Optional[TwinSimulation]:
        sim = await TwinSimulation.filter(id=sim_id).first()
        if not sim:
            return None
        if sim.status in ("completed", "failed"):
            raise ValueError(f"仿真当前状态为 {sim.status}，无法取消")
        sim.status = "failed"
        sim.error_message = "用户手动取消"
        sim.completed_at = datetime.now()
        await sim.save()
        return sim

    @staticmethod
    async def get_list(
        page: int = 1, page_size: int = 10,
        sim_code: Optional[str] = None,
        sim_name: Optional[str] = None,
        sim_type: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Tuple[List[TwinSimulation], int]:
        query = TwinSimulation.all()
        if sim_code:
            query = query.filter(sim_code__icontains=sim_code)
        if sim_name:
            query = query.filter(sim_name__icontains=sim_name)
        if sim_type:
            query = query.filter(sim_type=sim_type)
        if status:
            query = query.filter(status=status)
        if created_by:
            query = query.filter(created_by=created_by)
        total = await query.count()
        offset = (page - 1) * page_size
        items = await query.offset(offset).limit(page_size).order_by("-created_at")
        return items, total


# ==================== 看板统计服务 ====================

class TwinDashboardService:
    """数字孪生看板统计服务"""

    @staticmethod
    async def get_overview() -> Dict[str, Any]:
        total_entities = await TwinEntity.all().count()
        active_entities = await TwinEntity.filter(is_active=True).count()
        total_scenes = await TwinScene.all().count()
        unresolved_events = await TwinEvent.filter(is_resolved=False).count()
        running_sims = await TwinSimulation.filter(status="running").count()
        return {
            "total_entities": total_entities,
            "active_entities": active_entities,
            "total_scenes": total_scenes,
            "unresolved_events": unresolved_events,
            "running_simulations": running_sims,
        }

    @staticmethod
    async def get_status_distribution() -> List[Dict[str, Any]]:
        """按 current_status 分组统计实体数量"""
        rows = await TwinEntity.all().only("current_status")
        counter: Dict[str, int] = {}
        for r in rows:
            counter[r.current_status] = counter.get(r.current_status, 0) + 1
        return [{"status": k, "count": v} for k, v in counter.items()]

    @staticmethod
    async def get_alarm_summary() -> Dict[str, Any]:
        """告警事件汇总"""
        total = await TwinEvent.all().count()
        unresolved = await TwinEvent.filter(is_resolved=False).count()
        critical = await TwinEvent.filter(is_resolved=False, event_level="critical").count()
        error = await TwinEvent.filter(is_resolved=False, event_level="error").count()
        warning = await TwinEvent.filter(is_resolved=False, event_level="warning").count()
        info = await TwinEvent.filter(is_resolved=False, event_level="info").count()
        return {
            "total": total,
            "unresolved": unresolved,
            "by_level": {
                "critical": critical,
                "error": error,
                "warning": warning,
                "info": info,
            },
        }
