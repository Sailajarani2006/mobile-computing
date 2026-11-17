"""
Simulation for Q3: CDMA - Orthogonality, Spreading and the Near-Far Problem
Problem Context: Crowded Stadium Uplink

Simulates:
1. Spreading with binary phase chips (+1, -1).
2. Code lengths: L in [8, 16, 64].
3. Code types / conditions:
   (i) Synchronous Walsh-Hadamard codes (all equal power, perfect synchrony).
   (ii) Random pseudo-noise bipolar codes (equal power).
   (iii) Random pseudo-noise codes with User 1 at 10x power (+10 dB Near-Far).
   (iv) Asynchronous Walsh codes (random chip delay with consecutive bit transitions,
        exposing non-zero partial cross-correlation) with User 1 at 10x power.
4. Records Bit Error Rate (BER), cross-correlations, and processing gain.
"""

import random
import math

def generate_walsh_matrix(L):
    """Generates LxL Walsh-Hadamard matrix using Sylvester's construction."""
    matrix = [[1]]
    while len(matrix) < L:
        next_matrix = []
        for row in matrix:
            next_matrix.append(row + row)
        for row in matrix:
            next_matrix.append(row + [-x for x in row])
        matrix = next_matrix
    return matrix

def generate_random_code(L, rng):
    return [1 if rng.random() > 0.5 else -1 for _ in range(L)]

def simulate_cdma(L, num_bits=10000, seed=42):
    rng = random.Random(seed)
    walsh_matrix = generate_walsh_matrix(L)
    
    if L == 8:
        user_counts = [2, 4, 6, 8]
    elif L == 16:
        user_counts = [2, 4, 8, 12, 16]
    else: # 64
        user_counts = [2, 8, 16, 32, 48, 64]

    results = {
        "L": L,
        "processing_gain_linear": L,
        "processing_gain_dB": 10.0 * math.log10(L),
        "tests": {}
    }

    # Background thermal noise (AWGN) with SNR = 15 dB
    snr_linear = 10.0 ** (15.0 / 10.0)
    chip_noise_sigma = math.sqrt(1.0 / snr_linear)
    despread_noise_sigma = chip_noise_sigma / math.sqrt(L)

    for K in user_counts:
        # Precompute random codes
        rand_codes = [generate_random_code(L, rng) for _ in range(K)]
        rho_rand = [
            sum(rand_codes[u][c] * rand_codes[0][c] for c in range(L)) / L
            for u in range(K)
        ]

        # For asynchronous Walsh, pick an arbitrary user as target, e.g. user 1
        target_walsh_idx = 1 if L > 1 else 0
        target_walsh_code = walsh_matrix[target_walsh_idx]
        
        # User timing delays in chips
        delays = [0] + [rng.randint(1, L - 1) for _ in range(K - 1)]

        # Precompute partial cross-correlation components for async Walsh
        # In asynchronous transmission:
        # received chips during target bit interval =
        # prev_bit * code_u[L - tau : L] concatenated with curr_bit * code_u[0 : L - tau]
        # So correlation = prev_bit * R_prev + curr_bit * R_curr
        async_walsh_R_prev = [0.0] * K
        async_walsh_R_curr = [0.0] * K
        for u in range(K):
            if u == 0:
                continue
            tau = delays[u]
            u_code = walsh_matrix[(target_walsh_idx + u) % L]
            # chips from prev bit occupy first tau chips of target interval
            r_prev = sum(u_code[L - tau + c] * target_walsh_code[c] for c in range(tau)) / L
            # chips from curr bit occupy remaining L - tau chips
            r_curr = sum(u_code[c - tau] * target_walsh_code[c] for c in range(tau, L)) / L
            async_walsh_R_prev[u] = r_prev
            async_walsh_R_curr[u] = r_curr

        # Track errors
        errors_walsh_sync = 0
        errors_rand_equal = 0
        errors_rand_10x = 0
        errors_walsh_async_10x = 0

        amp_equal = [1.0] * K
        amp_10x = [1.0] * K
        amp_10x[1] = math.sqrt(10.0) # User 1 at 10x power

        # State for consecutive bits for async users
        prev_bits_async = [1 if rng.random() > 0.5 else -1 for _ in range(K)]

        for _ in range(num_bits):
            b0 = 1 if rng.random() > 0.5 else -1
            other_bits = [1 if rng.random() > 0.5 else -1 for _ in range(K - 1)]
            n_sample = rng.gauss(0, despread_noise_sigma)

            # (i) Sync Walsh (b0 + noise) - Zero MAI
            y_walsh = b0 + n_sample
            if (1 if y_walsh >= 0 else -1) != b0:
                errors_walsh_sync += 1

            # (ii) Random Codes (Equal Power)
            mai_rand = sum(amp_equal[u] * other_bits[u - 1] * rho_rand[u] for u in range(1, K))
            y_rand_equal = b0 + mai_rand + n_sample
            if (1 if y_rand_equal >= 0 else -1) != b0:
                errors_rand_equal += 1

            # (iii-A) Random Codes (User 1 at 10x Power)
            mai_rand_10x = sum(amp_10x[u] * other_bits[u - 1] * rho_rand[u] for u in range(1, K))
            y_rand_10x = b0 + mai_rand_10x + n_sample
            if (1 if y_rand_10x >= 0 else -1) != b0:
                errors_rand_10x += 1

            # (iii-B) Async Walsh (User 1 at 10x Power with partial correlations)
            curr_bits_async = [b0] + other_bits
            mai_walsh_async = sum(
                amp_10x[u] * (prev_bits_async[u] * async_walsh_R_prev[u] + curr_bits_async[u] * async_walsh_R_curr[u])
                for u in range(1, K)
            )
            y_walsh_async = b0 + mai_walsh_async + n_sample
            if (1 if y_walsh_async >= 0 else -1) != b0:
                errors_walsh_async_10x += 1
            prev_bits_async = curr_bits_async

        results["tests"][K] = {
            "BER_walsh_sync": errors_walsh_sync / num_bits,
            "BER_random_equal": errors_rand_equal / num_bits,
            "BER_random_near_far_10x": errors_rand_10x / num_bits,
            "BER_walsh_async_near_far_10x": errors_walsh_async_10x / num_bits
        }

    # Sample cross-correlation stats
    rand_samples = [generate_random_code(L, rng) for _ in range(8)]
    rand_cc = [
        abs(sum(rand_samples[i][c] * rand_samples[j][c] for c in range(L)) / L)
        for i in range(8) for j in range(i + 1, 8)
    ]
    results["avg_random_cross_corr"] = sum(rand_cc) / len(rand_cc)
    results["avg_walsh_sync_cross_corr"] = 0.0

    return results

def run_q3():
    all_results = {}
    for L in [8, 16, 64]:
        all_results[L] = simulate_cdma(L, num_bits=10000, seed=42)
    return all_results

if __name__ == "__main__":
    res = run_q3()
    print("="*95)
    print("Q3 SIMULATION RESULTS: DS-CDMA PERFORMANCE UNDER ORTHOGONAL & NEAR-FAR CONDITIONS")
    print("="*95)
    for L, data in res.items():
        print(f"\n================ Code Length L = {L} (Processing Gain = {data['processing_gain_dB']:.2f} dB) ================")
        print(f"Sync Walsh Avg Cross-Corr: {data['avg_walsh_sync_cross_corr']:.4f} | Random Avg Cross-Corr: {data['avg_random_cross_corr']:.4f}")
        print(f"{'Users (K)':<10} | {'Sync Walsh BER':<16} | {'Random Equal BER':<18} | {'Rand 10x Near-Far':<18} | {'Async Walsh 10x NF':<18}")
        print("-" * 95)
        for K, t in data["tests"].items():
            print(f"{K:<10} | {t['BER_walsh_sync']:<16.5f} | {t['BER_random_equal']:<18.5f} | {t['BER_random_near_far_10x']:<18.5f} | {t['BER_walsh_async_near_far_10x']:<18.5f}")
