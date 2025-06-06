#!/usr/bin/env python3

import socket
import time
import random
import argparse
import sys

def consulta_resolver(dominio, servidor, puerto):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    inicio = time.time()
    query_id = random.randint(10000, 65000)
    mensaje = f"{query_id}|{dominio}"
    sock.sendto(mensaje.encode(), (servidor, puerto))
    try:
        data, _ = sock.recvfrom(4096)
        fin = time.time()
        return data, int((fin - inicio) * 1000), query_id
    except socket.timeout:
        return None, None, query_id

def mostrar_salida_dig(respuesta, tiempo_ms, servidor, msg_size, dominio, query_id):
    now = time.gmtime()
    date_str = time.strftime('%a %b %d %H:%M:%S UTC %Y', now)
    ip = respuesta.decode().strip()
    status = "NOERROR" if ip != "NXDOMAIN" else "NXDOMAIN"
    answer_count = 1 if ip != "NXDOMAIN" else 0

    print(f"; <<>> MiDig 1.0 <<>> {dominio}")
    print(";; global options: +cmd")
    print(";; Got answer:")
    print(f";; ->>HEADER<<- opcode: QUERY, status: {status}, id: {query_id}")
    print(f";; flags: qr rd; QUERY: 1, ANSWER: {answer_count}, AUTHORITY: 0, ADDITIONAL: 0")
    print()
    print(";; QUESTION SECTION:")
    print(f";{dominio}.    IN    A")
    print()
    print(";; ANSWER SECTION:")
    if ip != "NXDOMAIN":
        print(f"{dominio}.    60    IN    A    {ip}")
    print()
    print(f";; Query time: {tiempo_ms if tiempo_ms is not None else '?'} msec")
    print(f";; SERVER: {servidor} (UDP)")
    print(f";; WHEN: {date_str}")
    print(f";; MSG SIZE  rcvd: {msg_size}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mi propio dig")
    parser.add_argument("dominio", help="Dominio a resolver (ej: www.ipn.mx)")
    parser.add_argument("@servidor", nargs="?", default="@127.0.0.4", help="Servidor DNS, ej: @127.0.0.4")
    parser.add_argument("--puerto", type=int, default=5304, help="Puerto del servidor DNS")
    args = parser.parse_args()

    # Soportar sintaxis tipo dig @127.0.0.4 dominio
    if args.dominio.startswith("@"):
        servidor = args.dominio[1:]
        dominio = sys.argv[2] if len(sys.argv) > 2 else ""
    else:
        dominio = args.dominio
        servidor = args.__dict__.get("@servidor", "@127.0.0.4")
        if servidor.startswith("@"):
            servidor = servidor[1:]
        else:
            servidor = "127.0.0.4"

    data, tiempo_ms, query_id = consulta_resolver(dominio, servidor, args.puerto)
    if data is None:
        print("Sin respuesta del resolver.")
    else:
        msg_size = len(data)
        mostrar_salida_dig(data, tiempo_ms, f"{servidor}#{args.puerto}", msg_size, dominio, query_id)