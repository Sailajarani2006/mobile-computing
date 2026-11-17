import math
area,R,S,N=12.0,0.5,336,7
cell_area=(3*math.sqrt(3)/2)*R**2
traffic_per_user=0.025
print("TASK 11 - RECOMMENDED TOWNSHIP NETWORK DESIGN")
print(f"Township area                  : {area:.1f} km^2")
print(f"Macrocell radius               : {R:.2f} km")
print(f"Geometric minimum cells        : {math.ceil(area/cell_area)}")
print("Working site allowance         : 22 macro sites (planning estimate)")
print(f"Reuse cluster size             : N={N}")
print(f"Nominal channels per cell      : {S//N}")
print(f"Reuse ratio                    : {math.sqrt(3*N):.3f}")
print(f"Reuse distance                 : {R*math.sqrt(3*N):.3f} km")
print(f"SIR for n=4                    : {10*math.log10((3*N)**2/6):.2f} dB")
print("\nRecommendation:")
print("- Seven-cell macro reuse foundation.")
print("- Three-sector antennas at high-load macro sites.")
print("- Selective microcells at measured hotspots.")
print("- Maintain blocking <=2%; validate with drive tests and traffic data.")
print("\n100,000 users ->", f"{100000*traffic_per_user:.1f} Erlangs busy-hour offered traffic.")
