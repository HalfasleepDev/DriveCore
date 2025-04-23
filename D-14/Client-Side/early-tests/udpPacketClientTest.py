import socket
import json
import time
import threading
from queue import Queue  

SERVER_IP = "127.0.0.1"  # Replace 
PORT = 4444

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0)  # Timeout for waiting on ACK

command_queue = Queue()

MAX_RETRIES = 3
COMMAND_ACK_TIMEOUT = 1.0  # seconds

def enqueue_command(cmd: str):
    """Add command to the queue."""
    command_queue.put(cmd)
    print(f"Queued command: {cmd}")

def send_command_with_ack(cmd: str) -> bool:
    """Send command and wait for ACK, retry if needed."""
    payload = {
        "type": "command",
        "command": cmd,
        "timestamp": int(time.time() * 1000)
    }
    encoded = json.dumps(payload).encode()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            sock.sendto(encoded, (SERVER_IP, PORT))
            print(f"Sent '{cmd}' (Attempt {attempt})")

            data, _ = sock.recvfrom(1024)
            ack = json.loads(data.decode())

            if ack.get("type") == "ack" and cmd in ack.get("message", ""):
                print(f"ACK for '{cmd}': {ack['message']}")
                return True
            else:
                print("Received invalid ACK:", ack)

        except socket.timeout:
            print(f"Timeout waiting for ACK (Attempt {attempt})")

    print(f"Failed to deliver command '{cmd}' after {MAX_RETRIES} attempts.")
    return False  # Skip the command

def process_queue():
    """Continuously processes the command queue one at a time."""
    while True:
        cmd = command_queue.get()
        success = send_command_with_ack(cmd)
        if not success:
            print(f"Command '{cmd}' skipped.")
        command_queue.task_done()

# Start the queue processor in a thread
threading.Thread(target=process_queue, daemon=True).start()

# Example usage — you can trigger these from key events
if __name__ == "__main__":
    enqueue_command("UP")
    enqueue_command("LEFTUP")
    enqueue_command("NEUTRAL")
    enqueue_command("RIGHT")
