"""
Analysis for Q6: Multi-Criteria Decision Analysis (MCDA) for 4 Real Deployments
Compares: SDMA, TDMA, FDMA, CDMA, OFDMA.

Deployments:
  D1: Wide-Area Cellular Voice
  D2: Jam-Resistant Tactical Link
  D3: High-Rate Stadium Downlink
  D4: Network of 5,000 Low-Rate Sensors Sending Small Reports

Criteria (Scores 1-5, higher is better):
  C1: Spectral Efficiency & High Throughput
  C2: Multipath & Frequency-Selective Fading Immunity
  C3: Anti-Jamming, Low Probability of Intercept (LPI) & Interference Robustness
  C4: Scalability for Massive Connection Density & Asynchronous Bursts
  C5: Low Terminal Complexity & Battery/Energy Efficiency
  C6: Mobility & Doppler Resilience
"""

def evaluate_q6_mcda():
    techniques = ["FDMA", "TDMA", "CDMA", "OFDMA", "SDMA"]

    # Base performance scores for each multiple access technique across criteria (1 to 5)
    # Grounded in findings from Q2, Q3, Q4, Q5:
    # FDMA: Low complexity, poor burst efficiency (Q2), narrowband avoids multipath equalization, no anti-jamming
    # TDMA: Good voice trunking (Q2), high time-domain guard/sync overhead (Q2), fair complexity
    # CDMA: High processing gain anti-jamming (Q3), soft capacity, requires strict fast power control (Q3)
    # OFDMA: Highest spectral efficiency & multi-user diversity (Q4), cyclic prefix eliminates ISI, complex PAPR/sync
    # SDMA: Spatial reuse (Q5), narrow beams, high array complexity, fails when users cluster (Q5)
    
    scores = {
        #               C1(SpecEff) C2(Multipath) C3(AntiJam) C4(MassiveConn) C5(Energy/LowComp) C6(Mobility)
        "FDMA":       { "C1": 2.5,  "C2": 2.0,    "C3": 1.5,  "C4": 2.0,      "C5": 4.5,         "C6": 4.0 },
        "TDMA":       { "C1": 3.0,  "C2": 2.5,    "C3": 2.0,  "C4": 2.5,      "C5": 4.0,         "C6": 3.5 },
        "CDMA":       { "C1": 3.0,  "C2": 4.0,    "C3": 5.0,  "C4": 3.5,      "C5": 2.5,         "C6": 4.0 },
        "OFDMA":      { "C1": 5.0,  "C2": 5.0,    "C3": 2.0,  "C4": 4.0,      "C5": 3.0,         "C6": 3.0 },
        "SDMA":       { "C1": 4.5,  "C2": 3.0,    "C3": 3.0,  "C4": 2.5,      "C5": 1.5,         "C6": 2.0 },
    }

    # Deployment specific criterion weightings (sum to 1.0)
    deployment_weights = {
        "D1_WideArea_Voice": {
            "name": "Wide-Area Cellular Voice",
            "weights": { "C1": 0.15, "C2": 0.15, "C3": 0.05, "C4": 0.20, "C5": 0.25, "C6": 0.20 },
            "hybrid_recommendation": "FDMA + TDMA (GSM classic) or CDMA (IS-95)"
        },
        "D2_Tactical_Link": {
            "name": "Jam-Resistant Tactical Link",
            "weights": { "C1": 0.05, "C2": 0.15, "C3": 0.45, "C4": 0.05, "C5": 0.15, "C6": 0.15 },
            "hybrid_recommendation": "CDMA (DSSS/FHSS) + SDMA (Adaptive Null Steering)"
        },
        "D3_Stadium_Downlink": {
            "name": "High-Rate Stadium Downlink",
            "weights": { "C1": 0.35, "C2": 0.25, "C3": 0.05, "C4": 0.20, "C5": 0.05, "C6": 0.10 },
            "hybrid_recommendation": "OFDMA + SDMA (Multi-User Massive MIMO in 5G NR)"
        },
        "D4_5000_Sensors": {
            "name": "5,000 Low-Rate IoT Sensors",
            "weights": { "C1": 0.05, "C2": 0.10, "C3": 0.05, "C4": 0.40, "C5": 0.35, "C6": 0.05 },
            "hybrid_recommendation": "FDMA + Asynchronous CDMA/CSS (LoRaWAN) or SC-FDMA (NB-IoT)"
        }
    }

    results = {}

    for d_key, d_info in deployment_weights.items():
        base_w = d_info["weights"]
        
        # Calculate nominal weighted score
        nominal_scores = {}
        for tech in techniques:
            s = sum(scores[tech][c] * base_w[c] for c in base_w)
            nominal_scores[tech] = round(s, 3)

        # Sensitivity Analysis: Perturb each weight by +20% and -20% (renormalizing)
        rankings_changed = False
        nominal_winner = max(nominal_scores, key=nominal_scores.get)
        sensitivity_log = []

        for c_perturbed in base_w:
            for factor in [1.20, 0.80]:
                perturbed_w = base_w.copy()
                perturbed_w[c_perturbed] *= factor
                total_w = sum(perturbed_w.values())
                # Renormalize
                norm_w = {k: v / total_w for k, v in perturbed_w.items()}
                
                # Re-evaluate
                p_scores = {}
                for tech in techniques:
                    p_scores[tech] = sum(scores[tech][c] * norm_w[c] for c in norm_w)
                p_winner = max(p_scores, key=p_scores.get)
                
                if p_winner != nominal_winner:
                    rankings_changed = True
                    sensitivity_log.append(f"Perturbation {c_perturbed} by {int((factor-1)*100)}% flipped winner from {nominal_winner} to {p_winner}")

        results[d_key] = {
            "name": d_info["name"],
            "nominal_scores": nominal_scores,
            "nominal_winner": nominal_winner,
            "rankings_changed": rankings_changed,
            "sensitivity_log": sensitivity_log,
            "hybrid": d_info["hybrid_recommendation"]
        }

    return results

if __name__ == "__main__":
    res = evaluate_q6_mcda()
    print("="*90)
    print("Q6 MULTI-CRITERIA DECISION ANALYSIS (MCDA) & SENSITIVITY FOR REAL DEPLOYMENTS")
    print("="*90)
    for d_key, d in res.items():
        print(f"\nDeployment: {d['name']}")
        print(f"Nominal Scores: {d['nominal_scores']}")
        print(f"--> Primary Choice: {d['nominal_winner']}")
        print(f"--> Recommended Hybrid: {d['hybrid']}")
        if d["rankings_changed"]:
            print(f"--> Sensitivity Alert: Winner shifted under +/- 20% weight changes!")
            for log in d["sensitivity_log"]:
                print(f"    * {log}")
        else:
            print("--> Sensitivity Check: ROBUST (Winner unchanged across all +/- 20% weight perturbations).")
