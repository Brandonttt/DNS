import socket
import random
import os
import ast

<<<<<<< Updated upstream
CACHE = {}

CACHE_FILE = "cache.txt"
=======
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
>>>>>>> Stashed changes

def guardar_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        for key, (answers, authorities, additionals, status) in CACHE.items():
            # Serializa como texto literal de Python para poder hacer eval/ast.literal_eval
            f.write(f"{key}|{status}|{repr(answers)}|{repr(authorities)}|{repr(additionals)}\n")

def cargar_cache():
    if not os.path.exists(CACHE_FILE):
        return
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                key, status, answers_repr, authorities_repr, additionals_repr = line.split("|", 4)
                answers = ast.literal_eval(answers_repr)
                authorities = ast.literal_eval(authorities_repr)
                additionals = ast.literal_eval(additionals_repr)
                CACHE[key] = (answers, authorities, additionals, status)
            except Exception as e:
                print(f"Error cargando línea de cache: {line}\n{e}")

def build_dig_response(query_id, dominio, status="NOERROR", answers=None, authorities=None, additionals=None, qtype="A"):
    answers = answers or []
    authorities = authorities or []
    additionals = additionals or []

    header = f";; ->>HEADER<<- opcode: QUERY, status: {status}, id: {query_id}"
    flags = f";; flags: qr rd ra; QUERY: 1, ANSWER: {len(answers)}, AUTHORITY: {len(authorities)}, ADDITIONAL: {len(additionals)}"
    edns = ";; OPT PSEUDOSECTION:\n;; EDNS: version: 0, flags:; udp: 512"
    question = f";; QUESTION SECTION:\n;{dominio}.    IN  {qtype}"

    def section_block(title, section):
        if section:
            return f";; {title}:\n" + "\n".join(section)
        return ""

    answer_section = section_block("ANSWER SECTION", answers)
    authority_section = section_block("AUTHORITY SECTION", authorities)
    additional_section = section_block("ADDITIONAL SECTION", additionals)

    response_parts = [
        header,
        flags,
        edns,
        question,
        "",
    ]
    if answer_section:
        response_parts.append(answer_section)
        response_parts.append("")
    if authority_section:
        response_parts.append(authority_section)
        response_parts.append("")
    if additional_section:
        response_parts.append(additional_section)
        response_parts.append("")

    return "\n".join(response_parts)

def consulta_autoritativo(dominio):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.sendto(dominio.encode(), ("127.0.0.3", 5302))
    try:
<<<<<<< Updated upstream
        data, _ = sock.recvfrom(2048)
        respuesta = data.decode().splitlines()
        return respuesta
    except socket.timeout:
        return ["NXDOMAIN"]

def parsear_registros_autoritativo(dominio, registros):
    answers = []
    authorities = []
    additionals = []
    status = "NOERROR"
    for reg in registros:
        if reg.startswith("A "):
            ip = reg.split(" ", 1)[1]
            answers.append(f"{dominio}. 3600 IN A {ip}")
        elif reg.startswith("CNAME "):
            cname = reg.split(" ", 1)[1]
            answers.append(f"{dominio}. 3600 IN CNAME {cname}.")
        elif reg.startswith("NS "):
            parts = reg.split()
            ns = parts[1]
            authorities.append(f"ipn.mx. 3600 IN NS {ns}.")
            if len(parts) > 2:
                ns_ip = parts[2]
                additionals.append(f"{ns}. 3600 IN A {ns_ip}")
        elif reg.startswith("MX "):
            mx = reg.split(" ", 1)[1]
            answers.append(f"{dominio}. 3600 IN MX {mx}")
        elif reg == "NXDOMAIN":
            status = "NXDOMAIN"
    return answers, authorities, additionals, status
=======
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
>>>>>>> Stashed changes

def resolver_loop():
    cargar_cache()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.4", 5304))
    print("Resolver escuchando en 127.0.0.4:5304")
    while True:
        data, addr = sock.recvfrom(4096)
        try:
            data_decoded = data.decode()
            if "|" in data_decoded:
                query_id, dominio = data_decoded.split("|", 1)
                query_id = int(query_id)
            else:
                query_id = random.randint(10000, 65000)
                dominio = data.decode().strip()
        except:
            query_id = random.randint(10000, 65000)
            dominio = data.decode().strip()

        key = dominio.strip(".").lower()
        if key in CACHE:
            answers, authorities, additionals, status = CACHE[key]
            print(f"Cache hit para {key}")
        else:
            registros = consulta_autoritativo(key)
            answers, authorities, additionals, status = parsear_registros_autoritativo(dominio, registros)
            CACHE[key] = (answers, authorities, additionals, status)
            guardar_cache()
            print(f"Cache miss para {key}: guardado en cache.")

        msg = build_dig_response(query_id, dominio, status, answers, authorities, additionals, qtype="A")
        sock.sendto(msg.encode(), addr)

if __name__ == "__main__":
    resolver_loop()