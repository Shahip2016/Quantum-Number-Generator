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

            // Draw histogram
            drawHistogram(data.bits);

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

    function drawHistogram(bits) {
        const section = document.getElementById('histogram-section');
        section.classList.remove('hidden');

        const hCanvas = document.getElementById('histogram-canvas');
        const hCtx = hCanvas.getContext('2d');
        hCanvas.width = hCanvas.parentElement.clientWidth;
        hCanvas.height = 200;

        // Pack bits into bytes and count frequencies
        const freq = new Array(256).fill(0);
        for (let i = 0; i + 7 < bits.length; i += 8) {
            let byte = 0;
            for (let b = 0; b < 8; b++) byte = (byte << 1) | bits[i + b];
            freq[byte]++;
        }
        const maxFreq = Math.max(...freq);
        if (maxFreq === 0) return;

        const padding = { top: 10, bottom: 4, left: 2, right: 2 };
        const chartW = hCanvas.width - padding.left - padding.right;
        const chartH = hCanvas.height - padding.top - padding.bottom;
        const barW = chartW / 256;

        hCtx.clearRect(0, 0, hCanvas.width, hCanvas.height);

        // Store bar data for tooltip
        window._histogramBars = [];

        for (let i = 0; i < 256; i++) {
            const barH = (freq[i] / maxFreq) * chartH;
            const x = padding.left + i * barW;
            const y = padding.top + chartH - barH;

            const gradient = hCtx.createLinearGradient(x, y, x, y + barH);
            gradient.addColorStop(0, '#8b5cf6');
            gradient.addColorStop(1, '#06b6d4');
            hCtx.fillStyle = gradient;
            hCtx.fillRect(x, y, Math.max(barW - 0.5, 1), barH);

            window._histogramBars.push({ x, y, w: barW, h: barH, byte: i, count: freq[i] });
        }
    }

    // Histogram tooltip
    const histCanvas = document.getElementById('histogram-canvas');
    const tooltip = document.getElementById('histogram-tooltip');
    histCanvas.addEventListener('mousemove', (e) => {
        if (!window._histogramBars) return;
        const rect = histCanvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const bar = window._histogramBars.find(b => mx >= b.x && mx < b.x + b.w);
        if (bar) {
            tooltip.textContent = `Byte 0x${bar.byte.toString(16).toUpperCase().padStart(2, '0')} (${bar.byte}) — Count: ${bar.count}`;
            tooltip.style.left = (e.pageX + 12) + 'px';
            tooltip.style.top = (e.pageY - 30) + 'px';
            tooltip.classList.add('visible');
        } else {
            tooltip.classList.remove('visible');
        }
    });
    histCanvas.addEventListener('mouseleave', () => tooltip.classList.remove('visible'));

    generateBtn.addEventListener('click', generateQuantumBits);
    document.getElementById('test-btn').addEventListener('click', runNistTests);
    document.getElementById('copy-hex-btn').addEventListener('click', copyHex);
    document.getElementById('download-bin-btn').addEventListener('click', downloadBinary);
    document.getElementById('viz-mode').addEventListener('change', () => {
        if (window.lastData && window.lastData.bits) drawEntropy(window.lastData.bits);
    });
});
