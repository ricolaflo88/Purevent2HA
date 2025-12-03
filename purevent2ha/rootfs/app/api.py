"""
Purevent2HA API Server
Provides HTTP API for Purevent2HA addon integration
"""

import logging
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class PureventAPI:
    """API Server for Purevent2HA"""
    
    def __init__(self, communicator):
        """Initialize API"""
        self.communicator = communicator
        self.data_dir = Path('/data/purevent2ha')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def get_status(self) -> dict:
        """Get current status"""
        return {
            'running': self.communicator.running,
            'connected': self.communicator.communicator is not None,
            'devices': self.communicator.get_all_devices(),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_device_data(self, device_id: str) -> dict:
        """Get device data"""
        device = self.communicator.get_device(device_id)
        if device:
            return device.to_dict()
        return {}
    
    def send_command(self, device_id: str, command: str, params: dict = None) -> bool:
        """Send command to device"""
        return self.communicator.send_command(device_id, {'command': command, 'params': params})
    
    def get_history(self, limit: int = 100) -> list:
        """Get history"""
        history_file = self.data_dir / 'history.json'
        if history_file.exists():
            with open(history_file, 'r') as f:
                data = json.load(f)
                return data[-limit:]
        return []
    
    def get_config(self) -> dict:
        """Get current configuration"""
        config_file = self.data_dir / 'devices_config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def set_device_config(self, device_id: str, config: dict) -> bool:
        """Set device configuration"""
        try:
            current = self.get_config()
            current[device_id] = config
            
            config_file = self.data_dir / 'devices_config.json'
            with open(config_file, 'w') as f:
                json.dump(current, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error setting config: {e}")
            return False


class WebAPI:
    """Web API routes handler"""
    
    @staticmethod
    def register_routes(app, api):
        """Register all API routes"""
        
        async def get_health(request):
            """Health check endpoint"""
            from aiohttp import web
            return web.json_response({'status': 'ok'})
        
        async def get_status(request):
            """Get status endpoint"""
            from aiohttp import web
            return web.json_response(api.get_status())
        
        async def get_devices(request):
            """Get all devices"""
            from aiohttp import web
            status = api.get_status()
            return web.json_response({'devices': status['devices']})
        
        async def get_device(request):
            """Get specific device"""
            from aiohttp import web
            device_id = request.match_info.get('device_id')
            data = api.get_device_data(device_id)
            if data:
                return web.json_response(data)
            return web.json_response({'error': 'Device not found'}, status=404)
        
        async def send_command(request):
            """Send command"""
            from aiohttp import web
            try:
                data = await request.json()
                device_id = data.get('device_id')
                command = data.get('command')
                params = data.get('parameters')
                
                success = api.send_command(device_id, command, params)
                return web.json_response({'success': success})
            except Exception as e:
                return web.json_response({'error': str(e)}, status=400)
        
        async def get_history(request):
            """Get history"""
            from aiohttp import web
            limit = int(request.query.get('limit', 100))
            history = api.get_history(limit)
            return web.json_response({'history': history})
        
        async def get_config(request):
            """Get configuration"""
            from aiohttp import web
            return web.json_response(api.get_config())
        
        # Register routes
        app.router.add_get('/health', get_health)
        app.router.add_get('/api/status', get_status)
        app.router.add_get('/api/devices', get_devices)
        app.router.add_get('/api/devices/{device_id}', get_device)
        app.router.add_post('/api/commands', send_command)
        app.router.add_get('/api/history', get_history)
        app.router.add_get('/api/config', get_config)
