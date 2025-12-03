"""
EnOcean Communication Manager for Purevent2HA
Handles serial communication with EnOcean devices
"""

import logging
import os
import json
import time
import threading
import queue
from datetime import datetime
from typing import Dict, List, Optional, Callable
from pathlib import Path

try:
    import serial
    from enocean.communicators.serialcommunicator import SerialCommunicator
    from enocean.protocol.packet import RadioPacket
    from enocean.protocol.constants import RORG
except ImportError:
    # Will be installed via requirements.txt
    pass

logger = logging.getLogger(__name__)

class PureventDevice:
    """Représentation d'un appareil Purevent"""
    
    DEVICE_TYPES = {
        'D1079-01-00': {
            'name': 'VMI Purevent',
            'description': 'Ventilation Mécanique par Insufflation Purevent',
            'rorg': 0xD1,
            'func': 0x07,
            'type': 0x09
        },
        'A5-09-04': {
            'name': 'Capteur CO2',
            'description': 'Capteur de dioxyde de carbone',
            'rorg': 0xA5,
            'func': 0x09,
            'type': 0x04
        },
        'A5-04-01': {
            'name': 'Capteur T°/Humidité',
            'description': 'Capteur température et humidité',
            'rorg': 0xA5,
            'func': 0x04,
            'type': 0x01
        },
        'D1079-00-00': {
            'name': 'Assistant Ventilairsec',
            'description': 'Module assistant Ventilairsec',
            'rorg': 0xD1,
            'func': 0x07,
            'type': 0x08
        }
    }
    
    def __init__(self, device_id: str, device_type: str):
        self.device_id = device_id
        self.device_type = device_type
        self.data = {}
        self.last_update = None
        self.enabled = True
        
    def to_dict(self) -> Dict:
        return {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'name': self.DEVICE_TYPES.get(self.device_type, {}).get('name', 'Unknown'),
            'data': self.data,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }


class EnOceanCommunicator:
    """Gestionnaire de communication EnOcean"""
    
    def __init__(self, port: str = '/dev/ttyUSB0', 
                 baudrate: int = 57600,
                 timeout: int = 30,
                 max_retry: int = 3,
                 log_level: str = 'info'):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.max_retry = max_retry
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self.communicator = None
        self.devices: Dict[str, PureventDevice] = {}
        self.running = False
        self.receive_thread = None
        self.callbacks: List[Callable] = []
        self.message_queue = queue.Queue()
        
        logger.info(f"EnOceanCommunicator initialized with port {port}")
        
    def add_callback(self, callback: Callable):
        """Ajouter une callback pour les messages reçus"""
        self.callbacks.append(callback)
        
    def connect(self) -> bool:
        """Établir la connexion avec le module EnOcean"""
        try:
            self.communicator = SerialCommunicator(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            logger.info(f"Connected to EnOcean on {self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to EnOcean: {e}")
            return False
            
    def disconnect(self):
        """Fermer la connexion"""
        self.running = False
        if self.communicator:
            self.communicator.stop()
            logger.info("Disconnected from EnOcean")
            
    def start(self):
        """Démarrer la réception de messages"""
        if not self.connect():
            return False
            
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        logger.info("EnOcean receiver started")
        return True
        
    def _receive_loop(self):
        """Boucle de réception des messages"""
        retry_count = 0
        
        while self.running:
            try:
                if self.communicator.is_alive():
                    packet = self.communicator.receive.get(timeout=1.0)
                    if packet:
                        self._handle_packet(packet)
                        retry_count = 0
                else:
                    if retry_count < self.max_retry:
                        logger.warning(f"Communicator dead, reconnecting... ({retry_count + 1}/{self.max_retry})")
                        retry_count += 1
                        time.sleep(2)
                        self.connect()
                    else:
                        logger.error("Max retries reached, stopping receiver")
                        self.running = False
                        break
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in receive loop: {e}")
                time.sleep(1)
                
    def _handle_packet(self, packet):
        """Traiter un paquet reçu"""
        try:
            logger.debug(f"Packet received: {packet}")
            
            # Extract sender ID
            sender_id = hex(packet.sender)[2:].upper().zfill(8)
            
            # Parse data based on RORG
            device_data = self._parse_packet(packet)
            
            if device_data:
                # Broadcast to callbacks
                event_data = {
                    'sender_id': sender_id,
                    'rorg': hex(packet.rorg)[2:].upper().zfill(2),
                    'data': device_data,
                    'timestamp': datetime.now().isoformat()
                }
                
                for callback in self.callbacks:
                    try:
                        callback(event_data)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
                        
        except Exception as e:
            logger.error(f"Error handling packet: {e}")
            
    def _parse_packet(self, packet) -> Optional[Dict]:
        """Parser un paquet selon son type"""
        try:
            if packet.rorg == RORG.BS4:
                # 4-byte telegrams - VMI Purevent
                return self._parse_bs4(packet)
            elif packet.rorg == RORG.VLD:
                # Variable length data - potential support
                return self._parse_vld(packet)
            elif packet.rorg == RORG.RPS:
                # Rocker switch profiles
                return self._parse_rps(packet)
            else:
                logger.debug(f"Unknown RORG: {hex(packet.rorg)}")
                return None
        except Exception as e:
            logger.error(f"Error parsing packet: {e}")
            return None
            
    def _parse_bs4(self, packet) -> Optional[Dict]:
        """Parser un télégram BS4 (4 bytes)"""
        data = {}
        try:
            # BS4 format for A5-09-04 (CO2)
            if len(packet.data) >= 4:
                # DB_0: Status
                db_0 = packet.data[0]
                # DB_1 & DB_2: CO2 concentration
                db_1 = packet.data[1]
                db_2 = packet.data[2]
                # DB_3: Linear/Non-linear, Temp sensor
                db_3 = packet.data[3]
                
                # Extract CO2 value (typically 0-2500 ppm)
                co2_value = ((db_1 & 0xFF) << 8) | (db_2 & 0xFF)
                co2_ppm = (co2_value / 2047.0) * 2500
                
                data['co2_ppm'] = round(co2_ppm, 1)
                data['raw_value'] = co2_value
                
            return data if data else None
        except Exception as e:
            logger.error(f"Error parsing BS4: {e}")
            return None
            
    def _parse_vld(self, packet) -> Optional[Dict]:
        """Parser un télégram VLD (longueur variable)"""
        data = {}
        try:
            # VLD format for D1079 devices
            if len(packet.data) >= 1:
                command = packet.data[0]
                data['command'] = hex(command)
                
                if len(packet.data) > 1:
                    data['payload'] = [hex(b) for b in packet.data[1:]]
                    
            return data if data else None
        except Exception as e:
            logger.error(f"Error parsing VLD: {e}")
            return None
            
    def _parse_rps(self, packet) -> Optional[Dict]:
        """Parser un RPS (Rocker switch telegram)"""
        data = {}
        try:
            if len(packet.data) >= 1:
                # RPS format for rocker switches
                status = packet.data[0]
                data['button_state'] = hex(status)
                
            return data if data else None
        except Exception as e:
            logger.error(f"Error parsing RPS: {e}")
            return None
            
    def send_command(self, device_id: str, command: Dict) -> bool:
        """Envoyer une commande à un appareil"""
        try:
            if not self.communicator or not self.communicator.is_alive():
                logger.error("Communicator not connected")
                return False
                
            # Build VLD packet for sending
            # This would need device-specific implementation
            logger.info(f"Sending command to {device_id}: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False
            
    def register_device(self, device_id: str, device_type: str):
        """Enregistrer un appareil"""
        device = PureventDevice(device_id, device_type)
        self.devices[device_id] = device
        logger.info(f"Device registered: {device_id} ({device_type})")
        
    def get_device(self, device_id: str) -> Optional[PureventDevice]:
        """Récupérer les infos d'un appareil"""
        return self.devices.get(device_id)
        
    def get_all_devices(self) -> List[Dict]:
        """Récupérer tous les appareils"""
        return [device.to_dict() for device in self.devices.values()]
