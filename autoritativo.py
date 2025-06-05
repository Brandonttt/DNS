import socket

# Archivo de zona simulado de ipn.mx (más ejemplos)
REGISTROS = {
    "www.ipn.mx": {"A": "148.204.103.43"},
    "correo.ipn.mx": {
        "A": "148.204.103.44",
        "MX": "10 correo.ipn.mx"
    },
    "portal.ipn.mx": {"CNAME": "www.ipn.mx"},
    "biblioteca.ipn.mx": {"A": "148.204.103.99"},
    "virtual.ipn.mx": {"CNAME": "www.ipn.mx"},
    "ftp.ipn.mx": {"A": "148.204.103.50"},
    "redes.ipn.mx": {"CNAME": "www.ipn.mx"},
    "ipn.mx": {
        "NS": [
            ("dns1.ipn.mx", "148.204.103.2"),
            ("dns2.ipn.mx", "148.204.198.2"),
            ("dns3.ipn.mx", "148.204.235.2")
        ],
        "A": "148.204.103.1"
    },
    "dns1.ipn.mx": {"A": "148.204.103.2"},
    "dns2.ipn.mx": {"A": "148.204.198.2"},
    "dns3.ipn.mx": {"A": "148.204.235.2"},
}

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.3", 5302))
    print("Servidor autoritativo ipn.mx escuchando en 127.0.0.3:5302")
    while True:
        data, addr = sock.recvfrom(1024)
        dominio = data.decode().strip()
        print(f"Consulta recibida: {dominio}")

        respuesta = []
        registros = REGISTROS.get(dominio)

        if registros:
            # Si hay un registro A
            if "A" in registros:
                respuesta.append(f"A {registros['A']}")
            # Si hay un registro CNAME
            if "CNAME" in registros:
                respuesta.append(f"CNAME {registros['CNAME']}")
            # Si hay un registro NS
            if "NS" in registros:
                for ns, ip in registros["NS"]:
                    respuesta.append(f"NS {ns} {ip}")
            # Si hay un registro MX
            if "MX" in registros:
                respuesta.append(f"MX {registros['MX']}")
        else:
            respuesta.append("NXDOMAIN")

        sock.sendto('\n'.join(respuesta).encode(), addr)

if __name__ == "__main__":
    main()