// File input handling
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        fileName.textContent = e.target.files[0].name;
    } else {
        fileName.textContent = 'Choose PDF or DOCX file';
    }
});

// Form submission
const uploadForm = document.getElementById('uploadForm');
const generateBtn = document.getElementById('generateBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const flashcardsContainer = document.getElementById('flashcardsContainer');
const flashcardsGrid = document.getElementById('flashcardsGrid');
const errorMessage = document.getElementById('errorMessage');
const cardCount = document.getElementById('cardCount');

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    const file = fileInput.files[0];
    const difficulty = document.getElementById('difficulty').value;
    
    if (!file) {
        showError('Please select a file to upload');
        return;
    }
    
    formData.append('file', file);
    formData.append('difficulty', difficulty);
    
    // Show loading state
    generateBtn.disabled = true;
    loadingSpinner.style.display = 'block';
    flashcardsContainer.style.display = 'none';
    errorMessage.style.display = 'none';
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to generate flashcards');
        }
        
        const flashcards = await response.json();
        displayFlashcards(flashcards);
        
    } catch (error) {
        showError(error.message);
    } finally {
        generateBtn.disabled = false;
        loadingSpinner.style.display = 'none';
    }
});

function displayFlashcards(flashcards) {
    if (!flashcards || flashcards.length === 0) {
        showError('No flashcards were generated. Please try a different document.');
        return;
    }
    
    // Clear previous flashcards
    flashcardsGrid.innerHTML = '';
    
    // Update count
    cardCount.textContent = flashcards.length;
    
    // Create flashcard elements
    flashcards.forEach((card, index) => {
        const flashcardDiv = document.createElement('div');
        flashcardDiv.className = 'flashcard';
        flashcardDiv.setAttribute('data-index', index);
        
        flashcardDiv.innerHTML = `
            <div class="flashcard-inner">
                <div class="flashcard-front">
                    <div class="flashcard-label">Question ${index + 1}</div>
                    <div class="flashcard-content">${escapeHtml(card.question)}</div>
                </div>
                <div class="flashcard-back">
                    <div class="flashcard-label">Answer</div>
                    <div class="flashcard-content">${escapeHtml(card.answer)}</div>
                </div>
            </div>
        `;
        
        // Add click event to flip card
        flashcardDiv.addEventListener('click', () => {
            flashcardDiv.classList.toggle('flipped');
        });
        
        flashcardsGrid.appendChild(flashcardDiv);
        
        // Add animation delay for staggered appearance
        setTimeout(() => {
            flashcardDiv.style.opacity = '1';
            flashcardDiv.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Show flashcards container with animation
    flashcardsContainer.style.display = 'block';
    flashcardsContainer.style.opacity = '0';
    setTimeout(() => {
        flashcardsContainer.style.transition = 'opacity 0.5s ease';
        flashcardsContainer.style.opacity = '1';
    }, 50);
}

function showError(message) {
    errorMessage.textContent = `❌ Error: ${message}`;
    errorMessage.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function sendFeedback(type) {
    // Placeholder for feedback functionality
    // In a production app, this would send feedback to the backend
    const messages = {
        'easy': 'Thank you! We\'ll generate harder flashcards next time.',
        'hard': 'Thank you! We\'ll make flashcards easier next time.',
        'perfect': 'Awesome! Glad the difficulty was just right!'
    };
    
    alert(messages[type] || 'Thank you for your feedback!');
    
    // You could implement this to send feedback to backend:
    // fetch('/feedback', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ type, difficulty: document.getElementById('difficulty').value })
    // });
}

// Add initial animation styles
document.addEventListener('DOMContentLoaded', () => {
    const style = document.createElement('style');
    style.textContent = `
        .flashcard {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
    `;
    document.head.appendChild(style);
});