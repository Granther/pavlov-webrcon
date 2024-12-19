from pavrcon import PavRCON

if __name__ == "__main__":
    rcon = PavRCON()
    sock = rcon._authenticate_rcon()
    # rcon._send_rcon_command(sock, "ResetSND")