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
    
    from src.nist_tests import monobit_test, runs_test, block_frequency_test, serial_test
    
    results = []
    
    p_mono = float(monobit_test(bits))
    results.append({"name": "Monobit Frequency", "passed": p_mono > 0.01, "p_value": round(p_mono, 6)})
    
    p_runs = float(runs_test(bits))
    results.append({"name": "Runs Test", "passed": p_runs > 0.01, "p_value": round(p_runs, 6)})
    
    block_size = 128 if len(bits) >= 128 else 8
    p_block = float(block_frequency_test(bits, block_size))
    results.append({"name": "Block Frequency", "passed": p_block > 0.01, "p_value": round(p_block, 6)})
    
    p_s1, p_s2 = serial_test(bits)
    p_s1, p_s2 = float(p_s1), float(p_s2)
    results.append({"name": "Serial Test (∇ψ²)", "passed": p_s1 > 0.01, "p_value": round(p_s1, 6)})
    results.append({"name": "Serial Test (∇²ψ²)", "passed": p_s2 > 0.01, "p_value": round(p_s2, 6)})
    
    return jsonify({"results": results})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "QRNG-API"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
