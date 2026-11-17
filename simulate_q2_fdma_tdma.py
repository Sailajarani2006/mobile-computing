"""
Simulation for Q2: Sharing the Channel - FDMA vs TDMA Under Different Traffic
Hostel-Campus Voice and Telemetry (2 MHz band per direction)

FDMA: 25 kHz channels (Nominal: 80).
  Usable channels after 50 kHz band edges (2x25 kHz) = 78 RF channels.
  2 channels reserved for Control/Paging -> 76 usable traffic channels.
  Payload efficiency per channel ~ 95% (small analog/digital guard).

TDMA: 200 kHz carriers, 8 slots/carrier (Nominal: 80).
  Band edges guard: 100 kHz (2x50 kHz) -> 9 carriers = 72 slots.
  Carrier 0 Slot 0 & 1 reserved for BCCH/FCCH/SCH/RACH -> 70 usable traffic slots.
  Time-domain overhead (Guard time 8.25b, Sync/Training 26b, Tail 6b out of 156.25b)
  plus 26-multiframe control (1/26) -> Payload efficiency per slot ~ 72.96% * 96.15% = 70.15%.

Datasets:
  1. Continuous Voice (100% voice, holding time mean 120s, 100% duty cycle)
  2. Bursty Telemetry/Data (10% duty cycle during session, mean session 20s)
  3. Mixed Traffic (70% Voice, 30% Bursty Data)
  4. Edge Case: Synchronized Arrival / Alarm Cascade (150 sudden requests at peak)
"""

import random
import math
import statistics

class TrafficGenerator:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)

    def generate_events(self, dataset_type, duration=3600):
        """
        Generates list of events: (arrival_time, holding_time, duty_cycle, traffic_type)
        """
        events = []
        t = 0.0
        
        if dataset_type == "continuous_voice":
            # Poisson arrivals, offered load ~ 65 Erlangs
            # lambda = 65 / 120 = 0.5417 calls/sec
            arrival_rate = 65.0 / 120.0
            while t < duration:
                inter_arrival = self.rng.expovariate(arrival_rate)
                t += inter_arrival
                if t >= duration:
                    break
                holding = self.rng.expovariate(1.0 / 120.0) # mean 120s
                events.append((t, holding, 1.0, "voice"))

        elif dataset_type == "bursty_data":
            # Bursty sessions with 10% duty cycle, session duration mean 30s
            # High arrival rate ~ 2.0 arrivals/sec
            arrival_rate = 2.2
            while t < duration:
                inter_arrival = self.rng.expovariate(arrival_rate)
                t += inter_arrival
                if t >= duration:
                    break
                session_len = self.rng.expovariate(1.0 / 30.0) # mean 30s
                events.append((t, session_len, 0.10, "data"))

        elif dataset_type == "mixed_70_30":
            # 70% voice calls, 30% bursty data
            # Target total offered load ~ 70 Erlangs
            arrival_rate = 0.8
            while t < duration:
                inter_arrival = self.rng.expovariate(arrival_rate)
                t += inter_arrival
                if t >= duration:
                    break
                is_voice = (self.rng.random() < 0.70)
                if is_voice:
                    holding = self.rng.expovariate(1.0 / 120.0)
                    events.append((t, holding, 1.0, "voice"))
                else:
                    holding = self.rng.expovariate(1.0 / 30.0)
                    events.append((t, holding, 0.10, "data"))

        elif dataset_type == "edge_synchronized_burst":
            # Regular light background traffic + massive synchronized arrival flash crowd
            arrival_rate = 0.2
            while t < duration:
                inter_arrival = self.rng.expovariate(arrival_rate)
                t += inter_arrival
                if t >= duration:
                    break
                holding = self.rng.expovariate(1.0 / 60.0)
                events.append((t, holding, 0.50, "sensor"))
            
            # Flash crowd at t = 1800.0s (e.g. 160 sensors report simultaneously)
            flash_time = 1800.0
            for _ in range(160):
                # Arrive within a tight 2-second window
                arr = flash_time + self.rng.uniform(0.0, 2.0)
                holding = self.rng.uniform(15.0, 45.0)
                events.append((arr, holding, 0.10, "alarm"))
            events.sort(key=lambda x: x[0])

        return events


def simulate_dedicated_allocation(channels, bit_efficiency, events, duration=3600):
    """
    Simulates a dedicated multi-server queue (M/M/c/c Erlang loss system).
    channels: integer number of usable trunks/channels.
    bit_efficiency: physical payload fraction after guard times/sync/control.
    """
    channel_free_times = [0.0] * channels
    
    total_requests = len(events)
    admitted = 0
    blocked = 0
    
    # Integrated channel-busy time (channel-seconds)
    total_channel_busy_time = 0.0
    # Integrated true payload transmission time
    total_payload_busy_time = 0.0

    for arrival, holding, duty_cycle, ttype in events:
        # Find first free channel
        allocated = False
        for i in range(channels):
            if channel_free_times[i] <= arrival:
                # Channel is free!
                channel_free_times[i] = arrival + holding
                admitted += 1
                allocated = True
                total_channel_busy_time += holding
                total_payload_busy_time += (holding * duty_cycle * bit_efficiency)
                break
        if not allocated:
            blocked += 1

    total_capacity_available = channels * duration
    raw_utilization = (total_channel_busy_time / total_capacity_available) * 100.0
    effective_payload_utilization = (total_payload_busy_time / total_capacity_available) * 100.0
    blocking_prob = (blocked / total_requests) * 100.0 if total_requests else 0.0
    wasted_capacity_ratio = (1.0 - (total_payload_busy_time / total_capacity_available)) * 100.0

    return {
        "channels": channels,
        "total_requests": total_requests,
        "admitted": admitted,
        "blocked": blocked,
        "blocking_prob": blocking_prob,
        "raw_utilization": raw_utilization,
        "effective_payload_utilization": effective_payload_utilization,
        "wasted_capacity_ratio": wasted_capacity_ratio
    }


def run_q2():
    tg = TrafficGenerator(seed=101)
    datasets = ["continuous_voice", "bursty_data", "mixed_70_30", "edge_synchronized_burst"]
    
    # FDMA parameters
    c_fdma = 76
    eff_fdma = 0.95
    
    # TDMA parameters
    c_tdma = 70
    eff_tdma = 0.7015

    results = {}
    for ds in datasets:
        events = tg.generate_events(ds, duration=3600)
        fdma_res = simulate_dedicated_allocation(c_fdma, eff_fdma, events, duration=3600)
        tdma_res = simulate_dedicated_allocation(c_tdma, eff_tdma, events, duration=3600)
        results[ds] = {
            "events_count": len(events),
            "fdma": fdma_res,
            "tdma": tdma_res
        }

    return results

if __name__ == "__main__":
    res = run_q2()
    print("="*85)
    print("Q2 SIMULATION RESULTS: FDMA (76 ch) vs TDMA (70 ch) UNDER CONTRASTING TRAFFIC")
    print("="*85)
    for ds, data in res.items():
        print(f"\n--- Dataset: {ds} (Total Arrivals: {data['events_count']}) ---")
        f = data["fdma"]
        t = data["tdma"]
        print(f"FDMA (76 channels, eff: 95.0%):")
        print(f"  Admitted: {f['admitted']}, Blocked: {f['blocked']} (Pb = {f['blocking_prob']:.2f}%)")
        print(f"  Raw Trunk Utilization: {f['raw_utilization']:.2f}%, Effective Payload Util: {f['effective_payload_utilization']:.2f}%, Wasted: {f['wasted_capacity_ratio']:.2f}%")
        print(f"TDMA (70 channels, eff: 70.15%):")
        print(f"  Admitted: {t['admitted']}, Blocked: {t['blocked']} (Pb = {t['blocking_prob']:.2f}%)")
        print(f"  Raw Trunk Utilization: {t['raw_utilization']:.2f}%, Effective Payload Util: {t['effective_payload_utilization']:.2f}%, Wasted: {t['wasted_capacity_ratio']:.2f}%")
