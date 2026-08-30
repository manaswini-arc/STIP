import socket
import threading
import time
import struct

# Network Interface configuration
BIND_IP = "127.0.0.1"
BIND_PORT = 5005
BUFFER_SIZE = 10  # Pre-allocates exactly 10 safe memory slots in our ring

class CircularTelemetryBuffer:
    def __init__(self, size):
        self.size = size
        # Pre-allocating fixed memory blocks prevents dynamic allocation pauses
        self.buffer = [None] * size  
        self.head = 0  # Where the receiver writes data
        self.tail = 0  # Where the parser reads data
        self.lock = threading.Lock() # Mutex lock to prevent thread race conditions

    def write(self, packet):
        with self.lock:
            self.buffer[self.head] = packet
            # Move the write finger forward in a circle
            self.head = (self.head + 1) % self.size
            
            # Fault protection: If head catches tail, the buffer is full (data overwritten)
            if self.head == self.tail:
                print("⚠️ [Buffer Overflow] Receiver outpaced the parser! Tail bumped.")
                self.tail = (self.tail + 1) % self.size

    def read(self):
        with self.lock:
            # If head equals tail, there is no new telemetry data to read
            if self.head == self.tail:
                return None
            packet = self.buffer[self.tail]
            # Move the read finger forward in a circle
            self.tail = (self.tail + 1) % self.size
            return packet

def udp_receiver_thread(ring_buffer):
    """Thread 1: Dedicated solely to pulling bytes off the network card fast."""
    print(f"📡 Receiver Thread Active. Binding to UDP Port {BIND_PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((BIND_IP, BIND_PORT))
    
    while True:
        try:
            data, addr = sock.recvfrom(1024) # Capture incoming network payload
            if data:
                ring_buffer.write(data)
        except Exception as e:
            print(f"Receiver exception: {e}")
            break

def telemetry_parser_thread(ring_buffer):
    """Thread 2: Dedicated to reading data safely out of the ring memory."""
    print("🧠 Telemetry Parser Engine Active. Processing frames...")
    while True:
        raw_packet = ring_buffer.read()
        
        if raw_packet is None:
            time.sleep(0.1) # Wait briefly for the satellite to beam more data
            continue
            
        try:
            # Unpack the 10-byte structure back into standard system decimals
            header_sync, seq_id, sub_id, value = struct.unpack("!BIBf", raw_packet)
            
            if header_sync == 0xAA:
                subsystem_name = "Thermal" if sub_id == 0x01 else "Power System"
                print(f"✅ Parsed Frame -> Seq: {seq_id} | Subsystem: {subsystem_name} | Sensor Value: {value:.2f}")
        except Exception as e:
            print(f"Error parsing telemetry frame bytes: {e}")

def main():
    # Instantiate our fixed circular memory track
    shared_ring = CircularTelemetryBuffer(BUFFER_SIZE)
    
    # Fire up both execution threads working on the same memory block
    t1 = threading.Thread(target=udp_receiver_thread, args=(shared_ring,), daemon=True)
    t2 = threading.Thread(target=telemetry_parser_thread, args=(shared_ring,), daemon=True)
    
    t1.start()
    t2.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Ground Station processing architecture.")

if __name__ == "__main__":
    main()
  
