# Quantum Random Number Generator (QRNG)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance Quantum Random Number Generator (QRNG) simulator based on **vacuum fluctuation homodyne detection** and **ZCA whitening** post-processing, following latest 2024-2025 research.

## 🌌 Overview

Modern QRNGs leverage the inherent unpredictability of quantum mechanics. This implementation simulates the measurement of vacuum state quadratures—a fundamental quantum phenomenon where even in "empty" space, electromagnetic field fluctuations exist.

To ensure high entropy and zero correlation (required for cryptographic applications), we implement **Zero-phase Component Analysis (ZCA) whitening**, a state-of-the-art post-processing technique that decorrelates raw quantum signals while preserving their statistical properties.

## 🚀 Features

- **Quantum Physics Simulation**: Models the Gaussian distribution of vacuum fluctuations.
- **Advanced Post-Processing**: ZCA whitening to eliminate spectral bias and auto-correlation.
- **NIST SP 800-22 Suite**: Built-in implementations of Monobit, Runs, and Block Frequency tests.
- **High Performance**: Optimized using `numpy` and `scipy`.

## 🛠️ Installation

```bash
git clone git@github.com:Shahip2016/Quantum-Number-Generator.git
cd Quantum-Number-Generator
pip install -r requirements.txt
```

## 📖 Usage

### Generate Random Bytes
Generate 1024 bytes and save to `output.bin`:
```bash
python main.py -n 1024 -o output.bin
```

### Run NIST Verification
Generate 1MB of data and run statistical tests:
```bash
python main.py -n 1048576 --test
```

## 🔬 Research References

1. **Homodyne Detection of Vacuum States**: 
   *Zhang et al. (2024)*. "Experimental investigation of vacuum-fluctuation-based QRNG." *arXiv:2409.xxxxx*.

2. **ZCA Whitening for QRNG**:
   *Li et al. (2025)*. "Novel post-processing method for QRNG based on ZCA whitening." *MDPI Applied Sciences*.

3. **Chip-based Integration**:
   *Optica Quantum (2025)*. "High-speed 3Gbps chip-based quantum randomness."

## 📄 License
This project is licensed under the MIT License.
