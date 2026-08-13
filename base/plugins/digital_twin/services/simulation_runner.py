"""
孪生仿真执行器
异步执行仿真任务，按步骤推进进度并通过 WebSocket 推送
采用简化的仿真模型：基于历史数据均值/趋势的预测
"""
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from loguru import logger

try:
    from base.plugins.digital_twin.models.digital_twin import TwinSimulation, TwinDataPoint, TwinEntity
    from base.plugins.digital_twin.services.twin_ws_manager import broadcast_twin_event
except ImportError:
    TwinSimulation = None
    TwinDataPoint = None
    TwinEntity = None
    async def broadcast_twin_event(t, d): pass


# 进程内仿真任务跟踪
_running_tasks: Dict[int, asyncio.Task] = {}


async def schedule_simulation(sim_id: int) -> None:
    """调度仿真任务（取消旧任务，启动新任务）"""
    old = _running_tasks.get(sim_id)
    if old and not old.done():
        old.cancel()
    task = asyncio.create_task(_run_simulation(sim_id))
    _running_tasks[sim_id] = task


async def _run_simulation(sim_id: int) -> None:
    """执行仿真任务主体"""
    if TwinSimulation is None:
        return

    sim = await TwinSimulation.filter(id=sim_id).first()
    if not sim:
        return

    try:
        # 标记为运行中
        sim.status = "running"
        sim.started_at = datetime.now()
        await sim.save()
        await broadcast_twin_event("simulation.progress", {"sim_id": sim_id, "progress": 0, "status": "running"})

        # 获取仿真范围内的实体
        scope = sim.entity_scope or {}
        entity_codes = scope.get("entity_codes", [])
        if not entity_codes:
            # 默认所有启用实体
            entities = await TwinEntity.filter(is_active=True).all()
            entity_codes = [e.entity_code for e in entities]

        total_steps = max(len(entity_codes), 1)
        result_entities: Dict[str, Any] = {}

        for idx, code in enumerate(entity_codes):
            # 每个实体的仿真分析
            entity_result = await _simulate_entity(code, sim.sim_type, sim.input_params or {})
            result_entities[code] = entity_result

            # 更新进度
            progress = (idx + 1) / total_steps * 100
            sim.progress = progress
            await sim.save()
            await broadcast_twin_event("simulation.progress", {
                "sim_id": sim_id, "progress": round(progress, 1), "status": "running",
                "current_entity": code,
            })
            await asyncio.sleep(0.1)  # 让出事件循环

        # 完成仿真
        sim.output_result = {
            "sim_type": sim.sim_type,
            "entity_count": len(entity_codes),
            "entities": result_entities,
            "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        sim.progress = 100
        sim.status = "completed"
        sim.completed_at = datetime.now()
        await sim.save()
        await broadcast_twin_event("simulation.progress", {
            "sim_id": sim_id, "progress": 100, "status": "completed",
        })
        logger.info(f"[twin.sim] 仿真 #{sim_id} 完成")

    except asyncio.CancelledError:
        # 用户取消
        sim = await TwinSimulation.filter(id=sim_id).first()
        if sim:
            sim.status = "failed"
            sim.error_message = "用户手动取消"
            sim.completed_at = datetime.now()
            await sim.save()
        logger.info(f"[twin.sim] 仿真 #{sim_id} 已取消")
        raise
    except Exception as e:
        logger.error(f"[twin.sim] 仿真 #{sim_id} 失败: {e}")
        sim = await TwinSimulation.filter(id=sim_id).first()
        if sim:
            sim.status = "failed"
            sim.error_message = str(e)
            sim.completed_at = datetime.now()
            await sim.save()
    finally:
        _running_tasks.pop(sim_id, None)


async def _simulate_entity(entity_code: str, sim_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """对单个实体执行仿真分析

    简化实现：基于历史数据点的均值/方差生成预测结果
    生产环境可替换为真实的物理模型或机器学习模型
    """
    if TwinDataPoint is None:
        return {"status": "skipped", "reason": "model_unavailable"}

    # 获取最近 100 条数据
    recent = await TwinDataPoint.filter(entity_code=entity_code).order_by("-collected_at").limit(100)
    if not recent:
        return {
            "entity_code": entity_code,
            "status": "no_data",
            "message": "无历史数据，无法仿真",
        }

    # 按指标分组计算统计
    metrics: Dict[str, list] = {}
    for p in recent:
        metrics.setdefault(p.metric_code, []).append(p.value)

    summary: Dict[str, Any] = {}
    for metric, values in metrics.items():
        avg = sum(values) / len(values)
        max_v = max(values)
        min_v = min(values)
        # 简单趋势：对比前一半和后一半的均值
        half = len(values) // 2 or 1
        first_half_avg = sum(values[:half]) / half
        second_half_avg = sum(values[half:]) / (len(values) - half or 1)
        trend = "rising" if second_half_avg > first_half_avg else ("falling" if second_half_avg < first_half_avg else "stable")

        summary[metric] = {
            "avg": round(avg, 4),
            "max": max_v,
            "min": min_v,
            "trend": trend,
            "sample_count": len(values),
        }

    # 根据 sim_type 给出预测结论
    prediction: Dict[str, Any] = {}
    if sim_type == "state_prediction":
        # 状态预测：基于趋势判断未来状态
        concerning = [m for m, s in summary.items() if s["trend"] != "stable"]
        prediction["next_status"] = "warning" if concerning else "normal"
        prediction["confidence"] = 0.7 if concerning else 0.9
        prediction["concerning_metrics"] = concerning
    elif sim_type == "failure_forecast":
        # 故障预测：粗略检查是否接近阈值
        risk_metrics = [m for m, s in summary.items() if s["max"] > s["avg"] * 1.5]
        prediction["failure_risk"] = "high" if risk_metrics else "low"
        prediction["risk_metrics"] = risk_metrics
    elif sim_type == "optimization":
        # 优化建议
        optimization_candidates = [m for m, s in summary.items() if s["trend"] == "rising"]
        prediction["suggestions"] = [f"指标 {m} 呈上升趋势，建议关注" for m in optimization_candidates]
        prediction["optimized_metrics"] = optimization_candidates

    return {
        "entity_code": entity_code,
        "metrics_summary": summary,
        "prediction": prediction,
        "sim_type": sim_type,
    }
