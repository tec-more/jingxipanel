"""
数字孪生 Pydantic Schema
定义请求/响应模型，用于 API 文档与参数校验
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== 孪生实体 ====================

class TwinEntityBase(BaseModel):
    entity_code: str = Field(..., min_length=1, max_length=100, description="实体编码")
    entity_name: str = Field(..., min_length=1, max_length=255, description="实体名称")
    entity_type: str = Field(..., max_length=50, description="实体类型：equipment/product/process/production_line")
    source_code: Optional[str] = Field(None, max_length=100, description="来源对象编码（如设备编码）")
    entity_model: Optional[str] = Field(None, max_length=500, description="3D 模型文件路径")
    entity_icon: Optional[str] = Field(None, max_length=255, description="图标")
    parent_code: Optional[str] = Field(None, max_length=100, description="父实体编码")
    position_x: float = Field(default=0, description="场景 X 坐标")
    position_y: float = Field(default=0, description="场景 Y 坐标")
    position_z: float = Field(default=0, description="场景 Z 坐标")
    rotation_x: float = Field(default=0, description="绕 X 轴旋转角度")
    rotation_y: float = Field(default=0, description="绕 Y 轴旋转角度")
    rotation_z: float = Field(default=0, description="绕 Z 轴旋转角度")
    scale: float = Field(default=1, description="缩放比例")
    current_status: str = Field(default="normal", max_length=20, description="当前状态")
    properties: Optional[Dict[str, Any]] = Field(None, description="属性字典")
    source_type: str = Field(default="manual", max_length=20, description="数据来源")
    refresh_interval: int = Field(default=30, ge=1, description="数据刷新间隔（秒）")
    description: Optional[str] = Field(None, description="描述")
    is_active: bool = Field(default=True, description="是否启用")


class TwinEntityCreate(TwinEntityBase):
    pass


class TwinEntityUpdate(BaseModel):
    entity_name: Optional[str] = Field(None, max_length=255)
    entity_type: Optional[str] = Field(None, max_length=50)
    source_code: Optional[str] = Field(None, max_length=100)
    entity_model: Optional[str] = Field(None, max_length=500)
    entity_icon: Optional[str] = Field(None, max_length=255)
    parent_code: Optional[str] = Field(None, max_length=100)
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    position_z: Optional[float] = None
    rotation_x: Optional[float] = None
    rotation_y: Optional[float] = None
    rotation_z: Optional[float] = None
    scale: Optional[float] = None
    current_status: Optional[str] = Field(None, max_length=20)
    properties: Optional[Dict[str, Any]] = None
    source_type: Optional[str] = Field(None, max_length=20)
    refresh_interval: Optional[int] = Field(None, ge=1)
    last_sync_time: Optional[datetime] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TwinEntityResponse(TwinEntityBase):
    id: int
    source_code: Optional[str] = None
    last_sync_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TwinEntityListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=200)
    entity_code: Optional[str] = None
    entity_name: Optional[str] = None
    entity_type: Optional[str] = None
    current_status: Optional[str] = None
    parent_code: Optional[str] = None
    is_active: Optional[bool] = None


class EntityStatusUpdate(BaseModel):
    status: str = Field(..., max_length=20, description="新状态")
    reason: Optional[str] = Field(None, description="变更原因")


class EntityPropertiesUpdate(BaseModel):
    properties: Dict[str, Any] = Field(..., description="属性键值对（会合并到现有属性）")


# ==================== 孪生场景 ====================

class TwinSceneBase(BaseModel):
    scene_code: str = Field(..., min_length=1, max_length=100, description="场景编码")
    scene_name: str = Field(..., min_length=1, max_length=255, description="场景名称")
    scene_type: str = Field(default="custom", max_length=50, description="场景类型")
    scene_config: Optional[Dict[str, Any]] = Field(None, description="场景配置")
    entity_ids: Optional[List[int]] = Field(None, description="包含的实体 ID 列表")
    thumbnail: Optional[str] = Field(None, max_length=500, description="缩略图路径")
    description: Optional[str] = Field(None, description="描述")
    is_active: bool = Field(default=True, description="是否启用")


class TwinSceneCreate(TwinSceneBase):
    pass


class TwinSceneUpdate(BaseModel):
    scene_name: Optional[str] = Field(None, max_length=255)
    scene_type: Optional[str] = Field(None, max_length=50)
    scene_config: Optional[Dict[str, Any]] = None
    entity_ids: Optional[List[int]] = None
    thumbnail: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TwinSceneResponse(TwinSceneBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TwinSceneListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=200)
    scene_code: Optional[str] = None
    scene_name: Optional[str] = None
    scene_type: Optional[str] = None


class SceneEntitiesUpdate(BaseModel):
    entity_ids: List[int] = Field(..., description="实体 ID 列表（覆盖原列表）")


# ==================== 孪生数据采点 ====================

class TwinDataPointBase(BaseModel):
    entity_code: str = Field(..., max_length=100, description="关联实体编码")
    metric_code: str = Field(..., max_length=100, description="指标编码")
    metric_name: str = Field(..., max_length=255, description="指标名称")
    metric_type: str = Field(..., max_length=50, description="指标类型")
    value: float = Field(..., description="数值")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quality: str = Field(default="good", max_length=20, description="数据质量")
    source: str = Field(default="manual", max_length=20, description="数据来源")
    collected_at: datetime = Field(..., description="采集时间")


class TwinDataPointCreate(TwinDataPointBase):
    pass


class TwinDataPointBatchIngest(BaseModel):
    """批量数据写入"""
    points: List[TwinDataPointCreate] = Field(..., min_length=1, max_length=1000, description="数据点列表")


class TwinDataPointResponse(TwinDataPointBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TwinDataHistoryQuery(BaseModel):
    entity_code: str = Field(..., description="实体编码")
    metric_code: Optional[str] = Field(None, description="指标编码（不传则返回全部指标）")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    limit: int = Field(default=500, ge=1, le=5000, description="返回点数上限")


# ==================== 孪生事件 ====================

class TwinEventBase(BaseModel):
    event_code: str = Field(..., min_length=1, max_length=100, description="事件编码")
    entity_code: str = Field(..., max_length=100, description="关联实体编码")
    entity_name: Optional[str] = Field(None, max_length=255, description="实体名称")
    event_type: str = Field(..., max_length=30, description="事件类型")
    event_level: str = Field(default="info", max_length=20, description="事件级别")
    from_status: Optional[str] = Field(None, max_length=20, description="变更前状态")
    to_status: Optional[str] = Field(None, max_length=20, description="变更后状态")
    title: Optional[str] = Field(None, max_length=255, description="事件标题")
    description: Optional[str] = Field(None, description="事件描述")
    payload: Optional[Dict[str, Any]] = Field(None, description="事件附加数据")


class TwinEventCreate(TwinEventBase):
    pass


class TwinEventResponse(TwinEventBase):
    id: int
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolve_remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TwinEventListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=200)
    event_code: Optional[str] = None
    entity_code: Optional[str] = None
    event_type: Optional[str] = None
    event_level: Optional[str] = None
    is_resolved: Optional[bool] = None


class TwinEventResolve(BaseModel):
    resolved_by: Optional[str] = Field(None, max_length=100, description="处理人")
    resolve_remark: Optional[str] = Field(None, description="处理备注")


# ==================== 孪生仿真 ====================

class TwinSimulationBase(BaseModel):
    sim_code: str = Field(..., min_length=1, max_length=100, description="仿真编码")
    sim_name: str = Field(..., min_length=1, max_length=255, description="仿真名称")
    sim_type: str = Field(..., max_length=30, description="仿真类型：state_prediction/failure_forecast/optimization")
    entity_scope: Optional[Dict[str, Any]] = Field(None, description="仿真范围")
    input_params: Optional[Dict[str, Any]] = Field(None, description="输入参数")
    created_by: Optional[str] = Field(None, max_length=100, description="创建人")


class TwinSimulationCreate(TwinSimulationBase):
    pass


class TwinSimulationResponse(TwinSimulationBase):
    id: int
    output_result: Optional[Dict[str, Any]] = None
    status: str = "pending"
    progress: float = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TwinSimulationListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=200)
    sim_code: Optional[str] = None
    sim_name: Optional[str] = None
    sim_type: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None


# ==================== 通用 ====================

class ListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]
