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

def mostrar_salida_dig(respuesta, tiempo_ms, servidor, msg_size):
    print(respuesta.decode())
    print(f";; Query time: {tiempo_ms if tiempo_ms is not None else '?'} msec")
    print(f";; SERVER: {servidor} (UDP)")
    import time as t
    print(f";; WHEN: {t.strftime('%a %b %d %H:%M:%S UTC %Y', t.gmtime())}")
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
        mostrar_salida_dig(data, tiempo_ms, f"{servidor}#{args.puerto}", msg_size)