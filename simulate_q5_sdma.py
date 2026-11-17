"""
Simulation for Q5: SDMA - Reusing the Same Channel in Different Directions
Problem Context: Highway Cell With Directional Antennas

Derives and evaluates:
1. Array Factor for Uniform Linear Array (ULA):
   AF(theta) = (1/N) * sin(N * pi * sin(theta) / 2) / sin(pi * sin(theta) / 2)
2. Main-lobe width (HPBW, FNBW) and Peak Side-Lobe Level (SLL) for N = 2, 4, 8, 16.
3. SIR evaluated at User B when steered at User A (theta_A = 0 deg)
   for angular separations: 5 deg to 60 deg.
4. Determines minimum angular separation meeting SIR threshold = 10 dB.
"""

import math

def array_factor(theta_deg, N):
    """
    Computes normalized array factor AF(theta) and power pattern |AF(theta)|^2
    for broadside ULA with d = lambda / 2.
    """
    theta_rad = math.radians(theta_deg)
    psi = math.pi * math.sin(theta_rad)
    
    if abs(psi) < 1e-9:
        return 1.0, 1.0, 0.0 # On-axis peak = 1 (0 dB)
    
    denom = math.sin(psi / 2.0)
    if abs(denom) < 1e-9:
        return 1.0, 1.0, 0.0
    
    num = math.sin(N * psi / 2.0)
    af = num / (N * denom)
    power = af * af
    power_db = 10.0 * math.log10(max(power, 1e-12))
    return af, power, power_db

def compute_beamwidth_and_sll(N):
    # Scan from 0.01 deg to 90 deg in fine steps
    step = 0.05
    angles = [i * step for i in range(1, int(90.0 / step) + 1)]
    
    # 1. HPBW (-3 dB point)
    hpbw = None
    for ang in angles:
        _, p, pdb = array_factor(ang, N)
        if pdb <= -3.0103: # Half-power
            hpbw = 2.0 * ang
            break
            
    # 2. First Null Beamwidth (FNBW)
    fnbw = None
    prev_af = 1.0
    first_null_angle = None
    for ang in angles:
        af, _, _ = array_factor(ang, N)
        if prev_af > 0 and af <= 0: # Zero crossing
            first_null_angle = ang
            fnbw = 2.0 * ang
            break
        prev_af = af

    # 3. Peak Side-Lobe Level (SLL)
    # Search after the first null
    peak_sll_db = -999.0
    if first_null_angle:
        for ang in angles:
            if ang > first_null_angle:
                _, _, pdb = array_factor(ang, N)
                if pdb > peak_sll_db:
                    peak_sll_db = pdb
                # If we passed the first side lobe and it starts decreasing again
                if peak_sll_db > -999.0 and pdb < peak_sll_db - 1.0:
                    break

    return {
        "HPBW_deg": hpbw,
        "FNBW_deg": fnbw,
        "peak_SLL_dB": peak_sll_db if peak_sll_db > -999.0 else None
    }

def evaluate_sir(N_values=[2, 4, 8, 16], separations=[5, 10, 15, 20, 30, 45, 60], sir_threshold_db=10.0):
    results = {}
    
    for N in N_values:
        props = compute_beamwidth_and_sll(N)
        sir_by_sep = {}
        min_sep_meeting_threshold = None
        
        # Check standard angles
        for sep in separations:
            _, p_b, pdb_b = array_factor(sep, N)
            sir_db = -pdb_b # Since P_A = 0 dB, SIR = P_A - P_B = -P_B(dB)
            sir_by_sep[sep] = sir_db
            
        # Find exact minimum separation meeting threshold in 0.1 deg increments
        for sep_fine in [i * 0.1 for i in range(10, 900)]:
            _, _, pdb = array_factor(sep_fine, N)
            sir = -pdb
            if sir >= sir_threshold_db:
                min_sep_meeting_threshold = sep_fine
                break
                
        results[N] = {
            "properties": props,
            "sir_by_sep": sir_by_sep,
            "min_sep_for_threshold": min_sep_meeting_threshold
        }
    return results

if __name__ == "__main__":
    res = evaluate_sir()
    print("="*85)
    print("Q5 SDMA BEAM PATTERN & SIR ANALYSIS (ULA, d = lambda/2, Steering at Broadside)")
    print("="*85)
    print(f"{'N':<4} | {'HPBW (deg)':<12} | {'FNBW (deg)':<12} | {'Peak SLL (dB)':<14} | {'Min Sep (SIR >= 10dB)':<22}")
    print("-" * 85)
    for N, d in res.items():
        p = d["properties"]
        hpbw_str = f"{p['HPBW_deg']:.1f}" if p['HPBW_deg'] else "N/A"
        fnbw_str = f"{p['FNBW_deg']:.1f}" if p['FNBW_deg'] else "N/A"
        sll_str = f"{p['peak_SLL_dB']:.2f}" if p['peak_SLL_dB'] else "None (N=2)"
        min_sep = f"{d['min_sep_for_threshold']:.1f} deg" if d['min_sep_for_threshold'] else "> 90 deg"
        print(f"{N:<4} | {hpbw_str:<12} | {fnbw_str:<12} | {sll_str:<14} | {min_sep:<22}")

    print("\n" + "="*85)
    print("SIR (dB) AT USER B FOR ANGULAR SEPARATIONS (5 deg to 60 deg)")
    print("="*85)
    seps = [5, 10, 15, 20, 30, 45, 60]
    header = f"{'N':<4} | " + " | ".join([f"{str(s) + ' deg':<8}" for s in seps])
    print(header)
    print("-" * 85)
    for N, d in res.items():
        row = f"{N:<4} | "
        vals = []
        for s in seps:
            sir = d["sir_by_sep"][s]
            vals.append(f"{sir:>7.2f}")
        row += " | ".join(vals)
        print(row)
