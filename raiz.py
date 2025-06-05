import socket

# Simula el archivo root-server-TLDs.txt
TLD_SERVIDORES = {
    ".mx": "127.0.0.2"
}

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Usando la IP real del root server a.root-servers.net (198.41.0.4)
    sock.bind(("198.41.0.4", 5300))
    print("Servidor raíz (a.root-servers.net) escuchando en 198.41.0.4:5300")
    while True:
        data, addr = sock.recvfrom(1024)
        dominio = data.decode()
        if dominio.endswith(".mx"):
            tld_ip = TLD_SERVIDORES[".mx"]
            respuesta = f"NS {tld_ip}"
            sock.sendto(respuesta.encode(), addr)
        else:
            sock.sendto(b"NXDOMAIN", addr)

if __name__ == "__main__":
    main()