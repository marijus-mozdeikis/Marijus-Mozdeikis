from scipy.signal import find_peaks
import numpy as np

def detect_peaks(signal, prominence, distance):
    # Return peak indices + peak properties
    return find_peaks(signal, prominence=prominence, distance=distance)

def calculate_depths(signal, peaks, properties):
    # Compute depth = baseline - peak value using left_bases
    depths = []
    left_bases = properties["left_bases"]

    for p, lb in zip(peaks, left_bases):
        baseline = signal[lb]
        peak_val = signal[p]

        depths.append({
            "peak_index": p,
            "baseline_index": lb,
            "baseline_value": baseline,
            "peak_value": peak_val,
            "depth": baseline - peak_val
        })

    return depths

def calculate_fwhm(signal, wavelengths, peaks, left_bases):
    fwhms = []
    for p, lb in zip(peaks, left_bases):
        half = (signal[lb] + signal[p]) / 2
        left_idx = np.where(signal[:p] <= half)[0][-1] if np.any(signal[:p] <= half) else 0
        right_idx = p + np.where(signal[p:] >= half)[0][0] if np.any(signal[p:] >= half) else p
        fwhms.append({
            "peak_index": p,
            "wl_left": wavelengths[left_idx],
            "wl_right": wavelengths[right_idx],
            "fwhm": wavelengths[right_idx] - wavelengths[left_idx]
        })
    return fwhms

def calculate_q_factors(wavelengths, depths, fwhms):
    """Calculate Q and MQ factors for each peak."""
    q_factors = []
    for d, f in zip(depths, fwhms):
        peak_wl = float(wavelengths[d["peak_index"]])
        fwhm_val = float(f["fwhm"]) if f["fwhm"] is not None else np.nan

        Q = peak_wl / fwhm_val if fwhm_val and fwhm_val != 0 else np.nan
        MQ = Q / 100 * d["depth"] if not np.isnan(Q) else np.nan

        q_factors.append({
            "peak_index": d["peak_index"],
            "Q": Q,
            "MQ": MQ
        })

    return q_factors

def order_peaks_by_wavelength(depths):
    """
    Assign order to peaks based on increasing wavelength.
    Adds 'order' key to each depth dict.
    """
    sorted_depths = sorted(depths, key=lambda d: d["peak_index"])
    for i, d in enumerate(sorted_depths, start=1):
        d["order"] = i  # m=1,2,3...
    return sorted_depths

def analyze_signal(wavelengths, signal, column_name="", prominence=4, distance=10):
    """
    Compute peaks, depths, FWHM, Q, MQ, and assign resonance order.
    Returns a list of dictionaries ready for export.
    """
    # Detect polarization from column name
    polarization = None
    if " P " in column_name:
        polarization = "P"
    elif " S " in column_name:
        polarization = "S"
    
    peaks, props = detect_peaks(signal, prominence, distance)
    depths = calculate_depths(signal, peaks, props)
    depths = order_peaks_by_wavelength(depths, polarization)
    fwhms = calculate_fwhm(signal, wavelengths, peaks, props["left_bases"])
    q_factors = calculate_q_factors(wavelengths, depths, fwhms)
    
    results = []
    for d, f, q in zip(depths, fwhms, q_factors):
        results.append({
            "resonance_order": d["order"],  # m=-1, +1, +2... or m=1,2,3...
            # REMOVE THIS LINE: "peak_index": d["peak_index"],
            "peak_wl": float(wavelengths[d["peak_index"]]),
            "depth": abs(float(d["depth"])),
            "fwhm": float(f["fwhm"]),
            "Q": float(q["Q"]),
            "MQ": float(q["MQ"])
        })
    return results

def order_peaks_by_wavelength(depths, polarization=None):
    """
    Assign order to peaks based on increasing wavelength and polarization.
    P polarization: m = -1, +1, +2, +3...
    S polarization: m = 1, 2, 3...
    
    Args:
        depths: List of depth dictionaries
        polarization: 'P' or 'S' (from column name)
    
    Returns:
        Sorted depths with 'order' key added
    """
    # Sort by wavelength (increasing peak_index)
    sorted_depths = sorted(depths, key=lambda d: d["peak_index"])
    
    # Assign order based on polarization
    if polarization and polarization.upper() == 'P':
        # P polarization: m = -1, +1, +2, +3...
        for i, d in enumerate(sorted_depths):
            if i == 0:
                d["order"] = -1  # First resonance is m=-1
            else:
                d["order"] = i   # m=+1, +2, +3... (i starts at 1 for 2nd peak)
    else:
        # S polarization or unknown: m = 1, 2, 3...
        for i, d in enumerate(sorted_depths, start=1):
            d["order"] = i
    
    return sorted_depths

def analyze_signal_with_custom_baseline(wavelengths, signal, column_name="", prominence=4, distance=10, custom_left_bases=None):
    """
    Same as analyze_signal but with manually adjusted baselines.
    custom_left_bases: list of baseline indices (one per peak)
    """
    # Detect polarization from column name
    polarization = None
    if " P " in column_name:
        polarization = "P"
    elif " S " in column_name:
        polarization = "S"
    
    peaks, props = detect_peaks(signal, prominence, distance)
    
    # Use custom baselines if provided
    if custom_left_bases is not None and len(custom_left_bases) == len(peaks):
        props["left_bases"] = np.array(custom_left_bases)
    
    depths = calculate_depths(signal, peaks, props)
    depths = order_peaks_by_wavelength(depths, polarization)
    fwhms = calculate_fwhm(signal, wavelengths, peaks, props["left_bases"])
    q_factors = calculate_q_factors(wavelengths, depths, fwhms)
    
    results = []
    for d, f, q in zip(depths, fwhms, q_factors):
        results.append({
            "resonance_order": d["order"],
            "peak_wl": float(wavelengths[d["peak_index"]]),
            "depth": abs(float(d["depth"])),
            "fwhm": float(f["fwhm"]),
            "Q": float(q["Q"]),
            "MQ": float(q["MQ"])
        })
    return results
