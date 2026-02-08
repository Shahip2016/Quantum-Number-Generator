import numpy as np
from typing import Tuple

class VacuumFluctuationSimulator:
    """
    Simulates the homodyne detection of quantum vacuum state fluctuations.
    According to quantum mechanics, the vacuum state has non-zero fluctuations 
    in its quadrature amplitudes (X and P).
    """
    
    def __init__(self, shot_noise_variance: float = 1.0, sampling_rate: int = 1000000):
        self.shot_noise_variance = shot_noise_variance
        self.sampling_rate = sampling_rate
        self.sigma = np.sqrt(shot_noise_variance)

    def generate_raw_quadratures(self, n_samples: int) -> np.ndarray:
        """
        Generates raw quadrature data following a Gaussian distribution
        centered at 0 with variance proportional to shot noise.
        """
        # Vacuum fluctuations in quadrature follow a Gaussian distribution
        return np.random.normal(0, self.sigma, n_samples)

    def quantize_data(self, data: np.ndarray, bits: int = 8) -> np.ndarray:
        """
        Digitizes the analog quantum signal into N-bit integers.
        """
        # Normalize to range of bit depth
        min_val, max_val = data.min(), data.max()
        if max_val == min_val:
            return np.zeros(data.shape, dtype=np.uint8)
            
        normalized = (data - min_val) / (max_val - min_val)
        quantized = (normalized * (2**bits - 1)).astype(np.uint64)
        return quantized

    def extract_bits(self, quantized_data: np.ndarray, bits_per_sample: int = 8) -> np.ndarray:
        """
        Extracts raw bits from quantized integers.
        """
        # Simply convert to bitstream
        bitstream = []
        for val in quantized_data:
            bits = bin(val)[2:].zfill(bits_per_sample)
            bitstream.extend([int(b) for b in bits])
        return np.array(bitstream, dtype=np.uint8)

if __name__ == "__main__":
    simulator = VacuumFluctuationSimulator()
    raw_data = simulator.generate_raw_quadratures(1000)
    print(f"Generated {len(raw_data)} samples of vacuum fluctuations.")
    print(f"Mean: {np.mean(raw_data):.4f}, Std: {np.std(raw_data):.4f}")
