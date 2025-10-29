import { useState, useEffect, useRef } from 'react';

/**
 * WebSocket Hook for Mystery Match Real-Time Chat
 * Usage: const { sendMessage, messages, isOnline, isTyping } = useWebSocket(matchId, userId);
 */
export const useWebSocket = (matchId, userId) => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isOnline, setIsOnline] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Use current origin and convert to WebSocket protocol
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const WS_URL = `${protocol}//${window.location.host}`;

  useEffect(() => {
    if (!matchId || !userId) return;

    const connect = () => {
      try {
        const ws = new WebSocket(`${WS_URL}/api/mystery/ws/chat/${matchId}/${userId}`);
        
        ws.onopen = () => {
          console.log('✅ WebSocket connected');
          setIsConnected(true);
          
          // Send ping every 30 seconds to keep connection alive
          const pingInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: 'ping' }));
            }
          }, 30000);
          
          ws.pingInterval = pingInterval;
        };
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'connected':
              console.log('Connected to match:', data.match_id);
              break;
              
            case 'new_message':
              setMessages(prev => [...prev, {
                user_id: data.user_id,
                content: data.message,
                timestamp: data.timestamp
              }]);
              break;
              
            case 'typing':
              setIsTyping(data.is_typing);
              break;
              
            case 'user_online':
              setIsOnline(true);
              break;
              
            case 'user_offline':
              setIsOnline(false);
              break;
              
            case 'unlock_achieved':
              // Handle unlock notification
              console.log('🎉 Unlock achieved:', data.unlock_level);
              break;
              
            case 'pong':
              // Ping response received
              break;
              
            default:
              console.log('Unknown message type:', data.type);
          }
        };
        
        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
        };
        
        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
          
          if (ws.pingInterval) {
            clearInterval(ws.pingInterval);
          }
          
          // Reconnect after 3 seconds
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('🔄 Reconnecting...');
            connect();
          }, 3000);
        };
        
        wsRef.current = ws;
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
      }
    };

    connect();

    // Cleanup
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [matchId, userId, WS_URL]);

  const sendMessage = (content) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'message',
        content: content,
        timestamp: new Date().toISOString()
      }));
      return true;
    }
    return false;
  };

  const sendTypingIndicator = (isTyping) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'typing',
        is_typing: isTyping
      }));
    }
  };

  const sendReadReceipt = (messageId) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'read_receipt',
        message_id: messageId
      }));
    }
  };

  return {
    sendMessage,
    sendTypingIndicator,
    sendReadReceipt,
    messages,
    isConnected,
    isTyping,
    isOnline
  };
};
