import socket

def consulta_dns(servidor, pregunta):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.sendto(pregunta.encode(), servidor)
    try:
        data, _ = sock.recvfrom(1024)
        return data.decode()
    except socket.timeout:
        return None

def main():
    dominio = input("Dominio a resolver (ej: www.ipn.mx): ").strip()
    # 1. Preguntar al servidor raíz
    respuesta = consulta_dns(("127.0.0.1", 5300), dominio)
    if respuesta is None or not respuesta.startswith("NS "):
        print("Fallo al contactar servidor raíz.")
        return
    print(f"Respuesta raíz: {respuesta}")

    # 2. Preguntar a TLD (.mx)
    tld_ip = respuesta.split()[1]
    respuesta = consulta_dns((tld_ip, 5301), dominio)
    if respuesta is None or not respuesta.startswith("NS "):
        print("Fallo al contactar servidor TLD.")
        return
    print(f"Respuesta TLD: {respuesta}")

    # 3. Preguntar al autoritativo
    auth_ip = respuesta.split()[1]
    respuesta = consulta_dns((auth_ip, 5302), dominio)
    if respuesta is None or not respuesta.startswith("A "):
        print("Fallo al contactar servidor autoritativo.")
        return
    print(f"Respuesta autoritativo: {respuesta}")
    print(f"La IP de {dominio} es {respuesta.split()[1]}")

if __name__ == "__main__":
    main()