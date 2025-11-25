import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from peak_tools import detect_peaks, calculate_depths, calculate_fwhm

def plot_with_sliders(wavelengths, signal, init_prom=4, init_dist=10, title="Signal"):
    """Interactive plot with peak detection and adjustable sliders."""

    # --- Initial peak detection ---
    peaks, props = detect_peaks(signal, init_prom, init_dist)

    # --- Figure layout ---
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title(title)
    plt.subplots_adjust(bottom=0.25)

    # --- Main plot ---
    ax.plot(wavelengths, signal, label="Signal")

    sc_peaks = ax.scatter(wavelengths[peaks], signal[peaks], s=50, color="red", label="Peaks")
    sc_base = ax.scatter(wavelengths[props["left_bases"]], signal[props["left_bases"]], s=40, color="green", label="Left Baseline")

    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Reflection (inverted)")
    ax.legend()

    # --- Slider axes ---
    ax_prom = plt.axes([0.25, 0.10, 0.65, 0.03])
    ax_dist = plt.axes([0.25, 0.15, 0.65, 0.03])

    slider_prom = Slider(ax_prom, "Prominence", 0, 10, valinit=init_prom, valstep=0.5)
    slider_dist = Slider(ax_dist, "Min Distance", 0, 50, valinit=init_dist, valstep=2)

    # --- Update function ---
    def update(_):
        prom = slider_prom.val
        dist = int(slider_dist.val)

        peaks, props = detect_peaks(signal, prom, dist)

        sc_peaks.set_offsets(np.c_[wavelengths[peaks], signal[peaks]])
        sc_base.set_offsets(np.c_[wavelengths[props["left_bases"]], signal[props["left_bases"]]])

        depths = calculate_depths(signal, peaks, props)
        fwhms = calculate_fwhm(signal, wavelengths, peaks, props["left_bases"])

        print("\nDetected dips:")
        for d, f in zip(depths, fwhms):
            lam = wavelengths[d["peak_index"]]
            lam_base = wavelengths[d["baseline_index"]]
            depth = abs(d["depth"])
            print(f"λ={lam:.2f} | baseline λ={lam_base:.2f} | depth={depth:.2f} | FWHM={f['fwhm']:.2f} nm")

        fig.canvas.draw_idle()

    # Connect sliders
    slider_prom.on_changed(update)
    slider_dist.on_changed(update)

    # Initial update call
    update(None)

    plt.show()
