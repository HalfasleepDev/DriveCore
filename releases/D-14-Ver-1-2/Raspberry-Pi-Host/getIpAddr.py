import socket

def get_local_ip():
    """Returns the local IP address of the machine on the network."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # Connect to Google's DNS to determine IP
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip