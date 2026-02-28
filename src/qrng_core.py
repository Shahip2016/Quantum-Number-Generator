import numpy as np
import logging
from scipy import linalg
from typing import Tuple, Optional

# Configure logging
logger = logging.getLogger(__name__)

class ZCAWhitening:
    """
    Implements Zero-phase Component Analysis (ZCA) whitening.
    ZCA whitening transforms the data such that the covariance matrix 
    becomes an identity matrix, effectively removing correlations 
    while staying as close as possible to the original data.
    """
    def __init__(self, epsilon: float = 1e-5):
        self.epsilon = epsilon
        self.zca_matrix: Optional[np.ndarray] = None
        self.mean: Optional[np.ndarray] = None

    def fit(self, x: np.ndarray) -> "ZCAWhitening":
        """
        Computes the ZCA transformation matrix from the input data.
        X should be of shape (n_samples, n_features)
        """
        if x.ndim != 2:
            raise ValueError(f"Expected 2D array, got {x.ndim}D.")
        if x.shape[0] <= 1:
            raise ValueError("Need more than one sample to compute covariance.")

        logger.debug(f"Fitting ZCA on data of shape {x.shape}")
        self.mean = np.mean(x, axis=0)
        x_centered = x - self.mean
        
        # Compute covariance matrix with safety check
        cov = np.cov(x_centered, rowvar=False)
        
        try:
            # Singular Value Decomposition
            u, s, v = linalg.svd(cov)
        except linalg.LinAlgError as e:
            logger.error(f"SVD failed: {e}")
            raise ValueError("Covariance matrix SVD failed. Data might be highly singular.") from e
            
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
    
    def __init__(self, shot_noise_variance: float = 1.0):
        if shot_noise_variance <= 0:
            raise ValueError("Shot noise variance must be positive.")
        self.shot_noise_variance = shot_noise_variance
        self.sigma = np.sqrt(shot_noise_variance)

    def generate_raw_quadratures(self, n_samples: int) -> np.ndarray:
        """
        Generates raw quadrature data following a Gaussian distribution
        centered at 0 with variance proportional to shot noise.
        """
        if n_samples <= 0:
            raise ValueError("Number of samples must be positive.")
        logger.debug(f"Generating {n_samples} raw quadrature samples")
        # Vacuum fluctuations in quadrature follow a Gaussian distribution
        return np.random.normal(0, self.sigma, n_samples)

    def quantize_data(self, data: np.ndarray, bits: int = 8) -> np.ndarray:
        """
        Digitizes the analog quantum signal into N-bit integers using vectorized normalization.
        """
        if data.size == 0:
            return np.array([], dtype=np.uint8)
        if bits < 1 or bits > 16:
            raise ValueError("Bits must be between 1 and 16.")

        # Linear quantization
        min_val = np.min(data)
        max_val = np.max(data)
        
        if max_val == min_val:
            logger.warning("Data is constant, cannot normalize effectively.")
            return np.zeros(data.shape, dtype=np.uint8)
            
        # Vectorized rescaling to [0, 2^bits - 1]
        # Using a safer approach with clipping to avoid overflow before conversion
        rescaled = (data - min_val) / (max_val - min_val) * (2**bits - 1)
        quantized = np.clip(np.round(rescaled), 0, 2**bits - 1)
        return quantized.astype(np.uint8 if bits <= 8 else np.uint16)

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
