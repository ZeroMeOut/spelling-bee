let userId = null;
let currentAudio = null;
const API_BASE = window.location.origin;

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
            showMessage('Correct! 🎉', 'success');
            document.getElementById('guessInput').value = '';
            document.getElementById('definitionBox').classList.add('hidden');
            
            if (data.end_game) {
                setTimeout(() => showGameOver(data.score, true), 1500);
            } else {
                setTimeout(() => playAudio(), 1500);
            }
        } else {
            if (data.end_game) {
                showMessage(`Wrong! The word was "${data.target_word}". Game Over!`, 'error');
                setTimeout(() => showGameOver(data.score, false), 2000);
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

function showGameOver(score, wonGame) {
    document.getElementById('gameScreen').classList.add('hidden');
    document.getElementById('gameOverScreen').classList.remove('hidden');
    document.getElementById('finalScore').textContent = score;
    
    const message = wonGame 
        ? 'Congratulations! You completed all words! 🏆' 
        : 'Better luck next time!';
    document.getElementById('gameOverMessage').textContent = message;
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