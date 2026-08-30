import socket
import time
import random
import struct

# Network configuration for local machine transmission
TARGET_IP = "127.0.0.1"
TARGET_PORT = 5005

def generate_telemetry_packet(sequence_id):
    """
    Packs aerospace sensor data into a strict binary format.
    Total frame size: 10 Bytes
    Layout: 
      - [1 Byte]  Header Sync (0xAA)
      - [4 Bytes] Sequence ID (Integer)
      - [1 Byte]  Subsystem ID (0x01=Thermal, 0x02=Power)
      - [4 Bytes] Sensor Value (Float reading)
    """
    header_sync = 0xAA  
    subsystem_id = random.choice([0x01, 0x02]) # 0x01: Temperature, 0x02: Battery Voltage
    
    if subsystem_id == 0x01:
        sensor_val = random.uniform(25.0, 42.0)  # Temperature in Celsius (can cross 38.0 limits!)
    else:
        sensor_val = random.uniform(3.2, 4.2)    # Battery cell voltage (can drop below 3.4 bounds!)
        
    # '!BIBf' structures the network byte order (Big-Endian configuration)
    packet = struct.pack("!BIBf", header_sync, sequence_id, subsystem_id, sensor_val)
    return packet

def main():
    print(f"🚀 Satellite Core Active. Streaming telemetry to {TARGET_IP}:{TARGET_PORT}...")
    
    # Initialize a pure network socket using UDP (SOCK_DGRAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sequence_id = 1
    
    try:
        while True:
            # Intentionally drop every 12th packet to simulate telemetry signal loss
            if sequence_id % 12 == 0:
                print(f"📡 [Simulation] Simulating atmospheric signal loss at Seq: {sequence_id}")
                sequence_id += 1
                continue
                
            raw_packet = generate_telemetry_packet(sequence_id)
            sock.sendto(raw_packet, (TARGET_IP, TARGET_PORT))
            print(f"🛰️ Packet Pushed -> Seq ID: {sequence_id}")
            
            sequence_id += 1
            time.sleep(1.0) # Transmit exactly 1 packet per second
            
    except KeyboardInterrupt:
        print("\nSatellite stream stopped safely.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
  
