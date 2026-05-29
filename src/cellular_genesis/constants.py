"""Physical and model constants for cellular-genesis Package 25."""

# ATP concentrations [mM]
ATP_HEALTHY_MM = 5.0        # K: healthy cytoplasmic ATP
ATP_THRESHOLD_MM = 1.0      # H*: cytochrome c release threshold
ATP_INITIAL_MM = 4.5        # typical starting point

# UTAC parameters
K_ATP = ATP_HEALTHY_MM
H_STAR_ATP = ATP_THRESHOLD_MM
ETA_APOPTOSIS = H_STAR_ATP / K_ATP  # 0.20
SIGMA_CREP = 2.2

# CREP criticality
GAMMA_CELLULAR = 0.090  # arctanh(0.20) / 2.2

# Kinetic rates [h⁻¹ unless noted]
V_OXPHOS_MAX = 0.25        # max OXPHOS ATP production rate (normalised)
V_GLYCOLYSIS = 0.08        # baseline glycolysis contribution
V_CONSUMPTION = 0.18       # baseline ATP consumption
V_LEAK = 0.02              # mitochondrial leak
LOADING_RATE_R = 0.20      # r: ATP recovery rate

# Bcl-2 family
BCL_XL_DEFAULT = 0.5       # Bcl-xL expression level [0,1]
K_BCL = 1.0                # half-saturation for Bcl-xL rescue
BCL_RESCUE_MAX = 0.30      # max fraction shift of H_threshold

# Caspase parameters
K_CASP_ACT = 0.8           # caspase activation rate
K_CASP_INH = 0.15          # caspase inhibition rate
HILL_N = 6.0               # Hill coefficient (ultrasensitivity)
CYTOC_THRESHOLD = 0.3      # cytochrome c threshold for activation

# Population
N_CELLS_DEFAULT = 1000
SIGMA_ATP_NOISE = 0.15     # cell-to-cell ATP variability (mM)
DURATION_HOURS = 48.0

# Benchmark targets
BENCHMARK_TARGETS = {
    "atp_threshold_mM":         (1.0,  0.20),
    "healthy_atp_mM":           (5.0,  0.10),
    "gamma_cellular":           (0.090, 0.010),
    "caspase_hill_coefficient": (6.0,  2.0),
    "survival_fraction_72h":    (0.50, 0.15),
    "bcl_rescue_shift":         (0.30, 0.10),
}

# genesis-os resource bridge
RESOURCE_ATP_THRESHOLD = 0.20  # normalised resource level triggering apoptosis
