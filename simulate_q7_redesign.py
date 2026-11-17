"""
Simulation for Q7: Day-4 Design Challenge
Diagnose, Redesign and Validate: Eliminating User Starvation in Channel-Aware OFDMA

Comparison of:
  Original: Greedy Best-Subcarrier Allocation (Max-Sum-Rate)
  Redesigned: Elastic Two-Stage Proportional Fair Scheduler with Guaranteed Quota (E-PFS)
Under 1,000 identical frequency-selective Rayleigh channel realizations (Seed 42).
"""

import math
import random
import cmath

def generate_multipath_channel(N=64, num_taps=4, rng=None):
    tap_powers = [math.exp(-0.5 * l) for l in range(num_taps)]
    norm = math.sqrt(sum(tap_powers))
    tap_gains = []
    for l in range(num_taps):
        sigma = math.sqrt(tap_powers[l]) / norm / math.sqrt(2)
        real = rng.gauss(0, sigma)
        imag = rng.gauss(0, sigma)
        tap_gains.append(complex(real, imag))

    H = []
    for k in range(N):
        h_k = sum(tap_gains[l] * cmath.exp(-2j * math.pi * k * l / N) for l in range(num_taps))
        H.append(abs(h_k) ** 2)
    return H

def jains_fairness(rates):
    n = len(rates)
    sum_r = sum(rates)
    sum_sq = sum(r * r for r in rates)
    if sum_sq == 0:
        return 0.0
    return (sum_r ** 2) / (n * sum_sq)

def run_q7_validation(num_realizations=1000, seed=42):
    rng = random.Random(seed)
    num_users = 8
    num_subcarriers = 64
    user_avg_snr_db = [18.0, 16.0, 15.0, 13.0, 12.0, 11.0, 10.0, 9.0]
    user_avg_snr_lin = [10.0 ** (s / 10.0) for s in user_avg_snr_db]

    # Metrics for Original
    orig_sum_rates = []
    orig_fairness = []
    orig_user_rates_accum = [0.0] * num_users
    orig_starved_count = 0
    orig_min_user_rates = []

    # Metrics for Redesign (E-PFS)
    redesign_sum_rates = []
    redesign_fairness = []
    redesign_user_rates_accum = [0.0] * num_users
    redesign_starved_count = 0
    redesign_min_user_rates = []

    for _ in range(num_realizations):
        # Generate channel SNR matrix
        snr_matrix = []
        for u in range(num_users):
            h_power = generate_multipath_channel(num_subcarriers, num_taps=4, rng=rng)
            snr_matrix.append([user_avg_snr_lin[u] * h_power[k] for k in range(num_subcarriers)])

        # Rate matrix R[u][k]
        rate_matrix = [
            [math.log2(1.0 + snr_matrix[u][k]) for k in range(num_subcarriers)]
            for u in range(num_users)
        ]

        # -------------------------------------------------------------------
        # 1. ORIGINAL: Greedy Best-Subcarrier Allocation
        # -------------------------------------------------------------------
        r_orig = [0.0] * num_users
        orig_assigned_counts = [0] * num_users
        for k in range(num_subcarriers):
            best_u = 0
            best_val = -1.0
            for u in range(num_users):
                if rate_matrix[u][k] > best_val:
                    best_val = rate_matrix[u][k]
                    best_u = u
            r_orig[best_u] += best_val
            orig_assigned_counts[best_u] += 1

        for count in orig_assigned_counts:
            if count == 0:
                orig_starved_count += 1

        orig_sum_rates.append(sum(r_orig))
        orig_fairness.append(jains_fairness(r_orig))
        orig_min_user_rates.append(min(r_orig))
        for u in range(num_users):
            orig_user_rates_accum[u] += r_orig[u]

        # -------------------------------------------------------------------
        # 2. REDESIGNED: Elastic Two-Stage Proportional Fair Scheduler (E-PFS)
        # -------------------------------------------------------------------
        # Stage 1: Guarantee minimum quota of K_min = 4 subcarriers per user.
        # Users select their preferred subcarriers iteratively in round-robin fashion
        # prioritizing users with currently lowest allocated rate to prevent starvation.
        r_redesign = [0.0] * num_users
        redesign_assigned_counts = [0] * num_users
        unallocated_subcarriers = set(range(num_subcarriers))

        K_min = 4
        for round_idx in range(K_min):
            # Sort users by currently accumulated rate (ascending) to give weaker users first pick
            user_order = sorted(range(num_users), key=lambda u: r_redesign[u])
            for u in user_order:
                # User u picks their best remaining subcarrier
                best_k = None
                best_val = -1.0
                for k in unallocated_subcarriers:
                    if rate_matrix[u][k] > best_val:
                        best_val = rate_matrix[u][k]
                        best_k = k
                if best_k is not None:
                    unallocated_subcarriers.remove(best_k)
                    r_redesign[u] += best_val
                    redesign_assigned_counts[u] += 1

        # Stage 2: Opportunistic Elastic Pool (remaining 32 subcarriers)
        # Allocated using Proportional Fair Metric: argmax_u ( R_uk / (T_u + eps) )
        # where T_u is accumulated rate in current frame
        for k in list(unallocated_subcarriers):
            best_u = 0
            best_metric = -1.0
            for u in range(num_users):
                # PF metric: instantaneous rate normalized by current allocation
                metric = rate_matrix[u][k] / max(r_redesign[u], 0.1)
                if metric > best_metric:
                    best_metric = metric
                    best_u = u
            r_redesign[best_u] += rate_matrix[best_u][k]
            redesign_assigned_counts[best_u] += 1

        for count in redesign_assigned_counts:
            if count == 0:
                redesign_starved_count += 1

        redesign_sum_rates.append(sum(r_redesign))
        redesign_fairness.append(jains_fairness(r_redesign))
        redesign_min_user_rates.append(min(r_redesign))
        for u in range(num_users):
            redesign_user_rates_accum[u] += r_redesign[u]

    return {
        "original": {
            "mean_sum_rate": sum(orig_sum_rates) / num_realizations,
            "mean_fairness": sum(orig_fairness) / num_realizations,
            "mean_min_user_rate": sum(orig_min_user_rates) / num_realizations,
            "starved_users_total": orig_starved_count,
            "starved_users_per_frame": orig_starved_count / num_realizations,
            "per_user_mean": [r / num_realizations for r in orig_user_rates_accum]
        },
        "redesigned": {
            "mean_sum_rate": sum(redesign_sum_rates) / num_realizations,
            "mean_fairness": sum(redesign_fairness) / num_realizations,
            "mean_min_user_rate": sum(redesign_min_user_rates) / num_realizations,
            "starved_users_total": redesign_starved_count,
            "starved_users_per_frame": redesign_starved_count / num_realizations,
            "per_user_mean": [r / num_realizations for r in redesign_user_rates_accum]
        }
    }

if __name__ == "__main__":
    res = run_q7_validation()
    orig = res["original"]
    red = res["redesigned"]
    print("="*85)
    print("Q7 DAY-4 CHALLENGE: VALIDATION OF ORIGINAL VS REDESIGNED OFDMA SCHEDULER")
    print("="*85)
    print(f"{'Performance Metric':<35} | {'Original (Greedy)':<20} | {'Redesigned (E-PFS)':<20} | {'Impact / Change':<15}")
    print("-" * 95)
    
    sum_diff = ((red['mean_sum_rate'] - orig['mean_sum_rate']) / orig['mean_sum_rate']) * 100
    print(f"{'Sum Throughput (bps/Hz)':<35} | {orig['mean_sum_rate']:<20.2f} | {red['mean_sum_rate']:<20.2f} | {sum_diff:+.2f}%")
    
    fair_diff = ((red['mean_fairness'] - orig['mean_fairness']) / orig['mean_fairness']) * 100
    print(f"{'Jain Fairness Index':<35} | {orig['mean_fairness']:<20.4f} | {red['mean_fairness']:<20.4f} | {fair_diff:+.2f}%")
    
    if orig['mean_min_user_rate'] > 0:
        min_diff_str = f"{((red['mean_min_user_rate'] - orig['mean_min_user_rate']) / orig['mean_min_user_rate']) * 100:+.2f}%"
    else:
        min_diff_str = f"From 0.00 to {red['mean_min_user_rate']:.2f} (Infinite Gain)"
    print(f"{'Worst-Case User Throughput (bps/Hz)':<35} | {orig['mean_min_user_rate']:<20.2f} | {red['mean_min_user_rate']:<20.2f} | {min_diff_str:<15}")
    
    print(f"{'Starved Users / Frame (0 subcarriers)':<35} | {orig['starved_users_per_frame']:<20.2f} | {red['starved_users_per_frame']:<20.2f} | -100.0% (ELIMINATED)")
    print(f"{'Total Starved User Events (1000 frames)':<35} | {orig['starved_users_total']:<20d} | {red['starved_users_total']:<20d} | -100.0% (ZERO)")

    print("\nPer-User Throughput Comparison (bps/Hz):")
    print(f"{'User':<6} | {'Original (Greedy)':<20} | {'Redesigned (E-PFS)':<20} | {'Change':<15}")
    print("-" * 65)
    for u in range(8):
        o_val = orig['per_user_mean'][u]
        r_val = red['per_user_mean'][u]
        chg = ((r_val - o_val) / o_val) * 100
        print(f"U{u+1:<5} | {o_val:<20.2f} | {r_val:<20.2f} | {chg:+.1f}%")
