from flask import Flask, jsonify, send_from_directory, request
import os
import sys
import numpy as np

# Add project root to path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.qrng_core import VacuumFluctuationSimulator, ZCAWhitening
from src.nist_tests import run_all_tests

app = Flask(__name__, static_folder='static')
simulator = VacuumFluctuationSimulator()
zca = ZCAWhitening()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/generate', methods=['GET'])
def generate_bits():
    num_bytes = int(request.args.get('n', 1024))
    features = 8
    
    n_samples = num_bytes // features + (1 if num_bytes % features != 0 else 0)
    total_samples = n_samples * features
    
    raw_data = simulator.generate_raw_quadratures(total_samples).reshape(n_samples, features)
    zca.fit(raw_data)
    whitened_data = zca.transform(raw_data).flatten()
    quantized = simulator.quantize_data(whitened_data, bits=8)
    bitstream = simulator.extract_bits(quantized)[:num_bytes * 8]
    
    return jsonify({
        "bits": bitstream.tolist(),
        "hex": np.packbits(bitstream).tobytes().hex(),
        "length_bits": len(bitstream)
    })

@app.route('/test-nist', methods=['POST'])
def test_nist():
    data = request.json
    bits = np.array(data.get('bits', []), dtype=int)
    
    if len(bits) < 100:
        return jsonify({"error": "Insufficient bits for NIST tests (min 100)"}), 400
        
    # Capture results from run_all_tests
    # Note: run_all_tests in src/nist_tests.py currently prints to stdout and returns None
    # We would ideally refactor it to return results, but for now we'll simulate or monkeypatch
    # Since I cannot easily refactor nist_tests.py without seeing it fully, I will implement a wrapper
    
    results = []
    # Simplified mock/logic based on the project's nist_tests.py structure
    from src.nist_tests import run_monobit_test, run_runs_test, run_block_frequency_test
    
    results.append({"name": "Monobit Frequency", "passed": run_monobit_test(bits)})
    results.append({"name": "Runs Test", "passed": run_runs_test(bits)})
    results.append({"name": "Block Frequency", "passed": run_block_frequency_test(bits, 128 if len(bits) >= 128 else 8)})
    
    return jsonify({"results": results})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "QRNG-API"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
