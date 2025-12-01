from data_tools import load_signal
from plot_tools import plot_with_sliders_and_baseline
from export_results import export_peak_results
from peak_tools import analyze_signal_with_custom_baseline
import os

# ---------------- CONFIGURATION ----------------
folder = r"C:\Users\Marijus\OneDrive - Vilnius University\3 semestras\cern\Marijus\Marijus_Mozdeikis\20250722_05nJ_06-10um_Spectras"
filename = "20250722_05nJ_08um.xlsx"
column_suffixes = [" P ", " S "]
initial_prominence = 10
initial_distance = 10
output_file = r"C:\Users\Marijus\OneDrive - Vilnius University\3 semestras\cern\Marijus\Marijus_Mozdeikis\results\resonance_properties.xlsx"
# ------------------------------------------------

resonance_properties = []

for suffix in column_suffixes:
    signals = load_signal(folder, filename, suffix, multiple=True)

    for col_name, (wavelengths, signal) in signals.items():
        print(f"\n=== Processing column: {col_name} ===")
        print("Adjust sliders, then close the plot window...")
        
        final_values = plot_with_sliders_and_baseline(wavelengths, signal, 
                                                    initial_prominence, initial_distance, 
                                                    title=col_name)
        
        final_prom = final_values['prominence']
        final_dist = final_values['distance']
        custom_baselines = final_values['baselines']['left_bases']
        
        print(f"\n{'='*60}")
        print("VERIFICATION - Comparing with and without custom baselines:")
        print('='*60)
        
        # 1. Analyze WITH custom baselines
        results_custom = analyze_signal_with_custom_baseline(wavelengths, signal, col_name, 
                                                            final_prom, final_dist, 
                                                            custom_baselines)
        
        # 2. Analyze WITHOUT custom baselines (for comparison)
        results_auto = analyze_signal_with_custom_baseline(wavelengths, signal, col_name, 
                                    final_prom, final_dist)
        
        # Show comparison
        print(f"\nColumn: {col_name}")
        print(f"Settings: prominence={final_prom}, distance={final_dist}")
        print(f"\n{'Peak':<6} {'Wavelength':<12} {'Depth (auto)':<12} {'Depth (custom)':<14} {'ΔDepth':<10}")
        print('-'*60)
        
        for i, (r_auto, r_custom) in enumerate(zip(results_auto, results_custom)):
            delta_depth = r_custom['depth'] - r_auto['depth']
            print(f"{i+1:<6} {r_custom['peak_wl']:<12.2f} {r_auto['depth']:<12.4f} {r_custom['depth']:<14.4f} {delta_depth:>+10.4f}")
        
        print(f"\nQ factors (custom baselines):")
        for i, r in enumerate(results_custom):
            print(f"  Peak {i+1}: Q={r['Q']:.0f}, MQ={r['MQ']:.2f}")
        
        print('='*60)
        
        # Use the CUSTOM results for export
        for r in results_custom:
            r["file"] = filename
            r["column"] = col_name
            resonance_properties.append(r)

export_peak_results(filename, resonance_properties, output_file=output_file)