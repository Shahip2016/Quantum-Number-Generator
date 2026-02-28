import argparse
import numpy as np
from src.qrng_core import VacuumFluctuationSimulator, ZCAWhitening
from src.nist_tests import run_all_tests
import sys
import logging

def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

def main():
    parser = argparse.ArgumentParser(description="Quantum Random Number Generator (QRNG) - Vacuum Fluctuations & ZCA Whitening")
    parser.add_argument("-n", "--num_bytes", type=int, default=1024, help="Number of random bytes to generate")
    parser.add_argument("-o", "--output", type=str, help="Output file to save random bytes")
    parser.add_argument("--test", action="store_true", help="Run NIST statistical tests on generated data")
    parser.add_argument("--features", type=int, default=8, help="Number of features for ZCA whitening (window size)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    if args.num_bytes <= 0:
        logger.error("Error: --num_bytes must be a positive integer.")
        sys.exit(1)

    try:
        # Initialize components
        logger.info("Initializing QRNG components...")
        simulator = VacuumFluctuationSimulator()
        zca = ZCAWhitening()
        
        # 1 sample = 8 bits = 1 byte (with 8-bit quantization)
        n_samples = args.num_bytes // args.features + (1 if args.num_bytes % args.features != 0 else 0)
        total_samples = n_samples * args.features
        
        logger.info(f"Generating {total_samples} raw samples for {args.num_bytes} bytes...")
        # 1. Generate Raw Quadrature Data
        raw_data = simulator.generate_raw_quadratures(total_samples).reshape(n_samples, args.features)
        
        # 2. Apply ZCA Whitening
        logger.debug("Applying ZCA whitening...")
        zca.fit(raw_data)
        whitened_data = zca.transform(raw_data).flatten()
        
        # 3. Quantize and Extract Bits
        logger.debug("Quantizing data...")
        quantized = simulator.quantize_data(whitened_data, bits=8)
        
        # Extract bits from the quantized bytes
        bitstream = simulator.extract_bits(quantized)
        
        # Slice bitstream to exact number of requested bits (num_bytes * 8)
        bitstream = bitstream[:args.num_bytes * 8]
        
        # Convert bitstream to actual bytes
        byte_array = np.packbits(bitstream)
        
        logger.info(f"Successfully generated {len(byte_array)} bytes of quantum randomness.")
        
        if args.output:
            try:
                with open(args.output, "wb") as f:
                    f.write(byte_array.tobytes())
                logger.info(f"Saved random data to {args.output}")
            except IOError as e:
                logger.error(f"Failed to write output file: {e}")
                sys.exit(1)
            
        if args.test:
            run_all_tests(bitstream)

    except Exception as e:
        logger.exception(f"An unexpected error occurred during QRNG execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
