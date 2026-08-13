"""
数字孪生数据模型
包含孪生实体、场景、数据采点、事件、仿真任务
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    from tortoise import fields
    from base.common.model import BaseModel, TimestampMixin
except ImportError:
    # 兼容静态导入失败的场景（如未初始化 ORM 时被引用）
    class BaseModel:
        id = None

    class TimestampMixin:
        created_at = None
        updated_at = None

    class fields:
        @staticmethod
        def CharField(**kwargs): return kwargs
        @staticmethod
        def BooleanField(**kwargs): return kwargs
        @staticmethod
        def IntField(**kwargs): return kwargs
        @staticmethod
        def FloatField(**kwargs): return kwargs
        @staticmethod
        def DatetimeField(**kwargs): return kwargs
        @staticmethod
        def TextField(**kwargs): return kwargs
        @staticmethod
        def JSONField(**kwargs): return kwargs
        @staticmethod
        def DecimalField(**kwargs): return kwargs


class TwinEntity(BaseModel, TimestampMixin):
    """孪生实体 - 物理对象（设备/产品/工序/产线）的数字化映射"""
    verbose_name = "孪生实体"

    entity_code = fields.CharField(max_length=100, unique=True, description="实体编码", index=True)
    entity_name = fields.CharField(max_length=255, description="实体名称", index=True)
    entity_type = fields.CharField(max_length=50, description="实体类型：equipment/product/process/production_line", index=True)
    source_code = fields.CharField(max_length=100, null=True, description="来源对象编码（如设备编码）", index=True)
    entity_model = fields.CharField(max_length=500, null=True, description="3D 模型文件路径")
    entity_icon = fields.CharField(max_length=255, null=True, description="图标")
    parent_code = fields.CharField(max_length=100, null=True, description="父实体编码（层级关系）", index=True)
    position_x = fields.FloatField(default=0, description="场景 X 坐标")
    position_y = fields.FloatField(default=0, description="场景 Y 坐标")
    position_z = fields.FloatField(default=0, description="场景 Z 坐标")
    rotation_x = fields.FloatField(default=0, description="绕 X 轴旋转角度")
    rotation_y = fields.FloatField(default=0, description="绕 Y 轴旋转角度")
    rotation_z = fields.FloatField(default=0, description="绕 Z 轴旋转角度")
    scale = fields.FloatField(default=1, description="缩放比例")
    current_status = fields.CharField(max_length=20, default="normal", description="当前状态：normal/warning/error/maintenance/offline", index=True)
    properties = fields.JSONField(null=True, description="属性字典（温度、振动、转速等动态属性）")
    source_type = fields.CharField(max_length=20, default="manual", description="数据来源：iot/manual/simulated")
    refresh_interval = fields.IntField(default=30, description="数据刷新间隔（秒）")
    last_sync_time = fields.DatetimeField(null=True, description="最后同步时间")
    description = fields.TextField(null=True, description="描述")
    is_active = fields.BooleanField(default=True, description="是否启用", index=True)

    class Meta:
        table = "dt_twin_entity"

    async def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity_code": self.entity_code,
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "source_code": self.source_code,
            "entity_model": self.entity_model,
            "entity_icon": self.entity_icon,
            "parent_code": self.parent_code,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "position_z": self.position_z,
            "rotation_x": self.rotation_x,
            "rotation_y": self.rotation_y,
            "rotation_z": self.rotation_z,
            "scale": self.scale,
            "current_status": self.current_status,
            "properties": self.properties,
            "source_type": self.source_type,
            "refresh_interval": self.refresh_interval,
            "last_sync_time": self.last_sync_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_sync_time else None,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }


class TwinScene(BaseModel, TimestampMixin):
    """孪生场景 - 多个实体组成的可视化场景"""
    verbose_name = "孪生场景"

    scene_code = fields.CharField(max_length=100, unique=True, description="场景编码", index=True)
    scene_name = fields.CharField(max_length=255, description="场景名称", index=True)
    scene_type = fields.CharField(max_length=50, default="custom", description="场景类型：factory/workshop/production_line/custom", index=True)
    scene_config = fields.JSONField(null=True, description="场景配置（背景、光照、视角等）")
    entity_ids = fields.JSONField(null=True, description="包含的实体 ID 列表")
    thumbnail = fields.CharField(max_length=500, null=True, description="场景缩略图路径")
    description = fields.TextField(null=True, description="描述")
    is_active = fields.BooleanField(default=True, description="是否启用", index=True)

    class Meta:
        table = "dt_twin_scene"

    async def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "scene_code": self.scene_code,
            "scene_name": self.scene_name,
            "scene_type": self.scene_type,
            "scene_config": self.scene_config,
            "entity_ids": self.entity_ids,
            "thumbnail": self.thumbnail,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }


class TwinDataPoint(BaseModel, TimestampMixin):
    """孪生数据采点 - 实体的时序数据记录"""
    verbose_name = "孪生数据采点"

    entity_code = fields.CharField(max_length=100, description="关联实体编码", index=True)
    metric_code = fields.CharField(max_length=100, description="指标编码", index=True)
    metric_name = fields.CharField(max_length=255, description="指标名称")
    metric_type = fields.CharField(max_length=50, description="指标类型：temperature/vibration/pressure/current/custom")
    value = fields.FloatField(description="数值")
    unit = fields.CharField(max_length=20, null=True, description="单位")
    quality = fields.CharField(max_length=20, default="good", description="数据质量：good/bad/uncertain")
    source = fields.CharField(max_length=20, default="manual", description="数据来源：iot/sensor/api/manual")
    collected_at = fields.DatetimeField(description="采集时间", index=True)

    class Meta:
        table = "dt_twin_data_point"
        indexes = (("entity_code", "metric_code", "collected_at"),)

    async def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "entity_code": self.entity_code,
            "metric_code": self.metric_code,
            "metric_name": self.metric_name,
            "metric_type": self.metric_type,
            "value": self.value,
            "unit": self.unit,
            "quality": self.quality,
            "source": self.source,
            "collected_at": self.collected_at.strftime("%Y-%m-%d %H:%M:%S") if self.collected_at else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }


class TwinEvent(BaseModel, TimestampMixin):
    """孪生事件 - 实体状态变更与告警记录"""
    verbose_name = "孪生事件"

    event_code = fields.CharField(max_length=100, unique=True, description="事件编码", index=True)
    entity_code = fields.CharField(max_length=100, description="关联实体编码", index=True)
    entity_name = fields.CharField(max_length=255, null=True, description="实体名称（冗余便于查询）")
    event_type = fields.CharField(max_length=30, description="事件类型：state_change/alarm/maintenance/anomaly", index=True)
    event_level = fields.CharField(max_length=20, default="info", description="事件级别：info/warning/error/critical", index=True)
    from_status = fields.CharField(max_length=20, null=True, description="变更前状态")
    to_status = fields.CharField(max_length=20, null=True, description="变更后状态")
    title = fields.CharField(max_length=255, null=True, description="事件标题")
    description = fields.TextField(null=True, description="事件描述")
    payload = fields.JSONField(null=True, description="事件附加数据")
    is_resolved = fields.BooleanField(default=False, description="是否已处理", index=True)
    resolved_at = fields.DatetimeField(null=True, description="处理时间")
    resolved_by = fields.CharField(max_length=100, null=True, description="处理人")
    resolve_remark = fields.TextField(null=True, description="处理备注")

    class Meta:
        table = "dt_twin_event"

    async def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event_code": self.event_code,
            "entity_code": self.entity_code,
            "entity_name": self.entity_name,
            "event_type": self.event_type,
            "event_level": self.event_level,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "title": self.title,
            "description": self.description,
            "payload": self.payload,
            "is_resolved": self.is_resolved,
            "resolved_at": self.resolved_at.strftime("%Y-%m-%d %H:%M:%S") if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolve_remark": self.resolve_remark,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }


class TwinSimulation(BaseModel, TimestampMixin):
    """孪生仿真任务 - 状态预测、故障预测、优化仿真"""
    verbose_name = "孪生仿真"

    sim_code = fields.CharField(max_length=100, unique=True, description="仿真编码", index=True)
    sim_name = fields.CharField(max_length=255, description="仿真名称")
    sim_type = fields.CharField(max_length=30, description="仿真类型：state_prediction/failure_forecast/optimization", index=True)
    entity_scope = fields.JSONField(null=True, description="仿真范围（实体编码列表或场景编码）")
    input_params = fields.JSONField(null=True, description="输入参数")
    output_result = fields.JSONField(null=True, description="输出结果")
    status = fields.CharField(max_length=20, default="pending", description="状态：pending/running/completed/failed", index=True)
    progress = fields.FloatField(default=0, description="进度百分比 0-100")
    started_at = fields.DatetimeField(null=True, description="开始时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")
    error_message = fields.TextField(null=True, description="错误信息")
    created_by = fields.CharField(max_length=100, null=True, description="创建人")

    class Meta:
        table = "dt_twin_simulation"

    async def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sim_code": self.sim_code,
            "sim_name": self.sim_name,
            "sim_type": self.sim_type,
            "entity_scope": self.entity_scope,
            "input_params": self.input_params,
            "output_result": self.output_result,
            "status": self.status,
            "progress": self.progress,
            "started_at": self.started_at.strftime("%Y-%m-%d %H:%M:%S") if self.started_at else None,
            "completed_at": self.completed_at.strftime("%Y-%m-%d %H:%M:%S") if self.completed_at else None,
            "error_message": self.error_message,
            "created_by": self.created_by,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }
