"""
Simulation for Q1: Field-Service Technology Audit - Case (e)
Offline Meter Reading Synchronization: Immediate Send vs Store-and-Forward

Investigates link availability at 90%, 60%, and 30%.
Compares:
  Strategy 1: Send Immediately (Drop if disconnected)
  Strategy 2: Store-and-Forward Queue (Buffer locally, transmit upon reconnection)
"""

import random
import statistics

def run_q1_simulation(num_events=10000, seed=42):
    random.seed(seed)
    availabilities = [0.90, 0.60, 0.30]
    results = {}

    for p_avail in availabilities:
        # We model link state transitions using a 2-state Markov chain (Good / Bad)
        # to capture realistic wireless burst fading / coverage shadowing.
        # Average availability = p_avail.
        # Mean outage duration = 5 time steps.
        # P(Bad -> Good) = p_bg = 1.0 / 5 = 0.20.
        # In steady state: p_avail = p_bg / (p_gb + p_bg) => p_gb = p_bg * (1 - p_avail) / p_avail.
        p_bg = 0.20
        p_gb = p_bg * (1.0 - p_avail) / p_avail if p_avail > 0 else 1.0

        # Run simulation for T time steps
        # Each step, a meter reading is generated with probability lambda_gen = 0.2 (1 every 5 steps)
        # Channel capacity when link is UP: can transmit 1 reading per step.
        total_steps = num_events * 5
        link_state = 1 if random.random() < p_avail else 0 # 1 = UP, 0 = DOWN

        # Trackers for Strategy 1: Send Immediately
        s1_generated = 0
        s1_delivered = 0
        s1_lost = 0
        s1_delays = []

        # Trackers for Strategy 2: Store-and-Forward
        s2_generated = 0
        s2_delivered = 0
        s2_delayed = 0
        s2_lost = 0 # With finite buffer (e.g. 1000 items), can drop if full. We give 5000 capacity.
        s2_delays = []
        s2_queue = [] # stores generation timestamp
        max_queue_depth = 0

        reading_id = 0
        for t in range(total_steps):
            # Update Markov link state
            if link_state == 1:
                if random.random() < p_gb:
                    link_state = 0
            else:
                if random.random() < p_bg:
                    link_state = 1

            # Generate reading?
            generated_now = False
            if random.random() < 0.2:
                reading_id += 1
                generated_now = True

            # Strategy 1 Execution
            if generated_now:
                s1_generated += 1
                if link_state == 1:
                    s1_delivered += 1
                    s1_delays.append(0.0) # immediate delivery
                else:
                    s1_lost += 1

            # Strategy 2 Execution
            if generated_now:
                s2_generated += 1
                s2_queue.append(t)
                if len(s2_queue) > max_queue_depth:
                    max_queue_depth = len(s2_queue)

            # Drain queue if link is UP
            if link_state == 1 and len(s2_queue) > 0:
                gen_time = s2_queue.pop(0)
                delay = t - gen_time
                s2_delivered += 1
                s2_delays.append(delay)
                if delay > 0:
                    s2_delayed += 1

        # Post-simulation drain for Strategy 2 if items still left:
        # In real life, field worker reconnects at office (p_avail = 1.0 at end of shift)
        remaining_in_queue = len(s2_queue)
        for gen_time in s2_queue:
            delay = total_steps - gen_time
            s2_delivered += 1
            s2_delays.append(delay)
            s2_delayed += 1
        s2_queue.clear()

        results[p_avail] = {
            "p_avail": p_avail,
            "strategy_1": {
                "generated": s1_generated,
                "delivered": s1_delivered,
                "delayed": 0,
                "lost": s1_lost,
                "delivery_ratio": (s1_delivered / s1_generated) * 100.0 if s1_generated else 0,
                "mean_delay_steps": statistics.mean(s1_delays) if s1_delays else 0.0,
            },
            "strategy_2": {
                "generated": s2_generated,
                "delivered": s2_delivered,
                "delayed": s2_delayed,
                "lost": s2_lost,
                "delivery_ratio": (s2_delivered / s2_generated) * 100.0 if s2_generated else 0,
                "mean_delay_steps": statistics.mean(s2_delays) if s2_delays else 0.0,
                "max_queue_depth": max_queue_depth,
                "remaining_at_shift_end": remaining_in_queue
            }
        }

    return results

if __name__ == "__main__":
    res = run_q1_simulation()
    print("="*75)
    print("Q1 SIMULATION RESULTS: IMMEDIATE SEND VS STORE-AND-FORWARD")
    print("="*75)
    for p, data in res.items():
        print(f"\n--- Link Availability: {int(p*100)}% ---")
        s1 = data["strategy_1"]
        s2 = data["strategy_2"]
        print(f"Strategy 1 (Send Immediately):")
        print(f"  Generated: {s1['generated']}, Delivered: {s1['delivered']}, Lost: {s1['lost']}, Delivery Ratio: {s1['delivery_ratio']:.2f}%, Mean Delay: {s1['mean_delay_steps']:.2f} steps")
        print(f"Strategy 2 (Store-and-Forward):")
        print(f"  Generated: {s2['generated']}, Delivered: {s2['delivered']}, Delayed: {s2['delayed']}, Lost: {s2['lost']}, Delivery Ratio: {s2['delivery_ratio']:.2f}%, Mean Delay: {s2['mean_delay_steps']:.2f} steps, Max Queue: {s2['max_queue_depth']}")
