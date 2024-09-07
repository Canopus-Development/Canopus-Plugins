import psutil
import logging
import requests
from ipaddress import ip_address
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

VT_API_KEY = 'Virus Total API Key'
VT_API_URL = 'https://www.virustotal.com/vtapi/v2/ip-address/report'

if not VT_API_KEY:
    logging.error("VirusTotal API key is not set.")
    raise EnvironmentError("VirusTotal API key is not set.")

def check_ip_reputation(ip):
    try:
        params = {'apikey': VT_API_KEY, 'ip': ip}
        response = requests.get(VT_API_URL, params=params)
        response.raise_for_status()
        result = response.json()
        if result['response_code'] == 1 and 'detected_urls' in result and result['detected_urls']:
            return True
        return False
    except Exception as e:
        logging.error(f"Error checking IP reputation: {e}")
        return False

def detect_remote_access():
    logging.info("Starting remote access detection...")
    suspicious_connections = []
    connection_counter = Counter()

    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr and conn.raddr:
                local_ip, local_port = conn.laddr
                remote_ip, remote_port = conn.raddr
                logging.debug(f"Connection from {local_ip}:{local_port} to {remote_ip}:{remote_port}")

                connection_counter[remote_ip] += 1
                if connection_counter[remote_ip] > 5:
                    logging.warning(f"Suspicious activity detected from IP: {remote_ip}")
                    suspicious_connections.append(remote_ip)
    except Exception as e:
        logging.error(f"Error detecting remote access: {e}")

    high_risk_ips = [ip for ip in suspicious_connections if check_ip_reputation(ip)]

    if high_risk_ips:
        message = f"High-risk remote access detected from IPs: {', '.join(high_risk_ips)}"
        logging.info(message)
        return message
    else:
        message = "No suspicious remote access detected."
        logging.info(message)
        return message
