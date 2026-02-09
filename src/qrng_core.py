import numpy as np
from scipy import linalg
from typing import Tuple

class ZCAWhitening:
    """
    Implements Zero-phase Component Analysis (ZCA) whitening.
    ZCA whitening transforms the data such that the covariance matrix 
    becomes an identity matrix, effectively removing correlations 
    while staying as close as possible to the original data.
    """
    def __init__(self, epsilon: float = 1e-5):
        self.epsilon = epsilon
        self.zca_matrix = None
        self.mean = None

    def fit(self, x: np.ndarray):
        """
        Computes the ZCA transformation matrix from the input data.
        X should be of shape (n_samples, n_features)
        """
        self.mean = np.mean(x, axis=0)
        x_centered = x - self.mean
        
        # Compute covariance matrix with safety check
        cov = np.cov(x_centered, rowvar=False)
        
        # Singular Value Decomposition
        u, s, v = linalg.svd(cov)
        
        # ZCA Matrix: U * diag(1/sqrt(S + epsilon)) * U^T
        # Using a more robust epsilon handling
        s_inv = 1.0 / np.sqrt(s + self.epsilon)
        self.zca_matrix = np.dot(u, np.dot(np.diag(s_inv), u.T))
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        """
        Applies the ZCA whitening transformation.
        """
        if self.zca_matrix is None:
            raise ValueError("ZCAWhitening must be fit before transform.")
        
        return np.dot(x - self.mean, self.zca_matrix)

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
        Digitizes the analog quantum signal into N-bit integers using vectorized normalization.
        """
        # Linear quantization
        min_val = np.min(data)
        max_val = np.max(data)
        
        if max_val == min_val:
            return np.zeros(data.shape, dtype=np.uint8)
            
        # Vectorized rescaling to [0, 2^bits - 1]
        quantized = ((data - min_val) / (max_val - min_val) * (2**bits - 1))
        return quantized.astype(np.uint8)

    def extract_bits(self, quantized_data: np.ndarray, bits_per_sample: int = 8) -> np.ndarray:
        """
        Extracts raw bits from quantized integers using vectorized NumPy operations.
        """
        # Ensure data is in the correct uint form for unpackbits
        data_uint = quantized_data.astype(np.uint8)
        # unpackbits converts each uint8 into 8 bits
        bits = np.unpackbits(data_uint)
        
        # If bits_per_sample < 8, we only take the LSBs or relevant bits.
        # However, usually we take all bits or a specific amount.
        # This implementation assumes we want the full bit depth provided by uint8.
        return bits

if __name__ == "__main__":
    simulator = VacuumFluctuationSimulator()
    n_samples = 10000
    n_features = 4  # Treat consecutive samples as features for whitening
    
    raw_data = simulator.generate_raw_quadratures(n_samples * n_features).reshape(n_samples, n_features)
    
    print(f"Original Mean: {np.mean(raw_data):.4f}")
    print(f"Original Covariance (subset):\n{np.cov(raw_data.T)}")
    
    zca = ZCAWhitening()
    zca.fit(raw_data)
    whitened_data = zca.transform(raw_data)
    
    print(f"\nWhitened Mean: {np.mean(whitened_data):.4f}")
    print(f"Whitened Covariance (should be identity):\n{np.cov(whitened_data.T)}")
