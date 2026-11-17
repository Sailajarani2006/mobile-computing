"""
Simulation for Q4: OFDMA - Giving Each User the Subcarriers They Can Use Best
Problem Context: Lecture-Hall Downlink (8 users, 64 subcarriers)

Includes:
1. Numerical verification of subcarrier orthogonality via discrete inner products.
2. Frequency-selective Rayleigh multipath channel generation (1000 realizations).
3. Three Allocation Schemes:
   - Scheme 1: Fixed Contiguous Blocks (8 subcarriers per user)
   - Scheme 2: Interleaved Round-Robin (8 subcarriers spread evenly across band)
   - Scheme 3: Channel-Aware Best-Subcarrier (Greedy Max-SNR)
4. Evaluation of:
   - Sum throughput (bps/Hz)
   - Per-user throughput distribution
   - Jain's Fairness Index
   - Starvation rate (users receiving 0 subcarriers or below min threshold)
"""

import math
import random
import cmath

def verify_orthogonality(N=64, test_subcarriers=[3, 7, 12, 19]):
    """
    Numerically computes inner product of complex exponential subcarriers over N samples:
    <phi_k, phi_m> = (1/N) * sum_{n=0}^{N-1} exp(j*2*pi*k*n/N) * exp(-j*2*pi*m*n/N)
    """
    ortho_matrix = {}
    for k in test_subcarriers:
        for m in test_subcarriers:
            inner_prod = sum(
                cmath.exp(2j * math.pi * k * n / N) * cmath.exp(-2j * math.pi * m * n / N)
                for n in range(N)
            ) / N
            ortho_matrix[(k, m)] = (inner_prod.real, inner_prod.imag, abs(inner_prod))
    return ortho_matrix

def generate_multipath_channel(N=64, num_taps=4, rng=None):
    """
    Generates frequency response for N subcarriers from a Rayleigh fading multipath channel
    with exponential power delay profile.
    """
    # Tap powers normalize to 1.0
    tap_powers = [math.exp(-0.5 * l) for l in range(num_taps)]
    norm = math.sqrt(sum(tap_powers))
    tap_gains = []
    for l in range(num_taps):
        sigma = math.sqrt(tap_powers[l]) / norm / math.sqrt(2)
        real = rng.gauss(0, sigma)
        imag = rng.gauss(0, sigma)
        tap_gains.append(complex(real, imag))

    # FFT to get H[k] on all 64 subcarriers
    H = []
    for k in range(N):
        h_k = sum(tap_gains[l] * cmath.exp(-2j * math.pi * k * l / N) for l in range(num_taps))
        H.append(abs(h_k) ** 2) # Channel power gain |H_k|^2
    return H

def jains_fairness(rates):
    n = len(rates)
    sum_r = sum(rates)
    sum_sq = sum(r * r for r in rates)
    if sum_sq == 0:
        return 0.0
    return (sum_r ** 2) / (n * sum_sq)

def simulate_ofdma(num_realizations=1000, seed=42):
    rng = random.Random(seed)
    num_users = 8
    num_subcarriers = 64
    
    # Average SNR for users: let's model a realistic lecture hall where users have slight
    # distance differences: average SNR from 10 dB to 18 dB (linear 10 to 63)
    user_avg_snr_db = [18.0, 16.0, 15.0, 13.0, 12.0, 11.0, 10.0, 9.0]
    user_avg_snr_lin = [10.0 ** (s / 10.0) for s in user_avg_snr_db]

    sum_rates_contiguous = []
    sum_rates_interleaved = []
    sum_rates_best = []

    fairness_contiguous = []
    fairness_interleaved = []
    fairness_best = []

    user_rates_contiguous_accum = [0.0] * num_users
    user_rates_interleaved_accum = [0.0] * num_users
    user_rates_best_accum = [0.0] * num_users

    starved_users_best = 0 # users getting 0 subcarriers in a frame

    for _ in range(num_realizations):
        # Generate H[u][k] for all 8 users
        gains = []
        snr_matrix = [] # snr_matrix[u][k]
        for u in range(num_users):
            h_power = generate_multipath_channel(num_subcarriers, num_taps=4, rng=rng)
            gains.append(h_power)
            snr_matrix.append([user_avg_snr_lin[u] * h_power[k] for k in range(num_subcarriers)])

        # Scheme 1: Fixed Contiguous Blocks (8 per user: u gets [8u, 8u+7])
        r_cont = [0.0] * num_users
        for u in range(num_users):
            for k in range(u * 8, (u + 1) * 8):
                r_cont[u] += math.log2(1.0 + snr_matrix[u][k])
        sum_rates_contiguous.append(sum(r_cont))
        fairness_contiguous.append(jains_fairness(r_cont))
        for u in range(num_users):
            user_rates_contiguous_accum[u] += r_cont[u]

        # Scheme 2: Interleaved Round-Robin (u gets u, u+8, u+16, ...)
        r_inter = [0.0] * num_users
        for u in range(num_users):
            for k in range(u, num_subcarriers, 8):
                r_inter[u] += math.log2(1.0 + snr_matrix[u][k])
        sum_rates_interleaved.append(sum(r_inter))
        fairness_interleaved.append(jains_fairness(r_inter))
        for u in range(num_users):
            user_rates_interleaved_accum[u] += r_inter[u]

        # Scheme 3: Best Subcarrier (Greedy opportunistic: k assigned to argmax_u rate)
        r_best = [0.0] * num_users
        subcarriers_assigned_count = [0] * num_users
        for k in range(num_subcarriers):
            best_u = 0
            best_val = -1.0
            for u in range(num_users):
                rate_uk = math.log2(1.0 + snr_matrix[u][k])
                if rate_uk > best_val:
                    best_val = rate_uk
                    best_u = u
            r_best[best_u] += best_val
            subcarriers_assigned_count[best_u] += 1

        for count in subcarriers_assigned_count:
            if count == 0:
                starved_users_best += 1

        sum_rates_best.append(sum(r_best))
        fairness_best.append(jains_fairness(r_best))
        for u in range(num_users):
            user_rates_best_accum[u] += r_best[u]

    # Averages
    mean_user_cont = [r / num_realizations for r in user_rates_contiguous_accum]
    mean_user_inter = [r / num_realizations for r in user_rates_interleaved_accum]
    mean_user_best = [r / num_realizations for r in user_rates_best_accum]

    return {
        "orthogonality": verify_orthogonality(64, [2, 5, 11, 23]),
        "mean_sum_contiguous": sum(sum_rates_contiguous) / num_realizations,
        "mean_sum_interleaved": sum(sum_rates_interleaved) / num_realizations,
        "mean_sum_best": sum(sum_rates_best) / num_realizations,
        "mean_fairness_contiguous": sum(fairness_contiguous) / num_realizations,
        "mean_fairness_interleaved": sum(fairness_interleaved) / num_realizations,
        "mean_fairness_best": sum(fairness_best) / num_realizations,
        "per_user_contiguous": mean_user_cont,
        "per_user_interleaved": mean_user_inter,
        "per_user_best": mean_user_best,
        "starved_users_count_total": starved_users_best,
        "starved_users_per_frame": starved_users_best / num_realizations
    }

if __name__ == "__main__":
    res = simulate_ofdma()
    print("="*85)
    print("Q4 NUMERICAL ORTHOGONALITY VERIFICATION (Discrete Inner Product of Subcarriers)")
    print("="*85)
    for (k, m), (re, im, mag) in res["orthogonality"].items():
        if k <= m:
            status = "ORTHOGONAL (Delta=0)" if k != m else "SELF-NORMALIZED (Delta=1.0)"
            print(f"Subcarrier pair ({k:2d}, {m:2d}): Inner Product = {re:+.4e} + {im:+.4e}j | Magnitude = {mag:.4e} -> {status}")

    print("\n" + "="*85)
    print("Q4 SIMULATION RESULTS: 8 USERS, 64 SUBCARRIERS, 1000 CHANNEL REALIZATIONS")
    print("="*85)
    print(f"{'Scheme':<28} | {'Sum Throughput (bps/Hz)':<24} | {'Jain Fairness Index':<20}")
    print("-" * 85)
    print(f"{'1. Fixed Contiguous':<28} | {res['mean_sum_contiguous']:<24.2f} | {res['mean_fairness_contiguous']:<20.4f}")
    print(f"{'2. Interleaved Round-Robin':<28} | {res['mean_sum_interleaved']:<24.2f} | {res['mean_fairness_interleaved']:<20.4f}")
    print(f"{'3. Channel-Aware Best-Subcarrier':<28} | {res['mean_sum_best']:<24.2f} | {res['mean_fairness_best']:<20.4f}")
    print(f"\nStarvation Metric under Best-Subcarrier:")
    print(f"  Total starved user events (0 subcarriers in frame): {res['starved_users_count_total']} / {1000 * 8} user-frames ({res['starved_users_per_frame']:.2f} users starved per frame)")

    print("\nPer-User Mean Throughput (bps/Hz):")
    print(f"{'User':<6} | {'Contiguous':<14} | {'Interleaved':<14} | {'Best-Subcarrier':<16}")
    print("-" * 55)
    for u in range(8):
        print(f"U{u+1:<5} | {res['per_user_contiguous'][u]:<14.2f} | {res['per_user_interleaved'][u]:<14.2f} | {res['per_user_best'][u]:<16.2f}")
