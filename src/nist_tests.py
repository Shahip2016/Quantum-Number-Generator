import numpy as np
import logging
from scipy import special
from typing import Tuple

logger = logging.getLogger(__name__)

def _validate_bitstream(bitstream: np.ndarray, min_length: int = 1):
    if not isinstance(bitstream, np.ndarray):
        raise TypeError("Bitstream must be a numpy ndarray.")
    if bitstream.size < min_length:
        raise ValueError(f"Bitstream too short. Minimum length required: {min_length}")
    if not np.all(np.isin(bitstream, [0, 1])):
        raise ValueError("Bitstream must contain only 0s and 1s.")

def monobit_test(bitstream: np.ndarray) -> float:
    """
    NIST Frequency (Monobit) Test.
    The focus of the test is the proportion of zeroes and ones for the entire sequence.
    """
    _validate_bitstream(bitstream, min_length=100)
    n = len(bitstream)
    # Convert 0s to -1s
    s_n = np.sum(2 * bitstream - 1)
    s_obs = abs(s_n) / np.sqrt(n)
    p_value = special.erfc(s_obs / np.sqrt(2))
    return p_value

def runs_test(bitstream: np.ndarray) -> float:
    """
    NIST Runs Test.
    The focus of the test is the total number of runs in the sequence, 
    where a run is an uninterrupted sequence of identical bits.
    """
    _validate_bitstream(bitstream, min_length=100)
    n = len(bitstream)
    pi = np.sum(bitstream) / n
    
    # Pre-test: Frequency test
    if abs(pi - 0.5) >= (2 / np.sqrt(n)):
        logger.warning(f"Runs Test: Sequence failed frequency pre-test (pi={pi:.4f}). Returning P-value=0.0")
        return 0.0
    
    # Observe total runs
    v_n_obs = 1 + np.sum(bitstream[:-1] != bitstream[1:])
    
    # Compute P-value
    numerator = abs(v_n_obs - 2 * n * pi * (1 - pi))
    denominator = 2 * np.sqrt(2 * n) * pi * (1 - pi)
    p_value = special.erfc(numerator / denominator)
    return p_value

def block_frequency_test(bitstream: np.ndarray, block_size: int = 128) -> float:
    """
    NIST Frequency Test within a Block.
    The focus of the test is the proportion of ones within M-bit blocks.
    """
    _validate_bitstream(bitstream, min_length=block_size)
    n = len(bitstream)
    n_blocks = n // block_size
    if n_blocks == 0:
        return 0.0
        
    # Trim bitstream to match integer number of blocks
    trimmed_stream = bitstream[:n_blocks * block_size]
    # Reshape and compute proportions in parallel
    blocks = trimmed_stream.reshape(n_blocks, block_size)
    proportions = np.sum(blocks, axis=1) / block_size
    
    chi_square = 4 * block_size * np.sum((proportions - 0.5)**2)
    p_value = special.gammaincc(n_blocks / 2, chi_square / 2)
    return p_value

def serial_test(bitstream: np.ndarray, m: int = 2) -> Tuple[float, float]:
    """
    NIST Serial Test.
    Checks the frequency of all possible overlapping m-bit patterns.
    Returns two p-values (P-value1 and P-value2).
    """
    _validate_bitstream(bitstream, min_length=100)
    n = len(bitstream)
    
    def psi_square(m_len):
        if m_len == 0: return 0.0
        # Overlapping blocks
        padded_stream = np.append(bitstream, bitstream[:m_len-1])
        counts = {}
        for i in range(n):
            pattern = tuple(padded_stream[i:i+m_len])
            counts[pattern] = counts.get(pattern, 0) + 1
        
        sum_sq = sum(c**2 for c in counts.values())
        return (2**m_len / n) * sum_sq - n

    psim = psi_square(m)
    psim1 = psi_square(m-1)
    psim2 = psi_square(m-2)
    
    del1 = psim - psim1
    del2 = psim - 2*psim1 + psim2
    
    p_value1 = special.gammaincc(2**(m-2), del1/2) # m=2 case: df=2^(2-1)=2
    p_value2 = special.gammaincc(2**(m-3) if m > 2 else 1/2, del2/2) # Simplified
    
    return p_value1, p_value2

def run_all_tests(bitstream: np.ndarray) -> None:
    logger.info("Starting NIST Statistical Tests")
    print("--- NIST Statistical Test Results ---")
    p_monobit = monobit_test(bitstream)
    p_runs = runs_test(bitstream)
    p_block = block_frequency_test(bitstream)
    p_serial1, p_serial2 = serial_test(bitstream)
    
    print(f"Monobit Test P-value: {p_monobit:.6f} {'[PASS]' if p_monobit > 0.01 else '[FAIL]'}")
    print(f"Runs Test P-value: {p_runs:.6f} {'[PASS]' if p_runs > 0.01 else '[FAIL]'}")
    print(f"Block Frequency Test P-value: {p_block:.6f} {'[PASS]' if p_block > 0.01 else '[FAIL]'}")
    print(f"Serial Test P-value1: {p_serial1:.6f} {'[PASS]' if p_serial1 > 0.01 else '[FAIL]'}")
    print(f"Serial Test P-value2: {p_serial2:.6f} {'[PASS]' if p_serial2 > 0.01 else '[FAIL]'}")

if __name__ == "__main__":
    # Test with random data
    test_bits = np.random.randint(0, 2, 10000)
    run_all_tests(test_bits)
