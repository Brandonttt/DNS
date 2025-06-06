#!/usr/bin/env python3
import socket
from dnslib import DNSRecord, QTYPE, RR, A, RCODE
import threading
import time
import json

# Configuración de puertos/IP internos de tus servidores
ROOT_IP = "127.0.0.1"    # Debe coincidir con el bind de raiz.py
ROOT_PORT = 5300
TLD_IP = "127.0.0.2"     # Debe coincidir con el bind de TLD.py
TLD_PORT = 5301
AUTH_IP = "127.0.0.3"    # Debe coincidir con el bind de autoritativo.py
AUTH_PORT = 5302

LISTEN_IP = "127.0.0.4"
LISTEN_PORT = 5304  # Cambia a 53 para producción real (requiere sudo)

TIMEOUT = 2  # segundos para timeouts de sockets internos

# Cache para respuestas exitosas e NXDOMAIN
cache = {}

def guardar_cache_en_archivo():
    # Solo guarda las IPs y expiraciones
    serializable = {dom: {'ip': ip, 'expires': expires} for dom, (ip, expires) in cache.items()}
    with open("cache.txt", "w") as f:
        json.dump(serializable, f, indent=2)

def cargar_cache_de_archivo():
    try:
        with open("cache.txt", "r") as f:
            data = json.load(f)
            for dom, v in data.items():
                cache[dom] = (v['ip'], v['expires'])
    except Exception:
        pass  # Si no existe, no pasa nada

def consulta_servidor(ip, puerto, mensaje):
    """Envía mensaje a un servidor DNS interno y espera respuesta como texto."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(TIMEOUT)
        try:
            s.sendto(mensaje.encode(), (ip, puerto))
            data, _ = s.recvfrom(1024)
            return data.decode().strip()
        except (socket.timeout, ConnectionResetError):
            return None

def resolver_iterativo(dominio):
    # 1. Revisar cache
    now = time.time()
    if dominio in cache:
        ip, expires = cache[dominio]
        if expires > now:
            print(f"[CACHE HIT] {dominio} -> {ip}")
            return ip
        else:
            del cache[dominio]  # Expirado

    # 2. Consulta raíz para TLD
    tld_resp = consulta_servidor(ROOT_IP, ROOT_PORT, dominio)
    if not tld_resp or not tld_resp.startswith("NS "):
        return None
    tld_ip = tld_resp.split(" ")[1]
    # 3. Consulta TLD para autoritativo
    auth_resp = consulta_servidor(tld_ip, TLD_PORT, dominio)
    if not auth_resp or not auth_resp.startswith("NS "):
        return None
    auth_ip = auth_resp.split(" ")[1]
    # 4. Consulta autoritativo para IP final
    final_resp = consulta_servidor(auth_ip, AUTH_PORT, dominio)
    if not final_resp or "NXDOMAIN" in final_resp:
        # Cachear NXDOMAIN por 30s
        cache[dominio] = (None, now + 30)
        guardar_cache_en_archivo()
        return None
    # Devuelve el primer registro A encontrado
    for line in final_resp.splitlines():
        if line.startswith("A "):
            ip = line.split()[1]
            cache[dominio] = (ip, now + 60)  # TTL 60 segundos
            guardar_cache_en_archivo()
            return ip
    # Si no hay registro A, cachear como NXDOMAIN
    cache[dominio] = (None, now + 30)
    guardar_cache_en_archivo()
    return None

def handle_dns_query(data, addr, sock):
    # Intentar parsear como paquete DNS estándar
    try:
        request = DNSRecord.parse(data)
        qname = str(request.q.qname).rstrip(".")
        qtype = QTYPE[request.q.qtype]
        print(f"Consulta estándar recibida: {qname} tipo {qtype} desde {addr}")

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
    except Exception:
        # Si falla el parseo, intentar como formato personalizado (query_id|dominio)
        try:
            mensaje = data.decode(errors="ignore")
            if "|" in mensaje:
                query_id, dominio = mensaje.split("|", 1)
                dominio = dominio.strip()
                print(f"Consulta personalizada recibida: {dominio} (id {query_id}) de {addr}")

                ip = resolver_iterativo(dominio)
                if ip:
                    respuesta = f"{ip}"
                else:
                    respuesta = "NXDOMAIN"
                sock.sendto(respuesta.encode(), addr)
            else:
                print(f"Formato de mensaje no reconocido de {addr}")
        except Exception as ex:
            print(f"Error procesando consulta personalizada: {ex}")

def resolver_loop():
    cargar_cache_de_archivo()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    print(f"Resolver escuchando en {LISTEN_IP}:{LISTEN_PORT} (compatible con dig y cliente personalizado)")

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            threading.Thread(target=handle_dns_query, args=(data, addr, sock), daemon=True).start()
        except ConnectionResetError:
            print("ConnectionResetError ignorado (puede ser Windows o cliente cerrado).")
            continue
        except Exception as e:
            print(f"Error inesperado en el loop: {e}")
            continue

if __name__ == "__main__":
    resolver_loop()