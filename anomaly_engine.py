import os
import requests

# Connection endpoint for your private phone alerts channel
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "isro-drdo-26")

class TelemetryAnomalyEngine:
    def __init__(self):
        self.last_sequence_id = None
        self.thermal_fault_counter = 0
        self.voltage_fault_counter = 0

    def trigger_ground_alert(self, severity, message):
        """Dispatches an emergency alert directly to the operator's ntfy app feed."""
        prefix = "🚨 [CRITICAL FAULT]" if severity == "HIGH" else "⚠️ [WARNING]"
        payload = f"{prefix}\n{message}"
        print(payload)
        
        try:
            requests.post(f"https://ntfy.sh{NTFY_TOPIC}", data=payload.encode('utf-8'))
        except Exception as e:
            print(f"Failed to transmit alert to ntfy network: {e}")

    def evaluate_sensor_frame(self, sequence_id, subsystem_id, sensor_value):
        """Analyzes real-time frames for sequence dropouts and consecutive out-of-bounds readings."""
        
        # --- 1. NETWORK LOSS LAYER ---
        if self.last_sequence_id is not None:
            # If sequence gap is greater than 1, a packet was lost in the atmosphere
            if sequence_id > self.last_sequence_id + 1:
                dropped_count = sequence_id - self.last_sequence_id - 1
                self.trigger_ground_alert(
                    "LOW", 
                    f"Telemetry Packet Gap! Dropped {dropped_count} frames between Seq ID {self.last_sequence_id} and {sequence_id}."
                )
        self.last_sequence_id = sequence_id

        # --- 2. THERMAL REGULATION MONITOR (Subsystem 0x01) ---
        if subsystem_id == 0x01:
            if sensor_value > 38.0:  # Mock critical upper boundary limit for satellite systems
                self.thermal_fault_counter += 1
                if self.thermal_fault_counter >= 3:
                    self.trigger_ground_alert(
                        "HIGH", 
                        f"CRITICAL OVERHEATING! Thermal sub-assembly has spent 3 consecutive seconds over safety threshold. Cur: {sensor_value:.2f}°C"
                    )
            else:
                # Reset error sequence counters once safe thresholds are restored
                self.thermal_fault_counter = 0

        # --- 3. POWER SYSTEM VOLTAGE MONITOR (Subsystem 0x02) ---
        elif subsystem_id == 0x02:
            if sensor_value < 3.4:  # Critically low battery cell discharge state threshold
                self.voltage_fault_counter += 1
                if self.voltage_fault_counter >= 3:
                    self.trigger_ground_alert(
                        "HIGH", 
                        f"CRITICAL BUS UNDERVOLTAGE! Onboard battery grid cells drained past absolute storage limit. Cur: {sensor_value:.2f}V"
                    )
            else:
                self.voltage_fault_counter = 0

# Mock initialization interface block for standalone engineering assessment checks
if __name__ == "__main__":
    print("🧠 Anomaly Engine Active. Awaiting evaluation parameters...")
    engine = TelemetryAnomalyEngine()
    
    # Test Evaluation Frame execution path check
    # Simulates an immediate critical heat spike sequence loop to test notification routing path
    print("Testing pipeline logic...")
    engine.evaluate_sensor_frame(1, 0x01, 39.5)
    engine.evaluate_sensor_frame(2, 0x01, 41.2)
    engine.evaluate_sensor_frame(3, 0x01, 40.8) # This third consecutive breach will trip the alert engine
  
