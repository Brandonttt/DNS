#!/usr/bin/env python3
import socket
from dnslib import DNSRecord, QTYPE, RR, A, RCODE
import threading

# Configuración
LISTEN_IP = "127.0.0.4"
LISTEN_PORT = 5304  # Cambia a 53 si quieres usar el puerto estándar (y recuerda usar sudo)

# Aquí podrías implementar cache, forwarding o lógica más compleja

def handle_dns_query(data, addr, sock):
    try:
        request = DNSRecord.parse(data)
        qname = str(request.q.qname)
        qtype = QTYPE[request.q.qtype]
        print(f"Consulta recibida: {qname} tipo {qtype} desde {addr}")

        # Ejemplo: responde a cualquier consulta con la IP 1.2.3.4
        # Aquí deberías poner la lógica para consultar tus servidores raíz/TLD/autoritativo, etc.
        reply = request.reply()
        if qtype == "A":
            reply.add_answer(RR(qname, QTYPE.A, rdata=A("1.2.3.4"), ttl=60))
            reply.header.rcode = RCODE.NOERROR
        else:
            reply.header.rcode = RCODE.NXDOMAIN

        sock.sendto(reply.pack(), addr)
        print(f"Respuesta enviada a {addr}")

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