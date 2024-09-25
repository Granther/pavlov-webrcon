import socket
import hashlib
import json

# Configuration (update with your server's IP, port, and password)
SERVER_IP = '192.168.1.173'  # Replace with your server's IP
SERVER_PORT = 9100       # Replace with your RCON port
RCON_PASSWORD = 'glorp123'  # Replace with your RCON password

# compute MD5 hash
def md5_hash(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()

# connect and authenticate to the Pavlov VR server via RCON
def authenticate_rcon(server_ip, server_port, rcon_password):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, server_port))
        
        # Wait for "Password: " prompt
        server_prompt = sock.recv(1024).decode('utf-8')
        if 'Password: ' not in server_prompt:
            print("Did not receive password prompt from server")
            return None
        
        # Send the MD5 hash of the RCON password
        password_md5 = md5_hash(rcon_password)
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

# send RCON commands and receive responses
def send_rcon_command(sock, command):
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
    
def set_profile(map_id, gamemode_id, mods: list) :
    rcon_socket = authenticate_rcon(SERVER_IP, SERVER_PORT, RCON_PASSWORD)
    rotate_target = {"MapId": map_id, "GameMode": gamemode_id}
    
    if rcon_socket:
        clear_mods_response = send_rcon_command(rcon_socket, "UGCClearModList")
        if clear_mods_response:
            print("Cleared mods from Game.ini")

        for mod in mods:
            response = send_rcon_command(rcon_socket, f"UGCAddMod {mod}")
            if response:
                print(f"Added modID {mod} to Game.ini")

        new_rotation_response = send_rcon_command(rcon_socket, f"AddMapRotation {map_id} {gamemode_id}")
        if new_rotation_response:
            print(f"Added new rotation of {map_id} with gamemode {gamemode_id}")

        server_info = send_rcon_command(rcon_socket, "MapList")
        if server_info:
            mapList = server_info.get("MapList")
            print(f"Current Rotation: {mapList}")

            for entry in mapList:
                if entry == rotate_target:
                    continue

                response = send_rcon_command(rcon_socket, f"RemoveMapRotation {entry['MapId']} {entry['GameMode']}")
                if response:
                    print(f"Removed {entry} from rotation")

        rotate_map_response = send_rcon_command(rcon_socket, "RotateMap")
        if rotate_map_response:
            print("Rotating map")
        
        rcon_socket.close()

# Get current maps
# Remove all but one
# Clear mods list
# Add mods list
# Add new map rotation
# Rotate map

# Example usage
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
