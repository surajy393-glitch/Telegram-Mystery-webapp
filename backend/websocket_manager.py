"""
WebSocket Manager for Real-Time Mystery Match Chat
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manage WebSocket connections for real-time chat"""
    
    def __init__(self):
        # Structure: {match_id: {user_id: websocket}}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        # Track which users are typing
        self.typing_users: Dict[int, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, match_id: int, user_id: int):
        """Connect a user to a match chat"""
        await websocket.accept()
        
        if match_id not in self.active_connections:
            self.active_connections[match_id] = {}
        
        self.active_connections[match_id][user_id] = websocket
        logger.info(f"User {user_id} connected to match {match_id}")
        
        # Notify the other user that this user is online
        await self.broadcast_to_match(match_id, {
            "type": "user_online",
            "user_id": user_id
        }, exclude_user=user_id)
    
    def disconnect(self, match_id: int, user_id: int):
        """Disconnect a user from a match chat"""
        if match_id in self.active_connections:
            if user_id in self.active_connections[match_id]:
                del self.active_connections[match_id][user_id]
                logger.info(f"User {user_id} disconnected from match {match_id}")
                
                # Clean up empty matches
                if not self.active_connections[match_id]:
                    del self.active_connections[match_id]
    
    async def send_personal_message(self, message: dict, match_id: int, user_id: int):
        """Send a message to a specific user"""
        if match_id in self.active_connections:
            if user_id in self.active_connections[match_id]:
                websocket = self.active_connections[match_id][user_id]
                try:
                    await websocket.send_json(message)
                except:
                    # Connection lost, remove it
                    self.disconnect(match_id, user_id)
    
    async def broadcast_to_match(self, match_id: int, message: dict, exclude_user: int = None):
        """Broadcast a message to all users in a match"""
        if match_id not in self.active_connections:
            return
        
        disconnected_users = []
        
        for user_id, websocket in self.active_connections[match_id].items():
            if user_id == exclude_user:
                continue
            
            try:
                await websocket.send_json(message)
            except:
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(match_id, user_id)
    
    async def send_typing_indicator(self, match_id: int, user_id: int, is_typing: bool):
        """Send typing indicator to other user"""
        if match_id not in self.typing_users:
            self.typing_users[match_id] = set()
        
        if is_typing:
            self.typing_users[match_id].add(user_id)
        else:
            self.typing_users[match_id].discard(user_id)
        
        # Broadcast to other users
        await self.broadcast_to_match(match_id, {
            "type": "typing",
            "user_id": user_id,
            "is_typing": is_typing
        }, exclude_user=user_id)
    
    def get_online_users(self, match_id: int) -> List[int]:
        """Get list of online users in a match"""
        if match_id in self.active_connections:
            return list(self.active_connections[match_id].keys())
        return []
    
    def is_user_online(self, match_id: int, user_id: int) -> bool:
        """Check if a user is online in a match"""
        return (match_id in self.active_connections and 
                user_id in self.active_connections[match_id])

# Global connection manager instance
manager = ConnectionManager()


async def handle_websocket_message(websocket: WebSocket, match_id: int, user_id: int, message: dict):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # Respond to ping with pong
        await websocket.send_json({"type": "pong"})
    
    elif message_type == "typing":
        # Handle typing indicator
        is_typing = message.get("is_typing", False)
        await manager.send_typing_indicator(match_id, user_id, is_typing)
    
    elif message_type == "message":
        # New message - broadcast to other user
        await manager.broadcast_to_match(match_id, {
            "type": "new_message",
            "user_id": user_id,
            "message": message.get("content"),
            "timestamp": message.get("timestamp")
        }, exclude_user=user_id)
    
    elif message_type == "read_receipt":
        # Message read receipt
        message_id = message.get("message_id")
        await manager.broadcast_to_match(match_id, {
            "type": "message_read",
            "message_id": message_id,
            "user_id": user_id
        }, exclude_user=user_id)
    
    elif message_type == "unlock_notification":
        # Unlock achieved notification
        await manager.broadcast_to_match(match_id, {
            "type": "unlock_achieved",
            "unlock_level": message.get("unlock_level"),
            "data": message.get("data")
        }, exclude_user=user_id)
