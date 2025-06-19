import os
import socket

# Get machine's IP (or fallback to env)
def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return os.getenv("HL7_HOST", "0.0.0.0")

HL7_HOST = get_local_ip()
HL7_PORT = int(os.getenv("HL7_PORT", 5030))

ERP_URL = os.getenv("ERP_URL")
ERP_USER = os.getenv("ERP_USER")
ERP_PASSWORD = os.getenv("ERP_PASSWORD")
