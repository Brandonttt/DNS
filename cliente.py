import socket
import time
import random

def consulta_resolver(dominio):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    inicio = time.time()
    query_id = random.randint(10000, 65000)
    mensaje = f"{query_id}|{dominio}"
    sock.sendto(mensaje.encode(), ("127.0.0.4", 5304))
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
    dominio = input("Dominio a resolver (ej: www.ipn.mx): ").strip()
    data, tiempo_ms, query_id = consulta_resolver(dominio)
    if data is None:
        print("Sin respuesta del resolver.")
    else:
        msg_size = len(data)
        servidor = "127.0.0.4#5304"
        mostrar_salida_dig(data, tiempo_ms, servidor, msg_size)