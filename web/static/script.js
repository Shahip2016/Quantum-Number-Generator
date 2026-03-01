document.addEventListener('DOMContentLoaded', () => {
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
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';

        try {
            const response = await fetch(`/generate?n=${n}`);
            const data = await response.json();

            // Update Display
            bitDisplay.textContent = data.bits.join('');

            // Visualize
            drawEntropy(data.bits);

            // Store bits for testing
            window.lastBitstream = data.bits;
            document.getElementById('nist-results').classList.add('hidden');

        } catch (error) {
            console.error('Generation failed:', error);
            bitDisplay.textContent = 'Error generating bits. Check console.';
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Quantum Bits';
        }
    }

    function drawEntropy(bits) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const size = Math.ceil(Math.sqrt(bits.length));
        const pSize = canvas.width / size;

        for (let i = 0; i < bits.length; i++) {
            const x = (i % size) * pSize;
            const y = Math.floor(i / size) * pSize;
            const val = bits[i] * 255;
            ctx.fillStyle = `rgb(${val}, ${val}, ${val})`;
            ctx.fillRect(x, y, pSize, pSize);
        }
    }

    async function runNistTests() {
        if (!window.lastBitstream) {
            alert('Generate bits first!');
            return;
        }

        const testBtn = document.getElementById('test-btn');
        const resultsSection = document.getElementById('nist-results');
        const testGrid = document.getElementById('test-grid');

        testBtn.disabled = true;
        testBtn.textContent = 'Testing...';
        resultsSection.classList.remove('hidden');
        testGrid.innerHTML = '<div class="loading">Running Statistical Tests...</div>';

        try {
            const response = await fetch('/test-nist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bits: window.lastBitstream })
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
            testGrid.innerHTML = '<div class="error">Test suite execution failed.</div>';
        } finally {
            testBtn.disabled = false;
            testBtn.textContent = 'Run NIST Tests';
        }
    }

    generateBtn.addEventListener('click', generateQuantumBits);
    document.getElementById('test-btn').addEventListener('click', runNistTests);
});
