document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle
    const savedTheme = localStorage.getItem('qrng-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    document.getElementById('theme-toggle').addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('qrng-theme', next);
        updateThemeIcon(next);
    });

    function updateThemeIcon(theme) {
        document.getElementById('theme-icon-moon').style.display = theme === 'dark' ? 'block' : 'none';
        document.getElementById('theme-icon-sun').style.display = theme === 'light' ? 'block' : 'none';
    }

    const generateBtn = document.getElementById('generate-btn');
    const numBytesInput = document.getElementById('num-bytes');
    const bitDisplay = document.getElementById('bit-display');
    const canvas = document.getElementById('entropy-canvas');
    const ctx = canvas.getContext('2d');

    // Initialize Canvas Size
    function resizeCanvas() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    async function generateQuantumBits() {
        const n = numBytesInput.value;
        const statusText = document.getElementById('status-text');
        const statusDot = document.querySelector('.status-dot');

        generateBtn.disabled = true;
        generateBtn.textContent = 'Capturing...';
        statusText.textContent = 'Capturing Vacuum Fluctuations...';
        statusDot.style.background = 'var(--secondary)';

        try {
            const t0 = performance.now();
            const response = await fetch(`/generate?n=${n}`);
            const data = await response.json();
            const genTime = ((performance.now() - t0) / 1000).toFixed(2);

            // Store results
            window.lastData = data;

            // Update Display (show first 1000 bits only for performance if very large)
            const preview = data.bits.length > 2000 ? data.bits.slice(0, 2000).join('') + '...' : data.bits.join('');
            bitDisplay.textContent = preview;

            // Visualize
            drawEntropy(data.bits);

            // Update stats dashboard
            updateStats(data.bits.length, genTime);

            // Hide previous test results
            document.getElementById('nist-results').classList.add('hidden');

            statusText.textContent = 'Quantum Field Stable';
            statusDot.style.background = 'var(--success)';

        } catch (error) {
            console.error('Generation failed:', error);
            bitDisplay.textContent = 'Error generating bits. Check console.';
            statusText.textContent = 'Field Instability Detected';
            statusDot.style.background = '#ef4444';
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Entropy';
        }
    }

    function drawEntropy(bits) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const mode = document.getElementById('viz-mode').value;
        const size = Math.ceil(Math.sqrt(bits.length));
        const pSize = canvas.width / size;

        for (let i = 0; i < bits.length; i++) {
            const x = (i % size) * pSize;
            const y = Math.floor(i / size) * pSize;

            if (mode === 'bw') {
                const val = bits[i] * 255;
                ctx.fillStyle = `rgb(${val}, ${val}, ${val})`;
            } else {
                // Spectral mode: use index and bit value for color
                const hue = (i / bits.length) * 360;
                const lum = bits[i] ? 60 : 20;
                ctx.fillStyle = `hsl(${hue}, 80%, ${lum}%)`;
            }
            ctx.fillRect(x, y, pSize, pSize);
        }
    }

    function copyHex() {
        if (!window.lastData || !window.lastData.hex) return;
        navigator.clipboard.writeText(window.lastData.hex).then(() => {
            const btn = document.getElementById('copy-hex-btn');
            const originalHtml = btn.innerHTML;
            btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
            btn.style.color = 'var(--success)';
            setTimeout(() => {
                btn.innerHTML = originalHtml;
                btn.style.color = '';
            }, 2000);
        });
    }

    function downloadBinary() {
        if (!window.lastData || !window.lastData.hex) return;
        const hex = window.lastData.hex;
        const bytes = new Uint8Array(hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
        const blob = new Blob([bytes], { type: 'application/octet-stream' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `quantum_entropy_${Date.now()}.bin`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    async function runNistTests() {
        if (!window.lastData || !window.lastData.bits) {
            alert('Generate entropy first!');
            return;
        }

        const testBtn = document.getElementById('test-btn');
        const resultsSection = document.getElementById('nist-results');
        const testGrid = document.getElementById('test-grid');

        testBtn.disabled = true;
        testBtn.textContent = 'Certifying...';
        resultsSection.classList.remove('hidden');
        testGrid.innerHTML = '<div class="loading">Statistically validating quantum bitstream...</div>';

        try {
            const response = await fetch('/test-nist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bits: window.lastData.bits })
            });
            const data = await response.json();

            testGrid.innerHTML = data.results.map(res => `
                <div class="test-item ${res.passed ? 'pass' : 'fail'}">
                    <span class="test-name">${res.name}</span>
                    <span class="test-status">${res.passed ? 'PASSED' : 'FAILED'}</span>
                </div>
            `).join('');

        } catch (error) {
            console.error('NIST tests failed:', error);
            testGrid.innerHTML = '<div class="error">Validation suite execution failed.</div>';
        } finally {
            testBtn.disabled = false;
            testBtn.textContent = 'NIST Certification';
        }
    }

    function updateStats(totalBits, genTimeSec) {
        const dashboard = document.getElementById('stats-dashboard');
        dashboard.classList.remove('hidden');

        // Entropy rate: ratio of 1s (ideal = 0.5 → 1.0 bit/bit)
        const bits = window.lastData.bits;
        const ones = bits.reduce((s, b) => s + b, 0);
        const p = ones / bits.length;
        const entropy = (p > 0 && p < 1) ? -(p * Math.log2(p) + (1 - p) * Math.log2(1 - p)) : 0;

        const throughput = (totalBits / parseFloat(genTimeSec)).toFixed(0);

        const updates = [
            ['stat-total-bits', totalBits.toLocaleString()],
            ['stat-entropy-rate', entropy.toFixed(4) + ' b/b'],
            ['stat-gen-time', genTimeSec + ' s'],
            ['stat-throughput', Number(throughput).toLocaleString() + ' b/s'],
        ];
        updates.forEach(([id, val]) => {
            const el = document.getElementById(id);
            el.textContent = val;
            el.classList.remove('animate');
            void el.offsetWidth; // reflow
            el.classList.add('animate');
        });
    }

    generateBtn.addEventListener('click', generateQuantumBits);
    document.getElementById('test-btn').addEventListener('click', runNistTests);
    document.getElementById('copy-hex-btn').addEventListener('click', copyHex);
    document.getElementById('download-bin-btn').addEventListener('click', downloadBinary);
    document.getElementById('viz-mode').addEventListener('change', () => {
        if (window.lastData && window.lastData.bits) drawEntropy(window.lastData.bits);
    });
});
