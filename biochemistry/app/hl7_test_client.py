import socket

# HL7 message
hl7_message = (
    "MSH|^~\\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|202406161200||ORM^O01|123456|P|2.3\r"
    "PID|1||123456^^^Hospital^MR||Doe^John||19800101|M\r"
    "PV1|1|I|W^389^1^UABH||||1234^Smith^Jack\r"
)

# MLLP framing
START_BLOCK = b'\x0b'
END_BLOCK = b'\x1c\r'
framed_message = START_BLOCK + hl7_message.encode('utf-8') + END_BLOCK

# Replace with the server IP or localhost if local
host = "127.0.0.1"  # or "192.168.x.x" for Docker on LAN
port = 5680

try:
    with socket.create_connection((host, port), timeout=10) as s:
        print("Connected to HL7 server")
        s.sendall(framed_message)
        print("HL7 message sent")

        ack = s.recv(4096)
        print("Received ACK/Response:\n", ack.decode("utf-8", errors="ignore"))

except Exception as e:
    print("Error:", e)
