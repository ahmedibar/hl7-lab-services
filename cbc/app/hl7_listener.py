import aiorun
import asyncio
import sys
import requests
from datetime import datetime
import json
import os
import time
import logging
from logging.handlers import RotatingFileHandler

from hl7 import parser
import hl7
from hl7.mllp import start_hl7_server
from hl7apy.parser import parse_message
from send_to_erp import send_to_erp
from local_config import HL7_HOST, HL7_PORT



async def process_hl7_messages(hl7_reader, hl7_writer):
    peername = hl7_writer.get_extra_info("peername")
    print(f"Connection established {peername}")

    try:
        while not hl7_writer.is_closing():
            try:
                hl7_message = await hl7_reader.readmessage()
                str_hl7_message = str(hl7_message)
                msg_lines = str_hl7_message.splitlines()

                results = []
                hormone = 0

                if len(msg_lines) > 3:
                    lab_test_name = msg_lines[2].split('|')[2]

                machine_model = msg_lines[0].split('|')[2]
                machine_make = msg_lines[0].split('|')[3]

                if machine_model == "Maglumi User":
                    for m in msg_lines:
                        row = m.split('|')
                        if row[0] == "SPM":
                            lab_test_name = row[2].split('^')[0]
                        if row[0] == "OBX":
                            hormone = 1
                            try:
                                raw_value = row[5].split('^')[0].strip()
                                value = round(float(raw_value), 2)
                                results.append({"par": row[3], "value": value})
                                print("inta", row[3])
                            except Exception as e:
                                print(f"Error parsing OBX value: {e}")
                else:
                    msg = hl7.parse(str_hl7_message)
                    for segment in msg:
                        s_type = str(segment[0]).lower().strip()
                        fields = segment[1:]

                        if s_type == "obr":
                            sample = str(fields).split("|")

                        if s_type == "obx":
                            result = str(fields).split("|")
                            if result[1] == "NM":
                                # print(result)
                                try:
                                    normal = result[6]
                                    pure_result = result[2].split('^')[0].strip()
                                    raw_value = result[4].split('^')[0].strip()
                                    value = round(float(raw_value), 2)
                                    results.append({"par": pure_result, "value": value, "normal_range": normal})
                                except Exception as e:
                                    print(f"Error parsing OBX numeric: {e}")

                send_to_erp(lab_test_name, results, hormone)

                await hl7_writer.drain()

            except (ConnectionResetError, asyncio.IncompleteReadError) as e:
                print(f"[{peername}] Connection lost: {e}")
                break
            except Exception as e:
                print(f"[{peername}] Unexpected error: {e}")

    finally:
        print(f"Connection closed {peername}")
        if not hl7_writer.is_closing():
            hl7_writer.close()
            await hl7_writer.wait_closed()


async def main():
    try:
        print(f"Starting HL7 CBC server on {HL7_HOST}:{HL7_PORT}...")
        async with await start_hl7_server(
            process_hl7_messages, 
            # '192.168.19.152', 
            HL7_HOST,
            # port=5660, 
            port=HL7_PORT,
            limit=1024 * 128,
        ) as hl7_server:
            await hl7_server.serve_forever()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Server error: {e}")


def _safe_get_error_str(res):
    try:
        error_json = json.loads(res._content)
        if 'exc' in error_json:
            error_str = json.loads(error_json['exc'])[0]
        else:
            error_str = json.dumps(error_json)
    except:
        error_str = str(res.__dict__)
    return error_str


def setup_logger(name, log_file, level=logging.INFO, formatter=None):
    if not formatter:
        formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')
    handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=50)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger


if __name__ == "__main__":
    aiorun.run(main(), stop_on_unhandled_errors=True)




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

