let level = 'easy';
let score = 0;
let isGameActive = false;
let totalTimeTaken = 0;
let roundStartTime;
let roundTimerInterval; 
let timeLeft = 0;

let currentLength = 2;
let currentSequence = [];
let userSequence = [];
let isShowingSequence = false;
let isRecalling = false;

const LEVEL_CONFIGS = {
    easy: { gridSize: 3, speed: 700, basePoints: 5, timeLimit: 9}, 
    medium: { gridSize: 4, speed: 500, basePoints: 8, timeLimit: 7},
    hard: { gridSize: 5, speed: 300, basePoints: 13, timeLimit: 5}
};

const startBtn = document.getElementById("start-btn");
const restartBtn = document.getElementById("restart-btn");
const levelSelect = document.getElementById("level-select");
const gridContainer = document.getElementById("grid-container");
const instructionText = document.getElementById("instruction-text");
const currentLengthEl = document.getElementById("current-length");
const scoreEl = document.getElementById("score");
const feedbackEl = document.getElementById("feedback");
const submitBtn = document.getElementById("submit-btn");
const actionArea = document.getElementById("action-area");
const timeLeftEl = document.getElementById("time-left");

startBtn.addEventListener("click", startGame);
restartBtn.addEventListener("click", restartGame);
gridContainer.addEventListener("click", handleCellClick);
submitBtn.addEventListener("click", submitAttempt);



function generateGrid(gridSize) {
    gridContainer.innerHTML = '';
    gridContainer.style.gridTemplateColumns = `repeat(${gridSize}, 1fr)`; 
    
    for (let r = 0; r < gridSize; r++) {
        for (let c = 0; c < gridSize; c++) {
            const cell = document.createElement('div');
            cell.className = 'grid-cell';
            cell.dataset.row = r;
            cell.dataset.col = c;
            gridContainer.appendChild(cell);
        }
    }
}

function updateUIForRecalling() {
    instructionText.textContent = `Your turn! Tap the sequence. Time left: ${timeLeft}s`;
    actionArea.style.display = 'block';
    submitBtn.disabled = userSequence.length !== currentLength;
    gridContainer.classList.add('recalling');
}

function updateUIForShowing() {
    instructionText.textContent = "Watch carefully...";
    actionArea.style.display = 'none';
    gridContainer.classList.remove('recalling');
    timeLeftEl.textContent = '-';
}

function clearRoundTimer() {
    if (roundTimerInterval) {
        clearInterval(roundTimerInterval);
        roundTimerInterval = null;
    }
}

function startRoundTimer() {
    clearRoundTimer();
    const config = LEVEL_CONFIGS[level];
    
    const baseTime = config.timeLimit;
    const timeIncrement = 1.2;
    
    timeLeft = Math.floor(baseTime + (currentLength - 2) * timeIncrement);
    timeLeftEl.textContent = timeLeft;

    roundTimerInterval = setInterval(() => {
        timeLeft--;
        timeLeftEl.textContent = timeLeft;
        
        if (timeLeft <= 0) {
            clearRoundTimer();
            setTimeout(handleTimeout, 100); 
        }
    }, 1000);
}

function handleTimeout() {
    if (!isGameActive || !isRecalling) return;
    
    isRecalling = false;
    actionArea.style.display = 'none';
    
    feedbackEl.textContent = `Time expired! Sequence length was ${currentLength}. Game Over.`;
    feedbackEl.classList.add('feedback-fail');
    
    setTimeout(finishGame, 2000);
}

function startGame() {
    level = levelSelect.value;
    const config = LEVEL_CONFIGS[level];

    score = 0;
    currentLength = 2;
    totalTimeTaken = 0;
    isGameActive = true;
    
    scoreEl.textContent = score;
    currentLengthEl.textContent = currentLength;
    feedbackEl.textContent = "";
    feedbackEl.className = '';
    timeLeftEl.textContent = '0';

    document.getElementById("level-text").textContent = level;
    document.getElementById("setup-area").style.display = "none";
    document.getElementById("game-area").style.display = "block";
    document.getElementById("result-area").style.display = "none";
    
    generateGrid(config.gridSize);
    
    startRound();
}

function startRound() {
    clearRoundTimer();
    isRecalling = false;
    userSequence = [];
    currentLengthEl.textContent = currentLength;
    
    currentSequence = generateSequence(LEVEL_CONFIGS[level].gridSize, currentLength);
    
    updateUIForShowing();
    setTimeout(showSequence, 1000); 
}

function generateSequence(gridSize, length) {
    const sequence = [];
    for (let i = 0; i < length; i++) {
        const r = Math.floor(Math.random() * gridSize);
        const c = Math.floor(Math.random() * gridSize);
        sequence.push([r, c]);
    }
    return sequence;
}

function showSequence() {
    isShowingSequence = true;
    const config = LEVEL_CONFIGS[level];
    let index = 0;

    const interval = setInterval(() => {
        if (index > 0) {
            const [pr, pc] = currentSequence[index - 1];
            const prevCell = document.querySelector(`[data-row="${pr}"][data-col="${pc}"]`);
            if (prevCell) prevCell.classList.remove('active');
        }
        
        if (index < currentSequence.length) {
            const [r, c] = currentSequence[index];
            const currentCell = document.querySelector(`[data-row="${r}"][data-col="${c}"]`);
            if (currentCell) currentCell.classList.add('active');
            
            index++;
        } else {
            clearInterval(interval);
            isShowingSequence = false;
            
            const [lr, lc] = currentSequence[currentSequence.length - 1];
            const lastCell = document.querySelector(`[data-row="${lr}"][data-col="${lc}"]`);
            if (lastCell) setTimeout(() => lastCell.classList.remove('active'), config.speed);
            
            roundStartTime = performance.now();
            isRecalling = true;
            startRoundTimer();
            updateUIForRecalling();
        }
    }, config.speed);
}


function handleCellClick(event) {
    if (!isGameActive || !isRecalling) return;
    const cell = event.target;
    if (!cell.classList.contains('grid-cell')) return;

    const r = parseInt(cell.dataset.row);
    const c = parseInt(cell.dataset.col);
    const pos = [r, c];
    
    userSequence.push(pos);
    
    cell.classList.add('user-tap');
    setTimeout(() => cell.classList.remove('user-tap'), 150);
    
    updateUIForRecalling();
    
    if (userSequence.length === currentLength) {
        submitAttempt();
    }
}

function submitAttempt() {
    if (!isRecalling) return;
    
    clearRoundTimer();
    
    isRecalling = false;
    actionArea.style.display = 'none';

    const timeTaken = (performance.now() - roundStartTime) / 1000;
    
    let isCorrect = true;
    for (let i = 0; i < currentLength; i++) {
        const seqCell = currentSequence[i];
        const userCell = userSequence[i];
        
        if (!userCell || seqCell[0] !== userCell[0] || seqCell[1] !== userCell[1]) {
            isCorrect = false;
            break;
        }
    }
    
    if (isCorrect) {
        const config = LEVEL_CONFIGS[level];
        const points = config.basePoints + (currentLength * 10); 
        score += points;
        totalTimeTaken += timeTaken;

        scoreEl.textContent = score;
        feedbackEl.textContent = `Correct! (+${points} pts)`;
        feedbackEl.classList.add('feedback-success');
        
        currentLength++; 
        
        setTimeout(startRound, 1000);
    } else {
        feedbackEl.textContent = `Incorrect! Game Over.`;
        feedbackEl.classList.add('feedback-fail');
        
        setTimeout(finishGame, 2000);
    }
}

function finishGame(silent = false) {
    if (!isGameActive) return;
    isGameActive = false;
    isRecalling = false;
    isShowingSequence = false;
    
    clearRoundTimer(); 
    
    document.querySelectorAll('.grid-cell').forEach(cell => cell.classList.remove('active', 'user-tap'));
    
    document.getElementById("game-area").style.display = "none";
    
    if (!silent) {
        const finalLength = currentLength - 1; 
        const avgTime = finalLength > 1 ? (totalTimeTaken / finalLength) : 0;
        
        document.getElementById("result-area").style.display = "block";
        document.getElementById("final-score").textContent = score;
        document.getElementById("final-length").textContent = finalLength;

        fetch("/game/tapping_memory/save_result", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                level: level,
                score: score,
                time: totalTimeTaken,
                rounds: finalLength, 
                avg_time: avgTime.toFixed(2)
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Result for Tapping Memory has been saved", data);
        })
        .catch(error => {
            console.error("Error saving game result:", error);
        });
    } else {
        document.getElementById("setup-area").style.display = "block";
    }
}

function restartGame() {
    document.getElementById("setup-area").style.display = "block";
    document.getElementById("result-area").style.display = "none";
}