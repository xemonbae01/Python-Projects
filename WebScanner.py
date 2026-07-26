import socket
import ssl
import sys
import json
import time
from urllib.parse import urlparse
from datetime import datetime

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

try:
    import dns.resolver
except ImportError:
    print("Install dnspython: pip install dnspython")
    sys.exit(1)

try:
    import whois
except ImportError:
    whois = None

def banner():
    print("""
╔══════════════════════════════════════╗
║       WEBSITE RECON SCANNER          ║
╚══════════════════════════════════════╝
""")

def get_ip(domain):
    results = []
    try:
        infos = socket.getaddrinfo(domain, None)
        for info in infos:
            ip = info[4][0]
            if ip not in results:
                results.append(ip)
    except Exception as e:
        results.append(f"Error: {e}")
    return results

def get_dns_records(domain):
    records = {}
    types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
    for rtype in types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records[rtype] = [r.to_text() for r in answers]
        except Exception:
            records[rtype] = []
    return records

def get_whois(domain):
    if whois is None:
        return "python-whois not installed (pip install python-whois)"
    try:
        w = whois.whois(domain)
        data = {
            "domain_name": w.domain_name,
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "updated_date": str(w.updated_date),
            "name_servers": w.name_servers,
            "status": w.status,
            "emails": w.emails,
            "org": w.org,
            "country": w.country,
        }
        return data
    except Exception as e:
        return f"WHOIS error: {e}"

def get_http_info(url):
    info = {}
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
        info["final_url"] = r.url
        info["status_code"] = r.status_code
        info["headers"] = dict(r.headers)
        info["cookies"] = {c.name: c.value for c in r.cookies}
        info["server"] = r.headers.get("Server", "Unknown")
        info["x_powered_by"] = r.headers.get("X-Powered-By", "Not set")
        info["content_type"] = r.headers.get("Content-Type", "Unknown")
        info["content_length"] = r.headers.get("Content-Length", "Unknown")
    except Exception as e:
        info["error"] = str(e)
    return info

def get_ssl_info(domain):
    info = {}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=8) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                info["version"] = ssock.version()
                info["cipher"] = ssock.cipher()
                info["subject"] = dict(x[0] for x in cert.get("subject", []))
                info["issuer"] = dict(x[0] for x in cert.get("issuer", []))
                info["serialNumber"] = cert.get("serialNumber")
                info["notBefore"] = cert.get("notBefore")
                info["notAfter"] = cert.get("notAfter")
                info["subjectAltName"] = cert.get("subjectAltName", [])
    except Exception as e:
        info["error"] = str(e)
    return info

def get_robots(url):
    try:
        r = requests.get(url.rstrip("/") + "/robots.txt", timeout=8)
        if r.status_code == 200:
            return r.text[:2000]
        return f"Status: {r.status_code}"
    except Exception as e:
        return str(e)

def get_tech_guess(headers):
    techs = []
    server = headers.get("Server", "").lower()
    powered = headers.get("X-Powered-By", "").lower()
    if "nginx" in server:
        techs.append("Nginx")
    if "apache" in server:
        techs.append("Apache")
    if "cloudflare" in server:
        techs.append("Cloudflare")
    if "php" in powered:
        techs.append("PHP")
    if "asp.net" in powered or "asp.net" in server:
        techs.append("ASP.NET")
    if "express" in powered:
        techs.append("Express.js")
    if "iis" in server:
        techs.append("IIS")
    if headers.get("X-Drupal-Cache"):
        techs.append("Drupal")
    if "wordpress" in str(headers).lower():
        techs.append("WordPress")
    return techs if techs else ["Unknown"]

def scan(target):
    if not target.startswith("http"):
        url = "https://" + target
    else:
        url = target

    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path.split("/")[0]
    domain = domain.split(":")[0]

    print(f"[*] Target      : {url}")
    print(f"[*] Domain      : {domain}")
    print(f"[*] Scan started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    print("\n[+] Resolving IP addresses...")
    ips = get_ip(domain)
    for ip in ips:
        print(f"    {ip}")

    print("\n[+] DNS Records...")
    dns_data = get_dns_records(domain)
    for rtype, values in dns_data.items():
        if values:
            print(f"    {rtype}:")
            for v in values:
                print(f"        {v}")

    print("\n[+] WHOIS Information...")
    whois_data = get_whois(domain)
    if isinstance(whois_data, dict):
        for k, v in whois_data.items():
            print(f"    {k}: {v}")
    else:
        print(f"    {whois_data}")

    print("\n[+] HTTP Information...")
    http_info = get_http_info(url)
    if "error" in http_info:
        print(f"    Error: {http_info['error']}")
    else:
        print(f"    Final URL     : {http_info.get('final_url')}")
        print(f"    Status Code   : {http_info.get('status_code')}")
        print(f"    Server        : {http_info.get('server')}")
        print(f"    X-Powered-By  : {http_info.get('x_powered_by')}")
        print(f"    Content-Type  : {http_info.get('content_type')}")
        print(f"    Content-Length: {http_info.get('content_length')}")
        print(f"    Cookies       : {http_info.get('cookies')}")
        print("\n    Response Headers:")
        for k, v in http_info.get("headers", {}).items():
            print(f"        {k}: {v}")

        techs = get_tech_guess(http_info.get("headers", {}))
        print(f"\n    Detected Tech : {', '.join(techs)}")

    print("\n[+] SSL Certificate...")
    ssl_info = get_ssl_info(domain)
    if "error" in ssl_info:
        print(f"    {ssl_info['error']}")
    else:
        for k, v in ssl_info.items():
            print(f"    {k}: {v}")

    print("\n[+] robots.txt...")
    robots = get_robots(url)
    print(robots[:1500] if robots else "Not found")

    print("\n" + "=" * 50)
    print("Scan finished.")
    print("=" * 50)

if __name__ == "__main__":
    banner()
    if len(sys.argv) < 2:
        target = input("Enter website (example.com or https://example.com): ").strip()
    else:
        target = sys.argv[1]
    if not target:
        print("No target provided.")
        sys.exit(1)
    scan(target)
