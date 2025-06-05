import socket

# Simula el archivo TLD-Server-Registrars (solo ipn.mx)
AUTORITATIVOS = {
    "ipn.mx": "127.0.0.3"
}

def main():
    hostname_tld = "c.mx-ns.mx"           # Nombre real del TLD server (para simular)
    ip_real = "192.100.224.1"             # IP real (solo referencia)
    ip_local = "127.0.0.2"                # IP local para pruebas
    port = 5301

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip_local, port))
    print(f"Servidor TLD simulado ({hostname_tld}, {ip_real}) escuchando en {ip_local}:{port}")

    while True:
        data, addr = sock.recvfrom(1024)
        dominio = data.decode()
        print(f"Consulta recibida de {addr}: {dominio}")

        if dominio.endswith("ipn.mx"):
            auth_ip = AUTORITATIVOS["ipn.mx"]
            respuesta = f"NS {auth_ip}"
            sock.sendto(respuesta.encode(), addr)
        else:
            sock.sendto(b"NXDOMAIN", addr)

if __name__ == "__main__":
    main()