import socket

# Simula el archivo TLD-Server-Registrars (solo ipn.mx)
AUTORITATIVOS = {
    "ipn.mx": "127.0.0.3"
}

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.2", 5301))
    print("Servidor TLD (.mx) escuchando en 127.0.0.2:5301")
    while True:
        data, addr = sock.recvfrom(1024)
        dominio = data.decode()
        if dominio.endswith("ipn.mx"):
            auth_ip = AUTORITATIVOS["ipn.mx"]
            respuesta = f"NS {auth_ip}"
            sock.sendto(respuesta.encode(), addr)
        else:
            sock.sendto(b"NXDOMAIN", addr)

if __name__ == "__main__":
    main()