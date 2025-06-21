# Using the third party aiorun instead of the asyncio.run() to avoid boilerplate.
import aiorun
import asyncio
import sys
import requests
from datetime import datetime
import json
import logging
from logging.handlers import RotatingFileHandler
import hl7
from hl7.mllp import start_hl7_server
from send_to_erp import send_to_erp
from local_config import HL7_HOST, HL7_PORT

async def process_hl7_messages(hl7_reader, hl7_writer):
    peername = hl7_writer.get_extra_info("peername")
    print(f"Connection established {peername}")

    try:
        try:
            hl7_message = await hl7_reader.readmessage()
        except asyncio.IncompleteReadError:
            print("Client disconnected while reading message.")
            return
        except Exception as e:
            print(f"❌ Error during message read: {e}")
            return

        if not hl7_message:
            print("⚠️ Empty message received. Closing connection.")
            return

        str_hl7_message = str(hl7_message)
        msg_lines = str_hl7_message.splitlines()

        try:
            lab_test_name = msg_lines[2].split('|')[2]
        except IndexError:
            print("⚠️ Could not extract lab_test_name. Message malformed?")
            print(str_hl7_message)
            return

        msg = hl7.parse(str_hl7_message)
        results = []

        for segment in msg:
            segment_name = segment[0]
            fields = segment[1:]
            s_type = str(segment_name).lower().strip()

            if s_type == "obx":
                result = str(fields).split("|")
                if result[1] in {"NM", "ST"}:
                    results.append({"par": result[3], "value": result[4]})

        send_to_erp(lab_test_name, results)
        print("✅ Message processed successfully.")

    except Exception as e:
        print(f"❌ Error processing message: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if not hl7_writer.is_closing():
            hl7_writer.close()
            await hl7_writer.wait_closed()
        print(f"Connection closed {peername}")

async def main():
    try:
        print(f"Starting HL7 server on {HL7_HOST}:{HL7_PORT}...")
        async with await start_hl7_server(
            process_hl7_messages,
            HL7_HOST,
            port=HL7_PORT,
            limit=1024 * 128,
            encoding='utf-8',
            encoding_errors='replace'
        ) as hl7_server:
            await hl7_server.serve_forever()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"❌ Error occurred in main: {str(e)}")

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
#     port = 5010
#     print(f"Starting HL7 server on {host}:{port}...")
#     async with await start_hl7_server(process_hl7_messages, host=host, port=port) as server:
#         await server.serve_forever()

# if __name__ == "__main__":
#     import aiorun
#     aiorun.run(main(), stop_on_unhandled_errors=True)

