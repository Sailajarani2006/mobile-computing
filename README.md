# Mobile Computing (CO2) – Simulation & Research Suite
## Course: ITA03-MP Mobile Computing — Assignment 2

This repository contains the complete simulation models, mathematical derivations, empirical validation results, and engineering redesign for Mobile Telecommunications, Multiple Access Schemes (FDMA, TDMA, CDMA, OFDMA, SDMA), and Mobile Computing Architectures.

---

## 📂 Repository Contents

| File | Question / Topic | Description |
| :--- | :--- | :--- |
| **[`run_all.py`](run_all.py)** | Master Test Suite | Executes all Q1–Q7 simulations end-to-end and outputs formatted logs. |
| **[`simulate_q1_mobility.py`](simulate_q1_mobility.py)** | Q1: Mobile Computing vs Comm | Simulates offline meter reading under 90%, 60%, 30% Markov link fading. |
| **[`simulate_q2_fdma_tdma.py`](simulate_q2_fdma_tdma.py)** | Q2: FDMA vs TDMA Channel Sharing | Simulates continuous voice, bursty data, mixed, and alarm cascade traffic. |
| **[`simulate_q3_cdma.py`](simulate_q3_cdma.py)** | Q3: DS-CDMA Uplink & Near-Far | Walsh vs Random codes with partial cross-correlation & power imbalance. |
| **[`simulate_q4_ofdma.py`](simulate_q4_ofdma.py)** | Q4: OFDMA Subcarrier Allocation | Inner product orthogonality, 64-subcarrier Rayleigh fading, and starvation. |
| **[`simulate_q5_sdma.py`](simulate_q5_sdma.py)** | Q5: SDMA Beamforming | Uniform Linear Array (ULA) array factor, HPBW, SLL, and SIR evaluation. |
| **[`simulate_q6_mcda.py`](simulate_q6_mcda.py)** | Q6: Real Deployments Selection | Multi-Criteria Decision Analysis (MCDA) across 4 deployments with ±20% sensitivity. |
| **[`simulate_q7_redesign.py`](simulate_q7_redesign.py)** | Q7: Day-4 Design Challenge | Elastic Proportional Fair Scheduler (E-PFS) eliminating user starvation. |
| **[`REPORT.md`](REPORT.md)** | Full Academic Report | Detailed theoretical proofs, analytical questions, and design decisions. |

---

## 🚀 Quick Start & Execution

All scripts are written in **pure Python 3 (standard library only)**. No external packages (`numpy`, `scipy`, etc.) are needed.

### Run All Simulations
```powershell
python run_all.py
```

### Run Any Specific Question
```powershell
python simulate_q1_mobility.py
python simulate_q2_fdma_tdma.py
python simulate_q3_cdma.py
python simulate_q4_ofdma.py
python simulate_q5_sdma.py
python simulate_q6_mcda.py
python simulate_q7_redesign.py
```

---

## 📊 Summary of Experimental Results

### Q1: Disconnected Operation (Store-and-Forward vs Immediate Send)
* At **30% link availability**, Immediate Send drops **69.83%** of updates.
* Store-and-Forward achieves **100.00% delivery** with a mean delay of $9.69$ time steps.

### Q2: FDMA (76 ch) vs TDMA (70 ch) Under Bursty Traffic
* Under continuous voice, FDMA achieves lower blocking ($1.16\%$ vs $4.10\%$) due to TDMA's guard/sync bit overhead ($29.85\%$).
* Under **10% bursty data**, both schemes suffer severe capacity waste ($>92\%$), proving that dedicated channel allocation is unjustified for campus telemetry.

### Q3: CDMA Near-Far & Code Orthogonality
* Synchronous Walsh codes yield $\text{BER} = 0.0000$ up to $K = L$.
* In an **asynchronous uplink**, partial cross-correlations across bit boundaries reach $0.5$. When one user transmits at 10x power (+10 dB), weaker users experience severe bit errors without fast power control ($1500\text{ Hz}$).

### Q4: OFDMA Starvation
* Greedy Best-Subcarrier boosts total sum rate to $398.50 \text{ bps/Hz}$ (+64% multi-user diversity gain), but **starves 4.27 out of 8 users per frame**, dropping Jain's fairness to $0.3073$.

### Q5: SDMA Beamforming (Uniform Linear Array)
* For $N=16$ elements, $\text{HPBW} = 6.4^\circ$, and minimum angular separation meeting the $10\text{ dB}$ SIR threshold is **$5.3^\circ$**. At a highway toll plaza with vehicles arriving in parallel lanes ($\Delta\theta < 2^\circ$), SDMA fails.

### Q6: Multi-Criteria Deployment Selection
* **Wide-Area Voice**: OFDMA / Hybrid FDMA+TDMA (GSM).
* **Tactical Link**: CDMA (DSSS/FHSS) + SDMA (Adaptive Nulling).
* **Stadium Downlink**: OFDMA + SDMA (5G Massive MIMO).
* **5,000 Low-Rate Sensors**: OFDMA / Hybrid FDMA+CSS (LoRaWAN).

### Q7: Day-4 Challenge (E-PFS Fair Scheduler)
* **Starved Users / Frame**: Reduced from **$4.27$ to $0.00$ (100% eliminated)**.
* **Jain's Fairness Index**: Increased from **$0.3073$ to $0.9273$ (+201.8%)**.
* **Worst-Case User Throughput**: Increased from **$0.00$ to $23.92\text{ bps/Hz}$**.
* **Aggregate Sum Rate**: Maintained at **$317.68\text{ bps/Hz}$** (+31% higher than static contiguous/interleaved schemes).
