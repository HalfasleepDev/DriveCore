import socket
import json

HOST = "0.0.0.0"
PORT = 4444

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT)) 

print(f"Server listening on {HOST}:{PORT}")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            payload = json.loads(data.decode())
            msg_type = payload.get("type")

            if msg_type == "command":
                command = payload.get("command")
                print(f"[COMMAND] {addr} → {command}")

                # Send ACK back to client
                ack_payload = {
                    "type": "ack",
                    "message": f"Command '{command}' received",
                    "timestamp": payload.get("timestamp")
                }
                sock.sendto(json.dumps(ack_payload).encode(), addr)
            
            elif msg_type == "telemetry":
                speed = payload.get("speed")
                battery = payload.get("battery")
                print(f"[TELEMETRY] {addr} → Speed: {speed}, Battery: {battery}%")

            elif msg_type == "mode":
                mode = payload.get("mode")
                print(f"[MODE SWITCH] {addr} → New Mode: {mode}")

            else:
                print(f"[UNKNOWN TYPE] {addr} → {payload}")

        except json.JSONDecodeError:
            print(f"Invalid JSON from {addr}")

except KeyboardInterrupt:
    print("\nServer shutting down.")
finally:
    sock.close()
