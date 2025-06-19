import socket

hl7_message = "MSH|^~\\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|202506161500||ORM^O01|12345|P|2.3\rPID|||123456^^^Hospital^MR||Doe^John\r"

# HL7 MLLP framing: start block 0x0b, end block 0x1c and carriage return 0x0d
start_block = b'\x0b'
end_block = b'\x1c\r'

with socket.create_connection(('localhost', 5030)) as sock:
    sock.sendall(start_block + hl7_message.encode() + end_block)
