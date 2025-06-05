import socket

# Simula el archivo root-server-TLDs.txt
TLD_SERVIDORES = {
    ".mx": "127.0.0.2"
}

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 5300))
    print("Servidor raíz escuchando en 127.0.0.1:5300")
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