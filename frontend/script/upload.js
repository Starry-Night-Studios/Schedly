const uploadForm = document.getElementById('upload-form');
const statusText = document.getElementById('upload-status');
const resultBox = document.getElementById('ocr-result');
const continueBtn = document.getElementById('continue-btn');

let extractedSchedule = null;

async function uploadImage(imageFile) {
    const statusText = document.getElementById('upload-status');
    
    try {
        statusText.textContent = 'Processing image...';
        
        const formData = new FormData();
        formData.append('image', imageFile);  // Changed from 'image-file' to 'image' to match backend

        const response = await fetch(window.API_CONFIG.ENDPOINTS.UPLOAD, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (response.ok) {
            statusText.textContent = 'Image processed successfully!';
            displayResults(data.text, data.schedule);
            return data.schedule;
        } else {
            statusText.textContent = `Error: ${data.error}`;
            return null;
        }
    } catch (error) {
        console.error('Error uploading image:', error);
        statusText.textContent = 'Error uploading image. Please try again.';
        return null;
    }
}

function displayResults(extractedText, schedule) {
    const resultBox = document.getElementById('ocr-result');
    const continueBtn = document.getElementById('continue-btn');
    
    // Display results
    resultBox.innerHTML = `
        <h3>Extracted Text:</h3>
        <pre>${extractedText}</pre>
        
        <h3>Parsed Schedule:</h3>
        <div id="scheduleResults"></div>
    `;
    
    // Display parsed schedule
    const scheduleDiv = document.getElementById('scheduleResults');
    
    schedule.forEach(course => {
        const courseDiv = document.createElement('div');
        courseDiv.className = 'course-item';
        courseDiv.innerHTML = `
            <h4>${course.code} - ${course.title}</h4>
            <p><strong>Room:</strong> ${course.room}</p>
            <p><strong>Instructor:</strong> ${course.instructor}</p>
            <div class="schedule-times">
                ${course.schedule.map(time => 
                    `<span class="time-slot">${time.day}: ${time.start}-${time.end}</span>`
                ).join('')}
            </div>
        `;
        scheduleDiv.appendChild(courseDiv);
    });
    
    // Show continue button and store schedule
    if (continueBtn) {
        continueBtn.style.display = 'block';
        continueBtn.onclick = () => window.location.href = 'email.html';
    }
    
    sessionStorage.setItem('extractedSchedule', JSON.stringify(schedule));
}

// DOM event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Check if access was verified
    if (!sessionStorage.getItem('accessVerified')) {
        window.location.href = 'index.html';
        return;
    }

    const uploadForm = document.getElementById('upload-form');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('image-file');
            if (fileInput && fileInput.files[0]) {
                uploadImage(fileInput.files[0]);
            } else {
                alert('Please select an image file.');
            }
        });
    }
});