"""Physical and model constants for spiking-aeon Package 26."""

# Firing rate [Hz]
FIRING_RATE_MAX_HZ = 1000.0       # K: Loihi 2 max sustainable rate per neuron
FIRING_RATE_CRITICAL_HZ = 320.0   # H*: critical rate for task performance
FIRING_RATE_INITIAL_HZ = 280.0    # typical starting point

# UTAC parameters
K_RATE = FIRING_RATE_MAX_HZ
H_STAR_RATE = FIRING_RATE_CRITICAL_HZ
ETA_SNN = H_STAR_RATE / K_RATE    # 0.32
SIGMA_CREP = 2.2

# CREP criticality
GAMMA_SNN = 0.150  # arctanh(0.32) / 2.2 ≈ 0.151

# LIF neuron parameters
TAU_M_MS = 20.0      # membrane time constant [ms]
V_THRESHOLD = -50.0  # mV
V_RESET = -65.0      # mV
V_REST = -65.0       # mV
TAU_REF_MS = 2.0     # refractory period [ms]
R_MEMBRANE = 10.0    # MΩ (membrane resistance)

# Synaptic parameters
WEIGHT_INIT = 0.5    # initial synaptic weight [0, 1]
STDP_LR = 0.01       # STDP learning rate
TAU_STDP_MS = 20.0   # STDP time window [ms]

# Stochastic resonance
D_NOISE_OPTIMAL = 0.15  # optimal noise amplitude (Ferreira 2025)
D_NOISE_MIN = 0.01
D_NOISE_MAX = 0.50

# Network defaults
N_NEURONS_DEFAULT = 1000
N_EXCITATORY_FRAC = 0.8          # 80% excitatory (Dale's law)
DURATION_MS_DEFAULT = 1000.0
DT_MS = 0.1                       # simulation timestep [ms]

# NeuEdge / Loihi 2 benchmark targets (arXiv:2602.02439)
LOIHI2_ENERGY_GOPS_W = 847.0     # GOp/s/W
LOIHI2_LATENCY_MS = 2.3
LOIHI2_CORE_UTIL_PCT = 89.0
LOIHI2_ACCURACY = 0.962

# STDP plasticity rate (normalised, per year equivalent)
LOADING_RATE_R = 0.30

BENCHMARK_TARGETS = {
    "energy_efficiency_GOp_s_W": (847.0, 84.7),
    "inference_latency_ms":      (2.3,   0.46),
    "core_utilization_pct":      (89.0,  4.45),
    "accuracy_vs_gpu":           (0.96,  0.02),
    "gamma_snn":                 (0.150, 0.020),
    "optimal_noise_D_res":       (0.15,  0.05),
}
