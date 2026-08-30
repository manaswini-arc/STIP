# Sat-Comm Telemetry Ingestion Pipeline (STIP)

A fault-tolerant, multi-threaded ground station simulator designed to ingest, buffer, and analyze high-speed satellite telemetry byte streams without data framework frame drops.

## 🛰️ Architecture Overview

The system is split into three decoupled operational layers to ensure deterministic performance under heavy real-time network loads:


