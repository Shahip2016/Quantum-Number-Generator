import numpy as np
from scipy import special

def monobit_test(bitstream: np.ndarray) -> float:
    """
    NIST Frequency (Monobit) Test.
    The focus of the test is the proportion of zeroes and ones for the entire sequence.
    """
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
    n = len(bitstream)
    pi = np.sum(bitstream) / n
    
    # Pre-test: Frequency test
    if abs(pi - 0.5) >= (2 / np.sqrt(n)):
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
    n = len(bitstream)
    n_blocks = n // block_size
    if n_blocks == 0:
        return 0.0
        
    proportions = []
    for i in range(n_blocks):
        block = bitstream[i * block_size : (i + 1) * block_size]
        proportions.append(np.sum(block) / block_size)
    
    chi_square = 4 * block_size * np.sum((np.array(proportions) - 0.5)**2)
    p_value = special.gammaincc(n_blocks / 2, chi_square / 2)
    return p_value

def run_all_tests(bitstream: np.ndarray):
    print("--- NIST Statistical Test Results ---")
    p_monobit = monobit_test(bitstream)
    p_runs = runs_test(bitstream)
    p_block = block_frequency_test(bitstream)
    
    print(f"Monobit Test P-value: {p_monobit:.6f} {'[PASS]' if p_monobit > 0.01 else '[FAIL]'}")
    print(f"Runs Test P-value: {p_runs:.6f} {'[PASS]' if p_runs > 0.01 else '[FAIL]'}")
    print(f"Block Frequency Test P-value: {p_block:.6f} {'[PASS]' if p_block > 0.01 else '[FAIL]'}")

if __name__ == "__main__":
    # Test with random data
    test_bits = np.random.randint(0, 2, 10000)
    run_all_tests(test_bits)
