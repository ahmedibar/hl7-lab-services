import asyncio
from hl7.mllp import start_hl7_server
from hl7apy.parser import parse_message
import hl7
import logging
from send_to_erp import send_to_erp
import random
from local_config import HL7_HOST, HL7_PORT

# Function to process HL7 messages
async def process_hl7_messages(hl7_reader, hl7_writer):
    peername = hl7_writer.get_extra_info("peername")
    print(f"Connection established {peername}")
    try:
        while not hl7_writer.is_closing():
            hl7_message = await hl7_reader.readmessage()
            str_hl7_message = str(hl7_message)

            msg_lines = str_hl7_message.splitlines()
            # print(msg_lines)
            msg = hl7.parse(str_hl7_message)
            hl = parse_message(str_hl7_message)

            results = []
            for segment in msg:
                segment_name = segment[0]
                fields = segment[1:]
                s_type = str(segment_name).lower().strip()

                if s_type == "obx":
                    result = str(fields).split("|")
                    if result[1] in ["NM", "ST"]:
                        results.append({"par": result[3], "value": result[4]})

            lab_test_name = msg_lines[1].split('|')[3]
            send_to_erp(lab_test_name, results)
            # print(results)

            print(lab_test_name)

            await hl7_writer.drain()

    except (asyncio.IncompleteReadError, ConnectionResetError) as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if not hl7_writer.is_closing():
            hl7_writer.close()
            await hl7_writer.wait_closed()
        print(f"Connection closed {peername}")

# Main server loop with retry
async def start_server_with_retries():
    backoff = 1  # initial wait time in seconds
    max_backoff = 60  # max wait time in seconds

    while True:
        try:
            # print("Starting HL7 server...")
            print(f"Starting HL7 server on {HL7_HOST}:{HL7_PORT}...")
            async with await start_hl7_server(
                process_hl7_messages, 
                # '192.168.19.152', 
                HL7_HOST,
                # port=5030, 
                port=HL7_PORT,
                limit=1024 * 128,
            ) as hl7_server:
                await hl7_server.serve_forever()
        except Exception as e:
            print(f"Server error: {e}")
            print(f"Retrying in {backoff} seconds...")
            await asyncio.sleep(backoff)
            backoff = min(max_backoff, backoff * 2 + random.uniform(0, 1))  # exponential backoff with jitter

# Start the server with aiorun
import aiorun
aiorun.run(start_server_with_retries(), stop_on_unhandled_errors=True)


# # Use this code only when using hl7_test_client.py

# import asyncio
# from hl7.mllp import start_hl7_server

# # MLLP ACK message (sample)
# ACK_MESSAGE = (
#     "MSH|^~\\&|Receiver|ReceiverFac|Sender|SenderFac|202406161200||ACK^O01|654321|P|2.3\r"
#     "MSA|AA|123456\r"
# )

# # Framing characters
# START_BLOCK = b'\x0b'
# END_BLOCK = b'\x1c\r'

# async def process_hl7_messages(hl7_reader, hl7_writer):
#     peername = hl7_writer.get_extra_info("peername")
#     print(f"Connection established {peername}")
#     try:
#         while not hl7_writer.is_closing():
#             hl7_message = await hl7_reader.readmessage()
#             str_hl7_message = str(hl7_message)

#             print("Received HL7 message:")
#             print(str_hl7_message)

#             # Send HL7 ACK response
#             framed_ack = START_BLOCK + ACK_MESSAGE.encode('utf-8') + END_BLOCK
#             hl7_writer.write(framed_ack)
#             await hl7_writer.drain()
#             print("ACK sent")

#     except (asyncio.IncompleteReadError, ConnectionResetError) as e:
#         print(f"Connection error: {e}")
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#     finally:
#         if not hl7_writer.is_closing():
#             hl7_writer.close()
#             await hl7_writer.wait_closed()
#         print(f"Connection closed {peername}")

# # Run the server
# async def main():
#     host = "0.0.0.0"  # Accept from any interface
#     port = 5030
#     print(f"Starting HL7 server on {host}:{port}...")
#     async with await start_hl7_server(process_hl7_messages, host=host, port=port) as server:
#         await server.serve_forever()

# if __name__ == "__main__":
#     import aiorun
#     aiorun.run(main(), stop_on_unhandled_errors=True)

