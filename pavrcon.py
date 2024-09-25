import os
import socket
import hashlib
import json

from logger import create_logger

SERVER_IP = '192.168.1.173'
SERVER_PORT = 9100 
RCON_PASSWORD = 'glorp123' 

class PavRCON:
    def __init__(self):
        self.SERVER_IP = os.environ.get("SERVER_IP")
        self.SERVER_PORT = int(os.environ.get("SERVER_PORT"))
        self.RCON_PASSWORD = os.environ.get("RCON_PASSWORD")
        self.logger = create_logger(__name__)

    def _md5_hash(self, password):
        """Compute MD5 hash form Pavlov Password"""
        return hashlib.md5(password.encode('utf-8')).hexdigest()

    def _authenticate_rcon(self, server_ip, server_port, rcon_password) -> socket.socket:
        """Connect and do non rcon-standard password operations..."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server_ip, server_port))
            
            # Wait for "Password: " prompt
            server_prompt = sock.recv(1024).decode('utf-8')
            if 'Password: ' not in server_prompt:
                print("Did not receive password prompt from server")
                return None
            
            # Send the MD5 hash of the RCON password
            password_md5 = self._md5_hash(rcon_password)
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
        
    def _set_profile(self, map_id: str, gamemode_id: str, mods: list) :
        rcon_socket = self._authenticate_rcon(SERVER_IP, SERVER_PORT, RCON_PASSWORD)
        rotate_target = {"MapId": map_id, "GameMode": gamemode_id}
        
        if rcon_socket:
            clear_mods_response = self._send_rcon_command(rcon_socket, "UGCClearModList")
            if clear_mods_response:
                print("Cleared mods from Game.ini")

            for mod in mods:
                response = self._send_rcon_command(rcon_socket, f"UGCAddMod {mod}")
                if response:
                    print(f"Added modID {mod} to Game.ini")

            new_rotation_response = self._send_rcon_command(rcon_socket, f"AddMapRotation {map_id} {gamemode_id}")
            if new_rotation_response:
                print(f"Added new rotation of {map_id} with gamemode {gamemode_id}")

            server_info = self._send_rcon_command(rcon_socket, "MapList")
            if server_info:
                mapList = server_info.get("MapList")
                print(f"Current Rotation: {mapList}")

                for entry in mapList:
                    if entry == rotate_target:
                        continue

                    response = self._send_rcon_command(rcon_socket, f"RemoveMapRotation {entry['MapId']} {entry['GameMode']}")
                    if response:
                        print(f"Removed {entry} from rotation")

            rotate_map_response = self._send_rcon_command(rcon_socket, "RotateMap")
            if rotate_map_response:
                print("Rotating map")
            
            rcon_socket.close()

if __name__ == "__main__":
    # Authenticate with the RCON server
    # rcon_socket = authenticate_rcon(SERVER_IP, SERVER_PORT, RCON_PASSWORD)
    
    # if rcon_socket:
    #     # Example: Send the 'ServerInfo' command
    #     server_info = send_rcon_command(rcon_socket, "UGCModList")
    #     if server_info:
    #         print("Server Info:", json.dumps(server_info, indent=4))
        
    #     # Close the connection
    #     rcon_socket.close()

    set_profile(map_id="datacenter", gamemode_id="TTT", mods=["UGC3945345"])