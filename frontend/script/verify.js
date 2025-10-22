async function verifyAccessCode(code) {
    try {
        const response = await fetch(window.API_CONFIG.ENDPOINTS.VERIFY, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: code })
        });

        const data = await response.json();
        
        if (data.valid) {
            sessionStorage.setItem('accessVerified', 'true');
            window.location.href = 'upload.html';
            return true;
        } else {
            const errorEl = document.getElementById('error');
            if (errorEl) {
                errorEl.textContent = 'Invalid code. Try again.';
                errorEl.classList.add('show');
            }
            return false;
        }
    } catch (error) {
        console.error('Error verifying access code:', error);
        const errorEl = document.getElementById('error');
        if (errorEl) {
            errorEl.textContent = 'Server error. Try again later.';
            errorEl.classList.add('show');
        }
        return false;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const accessForm = document.getElementById('access-form');
    
    if (accessForm) {
        accessForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const code = document.getElementById('access-code').value;
            verifyAccessCode(code);
        });
    }
});