import socket

# Simula el archivo de zona de ipn.mx
REGISTROS = {
    "www.ipn.mx": "148.204.103.43",
    "correo.ipn.mx": "148.204.103.44"
}

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.3", 5302))
    print("Servidor autoritativo ipn.mx escuchando en 127.0.0.3:5302")
    while True:
        data, addr = sock.recvfrom(1024)
        dominio = data.decode()
        ip = REGISTROS.get(dominio)
        if ip:
            respuesta = f"A {ip}"
        else:
            respuesta = "NXDOMAIN"
        sock.sendto(respuesta.encode(), addr)

if __name__ == "__main__":
    main()