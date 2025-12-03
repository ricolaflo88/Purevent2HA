#!/usr/bin/env python3
"""
Purevent2HA Daemon
Main daemon managing EnOcean communication and Home Assistant integration
"""

import logging
import os
import json
import time
import asyncio
from pathlib import Path
from aiohttp import web
from datetime import datetime
from typing import Dict, List

from enocean_comm import EnOceanCommunicator, PureventDevice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get configuration from environment
PUREVENT_PORT = os.getenv('PUREVENT_PORT', '/dev/ttyUSB0')
PUREVENT_BAUDRATE = int(os.getenv('PUREVENT_BAUDRATE', '57600'))
PUREVENT_TIMEOUT = int(os.getenv('PUREVENT_TIMEOUT', '30'))
PUREVENT_MAX_RETRY = int(os.getenv('PUREVENT_MAX_RETRY', '3'))
PUREVENT_LOG_LEVEL = os.getenv('PUREVENT_LOG_LEVEL', 'info')

# Data storage
DATA_DIR = Path('/data/purevent2ha')
DEVICES_FILE = DATA_DIR / 'devices.json'
HISTORY_FILE = DATA_DIR / 'history.json'

# Create data directory
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Purevent2HADaemon:
    """Daemon principal Purevent2HA"""
    
    def __init__(self):
        self.communicator = EnOceanCommunicator(
            port=PUREVENT_PORT,
            baudrate=PUREVENT_BAUDRATE,
            timeout=PUREVENT_TIMEOUT,
            max_retry=PUREVENT_MAX_RETRY,
            log_level=PUREVENT_LOG_LEVEL
        )
        
        # Add callback for received messages
        self.communicator.add_callback(self.on_message_received)
        
        self.app = web.Application()
        self.setup_routes()
        
        self.devices_data = {}
        self.history = []
        self.running = False
        
        logger.info("Purevent2HA Daemon initialized")
        
    def setup_routes(self):
        """Configure les routes HTTP"""
        self.app.router.add_get('/health', self.health)
        self.app.router.add_get('/api/devices', self.get_devices)
        self.app.router.add_get('/api/devices/{device_id}', self.get_device)
        self.app.router.add_post('/api/commands', self.send_command)
        self.app.router.add_get('/api/history', self.get_history)
        self.app.router.add_post('/api/config/devices', self.register_device)
        
        logger.info("HTTP routes configured")
        
    async def health(self, request):
        """Endpoint de santé"""
        return web.json_response({
            'status': 'healthy',
            'running': self.running,
            'connected': self.communicator.communicator is not None,
            'timestamp': datetime.now().isoformat()
        })
        
    async def get_devices(self, request):
        """Récupérer tous les appareils"""
        devices = self.communicator.get_all_devices()
        return web.json_response({'devices': devices})
        
    async def get_device(self, request):
        """Récupérer un appareil spécifique"""
        device_id = request.match_info.get('device_id')
        device = self.communicator.get_device(device_id)
        
        if device:
            return web.json_response(device.to_dict())
        else:
            return web.json_response({'error': 'Device not found'}, status=404)
            
    async def send_command(self, request):
        """Envoyer une commande"""
        try:
            data = await request.json()
            device_id = data.get('device_id')
            command = data.get('command')
            
            if not device_id or not command:
                return web.json_response(
                    {'error': 'Missing device_id or command'},
                    status=400
                )
                
            success = self.communicator.send_command(device_id, command)
            
            return web.json_response({
                'success': success,
                'device_id': device_id,
                'command': command
            })
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return web.json_response({'error': str(e)}, status=500)
            
    async def get_history(self, request):
        """Récupérer l'historique"""
        limit = int(request.query.get('limit', 100))
        return web.json_response({
            'history': self.history[-limit:],
            'total': len(self.history)
        })
        
    async def register_device(self, request):
        """Enregistrer un appareil"""
        try:
            data = await request.json()
            device_id = data.get('device_id')
            device_type = data.get('device_type')
            
            if not device_id or not device_type:
                return web.json_response(
                    {'error': 'Missing device_id or device_type'},
                    status=400
                )
                
            self.communicator.register_device(device_id, device_type)
            self.save_devices()
            
            return web.json_response({
                'success': True,
                'device_id': device_id,
                'device_type': device_type
            })
            
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            return web.json_response({'error': str(e)}, status=500)
            
    def on_message_received(self, event_data: Dict):
        """Callback pour les messages reçus"""
        try:
            logger.info(f"Message received from {event_data['sender_id']}: {event_data['data']}")
            
            # Store in devices data
            sender_id = event_data['sender_id']
            if sender_id not in self.devices_data:
                self.devices_data[sender_id] = {
                    'sender_id': sender_id,
                    'messages': []
                }
                
            message = {
                'timestamp': event_data['timestamp'],
                'rorg': event_data['rorg'],
                'data': event_data['data']
            }
            
            self.devices_data[sender_id]['messages'].append(message)
            self.devices_data[sender_id]['last_update'] = datetime.now().isoformat()
            
            # Add to history
            self.history.append({
                'timestamp': event_data['timestamp'],
                'sender_id': sender_id,
                'rorg': event_data['rorg'],
                'data': event_data['data']
            })
            
            # Keep only last 10000 entries
            if len(self.history) > 10000:
                self.history = self.history[-10000:]
                
            # Save periodically
            if len(self.history) % 100 == 0:
                self.save_data()
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            
    def save_data(self):
        """Sauvegarder les données"""
        try:
            # Save devices
            with open(DEVICES_FILE, 'w') as f:
                json.dump(self.devices_data, f, indent=2)
                
            # Save history
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.history[-1000:], f, indent=2)
                
            logger.debug("Data saved")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            
    def save_devices(self):
        """Sauvegarder la config des appareils"""
        try:
            devices_config = {
                device_id: {
                    'device_type': device.device_type,
                    'name': device.DEVICE_TYPES.get(device.device_type, {}).get('name', 'Unknown')
                }
                for device_id, device in self.communicator.devices.items()
            }
            
            config_file = DATA_DIR / 'devices_config.json'
            with open(config_file, 'w') as f:
                json.dump(devices_config, f, indent=2)
                
            logger.info("Devices configuration saved")
        except Exception as e:
            logger.error(f"Error saving devices config: {e}")
            
    def load_config(self):
        """Charger la configuration"""
        try:
            config_file = DATA_DIR / 'devices_config.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    for device_id, device_info in config.items():
                        self.communicator.register_device(
                            device_id,
                            device_info.get('device_type', 'unknown')
                        )
                logger.info("Configuration loaded")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            
    async def start(self):
        """Démarrer le daemon"""
        try:
            # Load configuration
            self.load_config()
            
            # Start EnOcean communicator
            if not self.communicator.start():
                logger.error("Failed to start EnOcean communicator")
                return False
                
            self.running = True
            logger.info("Purevent2HA Daemon started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting daemon: {e}")
            return False
            
    async def stop(self):
        """Arrêter le daemon"""
        self.running = False
        self.communicator.disconnect()
        self.save_data()
        logger.info("Purevent2HA Daemon stopped")
        
    async def run(self):
        """Lancer le daemon"""
        if await self.start():
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 5000)
            await site.start()
            logger.info("HTTP server started on port 5000")
            
            try:
                # Keep running
                while self.running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Interrupted")
            finally:
                await self.stop()
                await runner.cleanup()


async def main():
    """Main entry point"""
    daemon = Purevent2HADaemon()
    await daemon.run()


if __name__ == '__main__':
    asyncio.run(main())
