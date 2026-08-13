"""
数字孪生 WebSocket 连接管理器
按 user_id 维度管理连接，复用 mail 模块的设计模式
"""
import json
from typing import Dict, Set, Any
from fastapi import WebSocket
from loguru import logger


class TwinConnectionManager:
    """按 user_id 维度管理 WebSocket 连接，支持单用户多连接"""

    def __init__(self):
        self._connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(user_id, set()).add(ws)
        logger.info(f"[twin.ws] 用户 #{user_id} 连接，当前在线 {len(self._connections)} 人")

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        conns = self._connections.get(user_id)
        if conns:
            conns.discard(ws)
            if not conns:
                del self._connections[user_id]
        logger.info(f"[twin.ws] 用户 #{user_id} 断开，当前在线 {len(self._connections)} 人")

    async def push_to_user(self, user_id: int, payload: Dict[str, Any]) -> None:
        """向指定用户的所有连接推送 JSON 消息"""
        conns = self._connections.get(user_id)
        if not conns:
            return
        text = json.dumps(payload, ensure_ascii=False, default=str)
        dead = []
        for ws in conns:
            try:
                await ws.send_text(text)
            except Exception as e:
                logger.warning(f"[twin.ws] 推送失败 user=#{user_id}: {e}")
                dead.append(ws)
        for ws in dead:
            conns.discard(ws)
            if not conns:
                self._connections.pop(user_id, None)

    async def broadcast(self, payload: Dict[str, Any]) -> None:
        """向所有在线用户广播"""
        for user_id in list(self._connections.keys()):
            await self.push_to_user(user_id, payload)

    def online_user_ids(self) -> list:
        return list(self._connections.keys())

    def online_count(self) -> int:
        return len(self._connections)


# 模块级单例
twin_ws_manager = TwinConnectionManager()


async def broadcast_twin_event(event_type: str, data: Dict[str, Any]) -> None:
    """向所有在线用户广播孪生事件"""
    await twin_ws_manager.broadcast({"type": event_type, "data": data})
