import os
import socket
import hashlib
import json

from logger import create_logger

class PavRCON:
    def __init__(self):
        self.SERVER_IP = os.environ.get("SERVER_IP")
        self.RCON_PORT = int("9100")
        self.RCON_PASSWORD = os.environ.get("RCON_PASSWORD")
        self.logger = create_logger(__name__)

    def _md5_hash(self, password):
        """Compute MD5 hash form Pavlov Password"""
        
        return hashlib.md5(password.encode('utf-8')).hexdigest()

    def _authenticate_rcon(self) -> socket.socket:
        """Connect and do non rcon-standard password operations..."""
       
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.SERVER_IP, self.RCON_PORT))
            
            # Wait for "Password: " prompt
            server_prompt = sock.recv(1024).decode('utf-8')
            if 'Password: ' not in server_prompt:
                print("Did not receive password prompt from server")
                return None
            
            # Send the MD5 hash of the RCON password
            password_md5 = self._md5_hash(self.RCON_PASSWORD)
            sock.sendall(password_md5.encode('utf-8'))
            
            # Receive authentication response
            auth_response = sock.recv(1024).decode('utf-8')
            if 'Authenticated=1' in auth_response:
                print("Successfully authenticated!")
                return sock
            else:
                print("Authentication failed!")
                sock.close()
                return None
        except Exception as e:
            print(f"Failed to connect or authenticate: {e}")
            return None

    def _send_rcon_command(self, sock, command):
        """Send RCON command using socket opened from authenticat_rcon"""
        
        try:
            # Send the command with a newline
            sock.sendall(f"{command}\n".encode('utf-8'))
            
            # Receive the JSON response (until carriage return and newline)
            response = ""
            while True:
                data = sock.recv(1024).decode('utf-8')
                response += data
                if "\r\n" in data:
                    break
            
            # Parse and return the JSON response
            json_response = json.loads(response.strip())
            return json_response
        except Exception as e:
            print(f"Error sending command: {e}")
            return None
        
    def set_profile(self, map_id: str, gamemode_id: str, mods: list) -> bool:
        """Used to get Game.ini ready for the profile of the next map"""

        rcon_socket = self._authenticate_rcon()
        rotate_target = {"MapId": map_id, "GameMode": gamemode_id}
        
        if rcon_socket:
            clear_mods_response = self._send_rcon_command(rcon_socket, "UGCClearModList")
            if bool(clear_mods_response['Successful']):
                self.logger.info("Cleared mods from Game.ini")
            else:
                self.logger.fatal("Error occured while clearing mods")

            for mod in mods:
                response = self._send_rcon_command(rcon_socket, f"UGCAddMod {mod}")
                self.logger.info(response)
                if bool(response['Successful']):
                    self.logger.info(f"Added modID {mod} to Game.ini")
                else:
                    self.logger.fatal("Error adding modID")

            new_rotation_response = self._send_rcon_command(rcon_socket, f"AddMapRotation {map_id} {gamemode_id}")
            if bool(new_rotation_response['Successful']):
                self.logger.info(f"Added new rotation of {map_id} with gamemode {gamemode_id}")
            else:
                self.logger.fatal("Error occured while adding new rotation")

            server_info = self._send_rcon_command(rcon_socket, "MapList")
            if bool(server_info['Successful']):
                mapList = server_info.get("MapList")
                self.logger.info(f"Current Rotation: {mapList}")

                for entry in mapList:
                    if entry == rotate_target:
                        continue

                    response = self._send_rcon_command(rcon_socket, f"RemoveMapRotation {entry['MapId']} {entry['GameMode']}")
                    if bool(response['Successful']):
                        self.logger.info(f"Removed {entry} from rotation")
                    else:
                        self.logger.fatal("Error occured while removing an entry from rotation")
            else:
                self.logger.fatal("Error occured while getting server info")
                    
            rcon_socket.close()

            self.rotate_map()

            return True
        
        else:
            return False

    def rotate_map(self):
        """Rotates to the next map, usually used following set_profile"""

        rcon_socket = self._authenticate_rcon()
    
        if rcon_socket:
            server_info = self._send_rcon_command(rcon_socket, "RotateMap")
            if bool(server_info['Successful']):
                self.logger.info("Successfully rotated map")
            else:
                self.logger.fatal("Error occured while rotating map")
            
            rcon_socket.close()

_pavrcon = PavRCON()

def set_profile(map_id: str, gamemode_id: str, mods: list) -> bool:
    return _pavrcon.set_profile(map_id, gamemode_id, mods)

def rotate_map():
    return _pavrcon.rotate_map()

if __name__ == "__main__":
    #set_profile(map_id="datacenter", gamemode_id="TTT", mods=["UGC3945345"])
    pass