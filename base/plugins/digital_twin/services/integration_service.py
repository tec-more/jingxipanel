"""
数字孪生集成服务
负责与其他业务模块（equipment、mes）的数据同步
将物理对象（设备、工作中心等）映射为孪生实体
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime
from loguru import logger


# 设备状态 → 孪生实体状态映射
EQUIPMENT_STATUS_MAP = {
    "idle": "normal",
    "running": "normal",
    "maintenance": "maintenance",
    "fault": "error",
    "down": "offline",
}


class TwinIntegrationService:
    """孪生集成服务 - 与 equipment/mes 模块的数据同步"""

    @staticmethod
    async def sync_from_equipment(equipment_codes: List[str] = None) -> Dict[str, Any]:
        """从 equipment 模块同步设备到孪生实体

        Args:
            equipment_codes: 指定设备编码列表，None 则同步全部
        Returns:
            同步结果统计
        """
        try:
            from base.plugins.equipment.models.equipment import Equipment
            from base.plugins.digital_twin.models.digital_twin import TwinEntity
        except ImportError:
            return {"success": False, "message": "equipment 或 digital_twin 模块未启用"}

        # 查询设备
        query = Equipment.all()
        if equipment_codes:
            query = query.filter(equipment_code__in=equipment_codes)
        equipments = await query

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for eq in equipments:
            twin_code = f"EQ-{eq.equipment_code}"
            existing = await TwinEntity.filter(entity_code=twin_code).first()

            twin_status = EQUIPMENT_STATUS_MAP.get(eq.status, "normal")
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if existing:
                # 更新已有孪生实体
                need_update = False
                if existing.entity_name != eq.equipment_name:
                    existing.entity_name = eq.equipment_name
                    need_update = True
                if existing.current_status != twin_status:
                    existing.current_status = twin_status
                    need_update = True
                if existing.source_code != eq.equipment_code:
                    existing.source_code = eq.equipment_code
                    need_update = True
                if need_update:
                    existing.last_sync_time = datetime.now()
                    await existing.save()
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                # 创建新孪生实体
                await TwinEntity.create(
                    entity_code=twin_code,
                    entity_name=eq.equipment_name,
                    entity_type="equipment",
                    source_code=eq.equipment_code,
                    current_status=twin_status,
                    source_type="manual",
                    properties={
                        "equipment_type": eq.equipment_type,
                        "model": eq.model,
                        "manufacturer": eq.manufacturer,
                        "location": eq.location,
                        "synced_at": now_str,
                    },
                    description=f"从设备模块自动同步：{eq.equipment_code}",
                    last_sync_time=datetime.now(),
                )
                created_count += 1

        result = {
            "success": True,
            "source": "equipment",
            "total": len(equipments),
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
        }
        logger.info(f"[twin.integration] 从 equipment 同步完成: {result}")
        return result

    @staticmethod
    async def sync_from_mes_workcenter() -> Dict[str, Any]:
        """从 mes 模块同步工作中心到孪生实体"""
        try:
            from base.plugins.mes.models.base_data import WorkCenter
            from base.plugins.digital_twin.models.digital_twin import TwinEntity
        except ImportError:
            return {"success": False, "message": "mes 或 digital_twin 模块未启用"}

        workcenters = await WorkCenter.filter(is_active=True).all()
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for wc in workcenters:
            twin_code = f"WC-{wc.work_center_code}"
            existing = await TwinEntity.filter(entity_code=twin_code).first()

            if existing:
                need_update = False
                if existing.entity_name != wc.work_center_name:
                    existing.entity_name = wc.work_center_name
                    need_update = True
                if need_update:
                    existing.last_sync_time = datetime.now()
                    await existing.save()
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                await TwinEntity.create(
                    entity_code=twin_code,
                    entity_name=wc.work_center_name,
                    entity_type="production_line",
                    source_code=wc.work_center_code,
                    current_status="normal" if wc.is_active else "offline",
                    source_type="manual",
                    properties={
                        "department": wc.department,
                        "location": wc.location,
                        "capacity": wc.capacity,
                    },
                    description=f"从 mes 工作中心自动同步：{wc.work_center_code}",
                    last_sync_time=datetime.now(),
                )
                created_count += 1

        result = {
            "success": True,
            "source": "mes_workcenter",
            "total": len(workcenters),
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
        }
        logger.info(f"[twin.integration] 从 mes 工作中心同步完成: {result}")
        return result

    @staticmethod
    async def sync_equipment_status(equipment_code: str, new_status: str) -> bool:
        """设备状态变更时同步到孪生实体（供 equipment 模块调用）

        Args:
            equipment_code: 设备编码
            new_status: 设备新状态（equipment 模块的状态值）
        Returns:
            是否成功同步
        """
        try:
            from base.plugins.digital_twin.models.digital_twin import TwinEntity
        except ImportError:
            return False

        twin_code = f"EQ-{equipment_code}"
        twin_status = EQUIPMENT_STATUS_MAP.get(new_status, "normal")
        entity = await TwinEntity.filter(entity_code=twin_code).first()
        if not entity:
            return False

        if entity.current_status != twin_status:
            old_status = entity.current_status
            entity.current_status = twin_status
            entity.last_sync_time = datetime.now()
            await entity.save()

            # 自动产生状态变更事件
            try:
                from base.plugins.digital_twin.models.digital_twin import TwinEvent
                from uuid import uuid4
                await TwinEvent.create(
                    event_code=f"EVT-{uuid4().hex[:12].upper()}",
                    entity_code=entity.entity_code,
                    entity_name=entity.entity_name,
                    event_type="state_change",
                    event_level="info" if twin_status == "normal" else "warning",
                    from_status=old_status,
                    to_status=twin_status,
                    title=f"设备状态同步：{equipment_code} {old_status} -> {twin_status}",
                    description=f"设备 {equipment_code} 状态变更触发孪生实体同步",
                    payload={"equipment_code": equipment_code, "equipment_status": new_status},
                )
            except Exception as e:
                logger.warning(f"[twin.integration] 创建孪生事件失败: {e}")

            # 推送 WebSocket
            try:
                from base.plugins.digital_twin.services.twin_ws_manager import broadcast_twin_event
                await broadcast_twin_event("entity.status.changed", await entity.to_dict())
            except Exception:
                pass

        return True
