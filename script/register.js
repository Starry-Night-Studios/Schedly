const emailForm = document.getElementById('email-form');
const emailStatus = document.getElementById('email-status');

async function registerUser(email, schedule) {
    try {
        const response = await fetch(window.API_CONFIG.ENDPOINTS.REGISTER, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                schedule: schedule
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            alert('Registration successful! You will receive email reminders 15 minutes before each class.');
            // Redirect to success page or reset form
            window.location.href = 'email.html';
        } else {
            alert(`Registration failed: ${data.error}`);
        }
    } catch (error) {
        console.error('Error registering user:', error);
        alert('Error registering. Please try again.');
    }
}

// DOM event listeners
document.addEventListener('DOMContentLoaded', function() {
    const emailForm = document.getElementById('email-form');
    
    if (emailForm) {
        emailForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('user-email').value;
            const schedule = JSON.parse(sessionStorage.getItem('extractedSchedule') || '[]');
            
            if (!email) {
                alert('Please enter your email address.');
                return;
            }
            
            if (schedule.length === 0) {
                alert('No schedule data found. Please upload your timetable first.');
                window.location.href = 'upload.html';
                return;
            }
            
            registerUser(email, schedule);
        });
    }
});
