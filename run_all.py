"""
Master Simulation Runner for Mobile Computing Assignment 2 (CO2)
Runs all simulation modules for Q1 to Q7:
  - simulate_q1_mobility.py
  - simulate_q2_fdma_tdma.py
  - simulate_q3_cdma.py
  - simulate_q4_ofdma.py
  - simulate_q5_sdma.py
  - simulate_q6_mcda.py
  - simulate_q7_redesign.py

Outputs a comprehensive, unified experimental log.
"""

import sys
import os
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulate_q1_mobility import run_q1_simulation
from simulate_q2_fdma_tdma import run_q2
from simulate_q3_cdma import run_q3
from simulate_q4_ofdma import simulate_ofdma
from simulate_q5_sdma import evaluate_sir
from simulate_q6_mcda import evaluate_q6_mcda
from simulate_q7_redesign import run_q7_validation

def main():
    print("="*95)
    print("STARTING COMPLETE SIMULATION SUITE FOR MOBILE COMPUTING ASSIGNMENT 2 (CO2)")
    print("="*95)

    print("\n[1/7] Running Q1: Mobility & Connection Disconnection Simulation...")
    q1_res = run_q1_simulation()
    print("  -> Q1 Complete.")

    print("\n[2/7] Running Q2: FDMA vs TDMA Channel Sharing Under 4 Traffic Datasets...")
    q2_res = run_q2()
    print("  -> Q2 Complete.")

    print("\n[3/7] Running Q3: DS-CDMA Orthogonality, Spreading & Near-Far Simulation...")
    q3_res = run_q3()
    print("  -> Q3 Complete.")

    print("\n[4/7] Running Q4: OFDMA 64-Subcarrier Rayleigh Multipath Allocation...")
    q4_res = simulate_ofdma()
    print("  -> Q4 Complete.")

    print("\n[5/7] Running Q5: SDMA ULA Beamforming & SIR Separation Evaluation...")
    q5_res = evaluate_sir()
    print("  -> Q5 Complete.")

    print("\n[6/7] Running Q6: MCDA Multi-Criteria Evaluation & Sensitivity Analysis...")
    q6_res = evaluate_q6_mcda()
    print("  -> Q6 Complete.")

    print("\n[7/7] Running Q7: Day-4 Design Challenge (Original vs Redesigned Scheduler)...")
    q7_res = run_q7_validation()
    print("  -> Q7 Complete.")

    print("\n" + "="*95)
    print("ALL SIMULATION MODULES EXECUTED SUCCESSFULLY!")
    print("="*95)

if __name__ == "__main__":
    main()
