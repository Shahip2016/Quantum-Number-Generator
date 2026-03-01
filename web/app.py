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

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "QRNG-API"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
