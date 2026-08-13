"""
数字孪生 - WebSocket 实时推送路由
需在 start.py:init_app() 手动注册（prefix=/v1/digital-twin）
"""
import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from loguru import logger

try:
    from base.common.security import get_current_user_id_ws
    from base.plugins.digital_twin.services.twin_ws_manager import twin_ws_manager
except ImportError:
    async def get_current_user_id_ws(token): return None
    class twin_ws_manager:
        @staticmethod
        async def connect(u, w): pass
        @staticmethod
        def disconnect(u, w): pass

twin_ws_router = APIRouter(tags=["数字孪生-WebSocket"])


@twin_ws_router.websocket("/ws")
async def twin_ws(websocket: WebSocket, token: Optional[str] = Query(None)):
    """数字孪生实时推送 WebSocket

    连接：ws://host/api/v1/digital-twin/ws?token=<JWT>
    鉴权失败 → 服务端关闭连接（code=4401）

    服务端下发：
      {"type":"connected","message":"数字孪生连接已建立"}
      {"type":"entity.status.changed","data":{...}}    # 实体状态变更
      {"type":"event.created","data":{...}}            # 新事件产生
      {"type":"data.ingested","data":{...}}            # 数据写入
      {"type":"simulation.progress","data":{...}}      # 仿真进度

    客户端可发：
      {"type":"ping"}  # 心跳，服务端回 {"type":"pong"}
      {"type":"subscribe","entity_codes":["E001"]}  # 订阅指定实体（占位，后续支持）
    """
    user_id = await get_current_user_id_ws(token)
    if not user_id:
        await websocket.close(code=4401)
        return

    await twin_ws_manager.connect(user_id, websocket)
    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "数字孪生连接已建立",
        }, ensure_ascii=False))

        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.warning(f"[twin.ws] 异常 user=#{user_id}: {e}")
    finally:
        twin_ws_manager.disconnect(user_id, websocket)
