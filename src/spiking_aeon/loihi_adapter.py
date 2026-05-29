"""Loihi 2 hardware adapter stub for spiking-aeon Package 26.

Real deployment requires INRC membership and the Lava SDK:
  pip install lava-nc  (Intel Neuromorphic Research Community)
  https://github.com/lava-nc/lava

This module provides the interface contract; all methods raise
RuntimeError unless Lava is installed and INRC credentials are set.
"""

from __future__ import annotations


def _lava_available() -> bool:
    try:
        import lava  # noqa: F401
        return True
    except ImportError:
        return False


class LoihiAdapter:
    """
    Translates a SpikingAeon CREP config to Loihi 2 via the Lava SDK.

    Requires: INRC access + `pip install lava-nc`
    Falls back to Brian2Backend when Lava is unavailable.
    """

    def __init__(self) -> None:
        self._available = _lava_available()

    @property
    def is_available(self) -> bool:
        return self._available

    def deploy(self, lif_config: dict[str, float], n_neurons: int = 1000) -> dict[str, object]:
        """
        Deploy LIF network to Loihi 2 chip and return benchmark metrics.
        Raises RuntimeError if Lava SDK is not installed.
        """
        if not self._available:
            raise RuntimeError(
                "Lava SDK not installed. Install via: pip install lava-nc\n"
                "INRC access required: "
                "https://www.intel.com/content/www/us/en/research/neuromorphic-computing.html\n"
                "Use brian2_backend.Brian2Backend for software simulation."
            )
        # Real Lava deployment would go here
        raise NotImplementedError("Lava deployment path not yet implemented.")  # pragma: no cover
