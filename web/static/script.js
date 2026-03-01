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

    generateBtn.addEventListener('click', generateQuantumBits);
});
