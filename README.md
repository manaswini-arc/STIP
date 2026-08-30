# Sat-Comm Telemetry Ingestion Pipeline (STIP)

A fault-tolerant, multi-threaded ground station simulator designed to ingest, buffer, and analyze high-speed satellite telemetry byte streams without data framework frame drops.

## 🛰️ Architecture Overview

The system is split into three decoupled operational layers to ensure deterministic performance under heavy real-time network loads:
1. **`telemetry_emitter.py`**: Simulates an operational satellite downlink using space-efficient binary serialization (`struct.pack`). It transmits structured sensor payloads over raw **UDP sockets** at deterministic 1Hz frequencies.
2. **`receiver_buffer.py`**: Implements a zero-allocation, thread-safe **Circular Ring Buffer** from scratch. A high-priority background network worker thread continuously ingests incoming UDP frames into memory, while an independent consumer thread extracts frames for parsing, entirely preventing network card drops.
3. **`anomaly_engine.py`**: The intelligence center. It evaluates sequence counters to detect atmospheric signal loss dropouts and monitors critical parameter boundaries (thermal and bus voltages). It leverages an sliding fault counter to suppress brief sensor glitches while triggering immediate emergency overrides via **ntfy** push notifications during persistent breaches.
## 🛠️ Key Technical Highlights for Systems Interviews
* **Low-Level Socket Programming**: Written using un-connected `SOCK_DGRAM` profiles to mirror continuous orbital telecommand downlinks.
* **Deterministic Memory Footprint**: Uses a pre-allocated fixed-size ring matrix rather than expanding dynamic lists (`.append`), eliminating garbage collection latency spikes.
* **Thread Concurrency Control**: Employs mutual exclusion primitives (`threading.Lock`) to completely prevent memory race conditions between data ingestion and decoding cycles.   


