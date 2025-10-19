import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderNotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time order notifications
    Each user connects to their own group to receive updates
    """
    
    async def connect(self):
        # Get user from scope (set by AuthMiddlewareStack)
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            # Reject connection if user not authenticated
            await self.close()
            return
        
        # Create a unique group for this user
        self.group_name = f'user_{self.user.id}'
        
        # Join the user's group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to order notifications'
        }))
    
    async def disconnect(self, close_code):
        # Leave group when disconnected
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def order_update(self, event):
        """
        Receive order update from channel layer and send to WebSocket
        This method is called when group_send is triggered
        """
        # Send message to WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'order_id': event['order_id'],
            'status': event['status'],
            'message': event['message']
        }))