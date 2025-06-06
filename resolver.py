#!/usr/bin/env python3
import socket
from dnslib import DNSRecord, QTYPE, RR, A, RCODE
import threading

# Configuración de puertos/IP internos de tus servidores
ROOT_IP = "198.41.0.4"
ROOT_PORT = 5300
TLD_IP = "127.0.0.2"
TLD_PORT = 5301
AUTH_IP = "127.0.0.3"
AUTH_PORT = 5302

LISTEN_IP = "127.0.0.4"
LISTEN_PORT = 5304  # Cambia a 53 para producción real (requiere sudo)

TIMEOUT = 2  # segundos para timeouts de sockets internos

def consulta_servidor(ip, puerto, mensaje):
    """Envía mensaje a un servidor DNS interno y espera respuesta como texto."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(TIMEOUT)
        s.sendto(mensaje.encode(), (ip, puerto))
        try:
            data, _ = s.recvfrom(1024)
            return data.decode().strip()
        except socket.timeout:
            return None

def resolver_iterativo(dominio):
    """Consulta a los servidores raíz, TLD y autoritativo para obtener la IP final."""
    # 1. Consulta raíz para TLD
    tld_name = consulta_servidor(ROOT_IP, ROOT_PORT, dominio)
    if not tld_name:
        return None

    # 2. Consulta TLD para autoritativo
    auth_name = consulta_servidor(TLD_IP, TLD_PORT, dominio)
    if not auth_name:
        return None

    # 3. Consulta autoritativo para IP final
    ip_final = consulta_servidor(AUTH_IP, AUTH_PORT, dominio)
    return ip_final

def handle_dns_query(data, addr, sock):
    try:
        request = DNSRecord.parse(data)
        qname = str(request.q.qname).rstrip(".")
        qtype = QTYPE[request.q.qtype]
        print(f"Consulta recibida: {qname} tipo {qtype} desde {addr}")

        reply = request.reply()

        if qtype == "A":
            ip = resolver_iterativo(qname)
            if ip:
                reply.add_answer(RR(qname + ".", QTYPE.A, rdata=A(ip), ttl=60))
                reply.header.rcode = RCODE.NOERROR
                print(f"Respuesta: {ip} para {qname}")
            else:
                reply.header.rcode = RCODE.NXDOMAIN
                print(f"No se encontró IP para {qname}")
        else:
            reply.header.rcode = RCODE.NXDOMAIN
            print(f"No soportado tipo {qtype}")

        sock.sendto(reply.pack(), addr)
    except Exception as e:
        print(f"Error procesando consulta: {e}")

def resolver_loop():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    print(f"Resolver escuchando en {LISTEN_IP}:{LISTEN_PORT} (compatible con dig)")

    while True:
        data, addr = sock.recvfrom(4096)
        threading.Thread(target=handle_dns_query, args=(data, addr, sock), daemon=True).start()

if __name__ == "__main__":
    resolver_loop()