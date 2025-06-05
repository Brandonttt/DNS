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

def resolver_dns(dominio):
    print(f"\n[Cliente] Resolviendo: {dominio}\n")
    # 1. Preguntar al servidor raíz
    respuesta = consulta_dns(("127.0.0.1", 5300), dominio)
    if respuesta is None or not respuesta.startswith("NS "):
        print("Fallo al contactar servidor raíz.")
        return
    tld_ip = respuesta.split()[1]
    print(f"Respuesta raíz: {respuesta}")

    # 2. Preguntar al TLD
    respuesta = consulta_dns((tld_ip, 5301), dominio)
    if respuesta is None or not respuesta.startswith("NS "):
        print("Fallo al contactar servidor TLD.")
        return
    auth_ip = respuesta.split()[1]
    print(f"Respuesta TLD: {respuesta}")

    # 3. Preguntar al autoritativo
    intentos = 0
    while intentos < 5:
        respuesta = consulta_dns((auth_ip, 5302), dominio)
        if respuesta is None:
            print("Fallo al contactar servidor autoritativo.")
            return
        lineas = respuesta.strip().split("\n")
        for linea in lineas:
            if linea.startswith("A "):
                print(f"Respuesta autoritativo: {linea}")
                print(f"La IP de {dominio} es {linea.split()[1]}")
                return
            elif linea.startswith("CNAME "):
                nuevo_nombre = linea.split()[1]
                print(f"Respuesta autoritativo: {linea} (siguiendo alias...)")
                dominio = nuevo_nombre  # Cambia el dominio al alias y vuelve a preguntar
                intentos += 1
                break
        else:
            print(f"Respuesta autoritativo: {respuesta}")
            print("No se encontró un registro A.")
            return

if __name__ == "__main__":
    dominio = input("Dominio a resolver (ej: www.ipn.mx): ").strip()
    resolver_dns(dominio)