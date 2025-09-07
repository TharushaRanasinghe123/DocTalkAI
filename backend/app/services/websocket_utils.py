# app/services/websocket_utils.py


async def safe_send_json(client_ws, data):
    """Safely send JSON data to client with connection checking"""
    try:
        if client_ws.client_state.name == 'CONNECTED':
            await client_ws.send_json(data)
            return True
        else:
            print(f"⚠️ Cannot send data - WebSocket state: {client_ws.client_state.name}")
            return False
    except Exception as e:
        print(f"Error sending JSON: {e}")
        return False