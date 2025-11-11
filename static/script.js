let userId = null;
let currentAudio = null;
const API_BASE = window.location.origin;

// Audio feedback files
const AUDIO_FILES = {
    correct: '/audio/correct_audio.wav',
    incorrect1: '/audio/incorrect_audio_1.wav',
    incorrect2: '/audio/incorrect_audio_2.wav',
    incorrect3: '/audio/incorrect_audio_3.wav',
    lose: '/audio/you_lose_audio.wav'
};

function playFeedbackAudio(type) {
    let audioPath;
    
    if (type === 'correct') {
        audioPath = AUDIO_FILES.correct;
    } else if (type === 'lose') {
        audioPath = AUDIO_FILES.lose;
    } else if (type === 'incorrect') {
        // Randomly pick one of the incorrect sounds
        const randomIncorrect = Math.floor(Math.random() * 3) + 1;
        audioPath = AUDIO_FILES[`incorrect${randomIncorrect}`];
    }
    
    if (audioPath) {
        const audio = new Audio(audioPath);
        audio.play().catch(err => console.log('Audio play failed:', err));
    }
}

async function startGame() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/start`, {
            method: 'POST'
        });
        const data = await response.json();
        userId = data.user_id;
        
        document.getElementById('startScreen').classList.add('hidden');
        document.getElementById('loadingScreen').classList.add('hidden');
        document.getElementById('gameScreen').classList.remove('hidden');
        
        // Auto-play first word
        await playAudio();
    } catch (error) {
        showMessage('Failed to start game. Please try again.', 'error');
        document.getElementById('loadingScreen').classList.add('hidden');
        document.getElementById('startScreen').classList.remove('hidden');
    }
}

async function playAudio() {
    if (!userId) return;
    
    try {
        const response = await fetch(`${API_BASE}/audio?user_id=${userId}`);
        if (!response.ok) throw new Error('Failed to load audio');
        
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        if (currentAudio) {
            currentAudio.pause();
        }
        
        currentAudio = new Audio(audioUrl);
        currentAudio.play();
    } catch (error) {
        showMessage('Failed to play audio.', 'error');
    }
}

async function showDefinition() {
    if (!userId) return;
    
    try {
        const response = await fetch(`${API_BASE}/definition?user_id=${userId}`);
        const data = await response.json();
        
        document.getElementById('definition').textContent = data.definition;
        document.getElementById('definitionBox').classList.remove('hidden');
    } catch (error) {
        showMessage('Failed to load definition.', 'error');
    }
}

async function submitGuess() {
    const guess = document.getElementById('guessInput').value.trim();
    if (!guess || !userId) return;

    try {
        const response = await fetch(`${API_BASE}/guess`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                guess: guess
            })
        });

        const data = await response.json();
        
        updateGameStats(data.score, data.lifes);
        
        if (data.correct) {
            playFeedbackAudio('correct');
            showMessage('Correct! 🎉', 'success');
            document.getElementById('guessInput').value = '';
            document.getElementById('definitionBox').classList.add('hidden');
            
            if (data.end_game) {
                setTimeout(() => showGameOver(data.score, true, null), 1500);
            } else {
                setTimeout(() => playAudio(), 1500);
            }
        } else {
            playFeedbackAudio('incorrect');
            
            if (data.end_game) {
                playFeedbackAudio('lose');
                showMessage(`Wrong! The word was "${data.target_word}". Game Over!`, 'error');
                setTimeout(() => showGameOver(data.score, false, data.target_word), 2000);
            } else {
                showMessage('Wrong! Try again.', 'error');
                document.getElementById('guessInput').value = '';
            }
        }
    } catch (error) {
        showMessage('Failed to submit guess.', 'error');
    }
}

function updateGameStats(score, lives) {
    document.getElementById('score').textContent = score;
    const hearts = '❤️'.repeat(lives) + '🖤'.repeat(3 - lives);
    document.getElementById('lives').textContent = hearts;
}

function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove('hidden');
    
    setTimeout(() => {
        messageDiv.classList.add('hidden');
    }, 3000);
}

function showLoading() {
    document.getElementById('startScreen').classList.add('hidden');
    document.getElementById('loadingScreen').classList.remove('hidden');
}

function showGameOver(score, wonGame, correctWord) {
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('gameOverScreen').classList.remove('hidden');
    document.getElementById('finalScore').textContent = score;
    
    const messageEl = document.getElementById('gameOverMessage');
    if (wonGame) {
        messageEl.innerHTML = 'Congratulations! You completed all words! 🏆';
    } else {
        messageEl.innerHTML = `Better luck next time!<br><br>The correct word was: <strong>"${correctWord}"</strong>`;
    }
}

function goHome() {
    location.reload();
}

async function resetGame() {
    if (!userId) {
        location.reload();
        return;
    }

    try {
        await fetch(`${API_BASE}/reset?user_id=${userId}`, {
            method: 'POST'
        });
        
        document.getElementById('gameOverScreen').classList.add('hidden');
        document.getElementById('gameScreen').classList.remove('hidden');
        document.getElementById('guessInput').value = '';
        document.getElementById('definitionBox').classList.add('hidden');
        updateGameStats(0, 3);
        
        await playAudio();
    } catch (error) {
        showMessage('Failed to reset game.', 'error');
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        submitGuess();
    }
}

// --- Feedback Form Functions ---

function openFeedbackPopup() {
    document.getElementById('feedbackPopup').classList.remove('hidden');
}

function closeFeedbackPopup() {
    document.getElementById('feedbackPopup').classList.add('hidden');
    // Clear status message on close
    const statusDiv = document.getElementById('feedbackStatus');
    statusDiv.classList.add('hidden');
    statusDiv.className = 'feedback-status hidden';
}

document.addEventListener('DOMContentLoaded', () => {
    const feedbackForm = document.getElementById('feedbackForm');
    const statusDiv = document.getElementById('feedbackStatus');
    
    feedbackForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show submitting status
        statusDiv.textContent = 'Sending...';
        statusDiv.className = 'feedback-status info';
        statusDiv.classList.remove('hidden');

        const form = e.target;
        const formData = new FormData(form);
        
        try {
            const response = await fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                statusDiv.textContent = 'Thank you for your feedback! It has been sent.';
                statusDiv.className = 'feedback-status success';
                form.reset(); // Clear the form fields
                setTimeout(closeFeedbackPopup, 3000); // Close after a delay
            } else {
                statusDiv.textContent = 'Oops! There was an issue sending your feedback.';
                statusDiv.className = 'feedback-status error';
            }
        } catch (error) {
            statusDiv.textContent = 'Network error. Please try again.';
            statusDiv.className = 'feedback-status error';
        }
    });
});