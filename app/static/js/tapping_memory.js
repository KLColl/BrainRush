// BrainRush: Tapping Memory
let level = 'easy';
let score = 0;
let isGameActive = false;
let totalTimeTaken = 0;
let roundStartTime;
let roundTimerInterval = null;
let displayUpdateInterval = null;
let timeLeft = 0;

let currentLength = 2;
let currentSequence = [];
let userSequence = [];
let isShowingSequence = false;
let isRecalling = false;
let sequenceInterval = null;

const LEVEL_CONFIGS = {
    easy: { gridSize: 3, speed: 700, basePoints: 5, timeLimit: 9 },
    medium: { gridSize: 4, speed: 500, basePoints: 8, timeLimit: 7 },
    hard: { gridSize: 5, speed: 300, basePoints: 13, timeLimit: 5 }
};

let startBtn, restartBtn, levelSelect, gridContainer, instructionText, currentLengthEl, scoreEl, feedbackEl, submitBtn, actionArea, timeLeftEl;
let playAgainBtn, resultLevelSelect;

document.addEventListener('DOMContentLoaded', () => {
    startBtn = document.getElementById("start-btn");
    restartBtn = document.getElementById("restart-btn");
    levelSelect = document.getElementById("level-select");
    gridContainer = document.getElementById("grid-container");
    instructionText = document.getElementById("instruction-text");
    currentLengthEl = document.getElementById("current-length");
    scoreEl = document.getElementById("score");
    feedbackEl = document.getElementById("feedback");
    submitBtn = document.getElementById("submit-btn");
    actionArea = document.getElementById("action-area");
    timeLeftEl = document.getElementById("time-left");
    playAgainBtn = document.getElementById("play-again-btn");
    resultLevelSelect = document.getElementById("result-level-select");

    if (!startBtn) return console.error("Tapping Memory: start-btn not found");

    startBtn.addEventListener("click", () => startGame());
    if (restartBtn) restartBtn.addEventListener("click", restartGame);
    if (gridContainer) gridContainer.addEventListener("click", handleCellClick);
    if (submitBtn) submitBtn.addEventListener("click", submitAttempt);

    if (playAgainBtn) {
        playAgainBtn.addEventListener("click", () => {
            const chosen = (resultLevelSelect && resultLevelSelect.value) ? resultLevelSelect.value : (levelSelect && levelSelect.value ? levelSelect.value : 'easy');
            if (levelSelect) levelSelect.value = chosen;
            const resultArea = document.getElementById("result-area");
            if (resultArea) resultArea.style.display = "none";
            startGame();
        });
    }
});

function generateGrid(gridSize) {
    if (!gridContainer) return;
    gridContainer.innerHTML = '';
    gridContainer.style.gridTemplateColumns = `repeat(${gridSize}, 1fr)`;

    for (let r = 0; r < gridSize; r++) {
        for (let c = 0; c < gridSize; c++) {
            const cell = document.createElement('div');
            cell.className = 'grid-cell';
            cell.dataset.row = r;
            cell.dataset.col = c;
            cell.tabIndex = 0; 
            gridContainer.appendChild(cell);
        }
    }
}

function updateUIForRecalling() {
    if (instructionText) instructionText.textContent = `Your turn! Tap the sequence. Time left: ${timeLeft}s`;
    if (actionArea) actionArea.style.display = 'block';
    if (submitBtn) submitBtn.disabled = (userSequence.length !== currentLength);
    if (gridContainer) gridContainer.classList.add('recalling');
}

function updateUIForShowing() {
    if (instructionText) instructionText.textContent = "Watch carefully...";
    if (actionArea) actionArea.style.display = 'none';
    if (gridContainer) gridContainer.classList.remove('recalling');
    if (timeLeftEl) timeLeftEl.textContent = '-';
}

function clearRoundTimer() {
    if (roundTimerInterval) {
        clearInterval(roundTimerInterval);
        roundTimerInterval = null;
    }
    if (displayUpdateInterval) {
        clearInterval(displayUpdateInterval);
        displayUpdateInterval = null;
    }
    if (sequenceInterval) {
        clearInterval(sequenceInterval);
        sequenceInterval = null;
    }
}

function startRoundTimer() {
    clearRoundTimer();
    const config = LEVEL_CONFIGS[level];
    const baseTime = config.timeLimit;
    const timeIncrement = 1.2;

    timeLeft = Math.floor(baseTime + (currentLength - 2) * timeIncrement);
    if (timeLeftEl) timeLeftEl.textContent = timeLeft;

    roundTimerInterval = setInterval(() => {
        timeLeft--;
        if (timeLeft <= 0) {
            timeLeft = 0;
            if (timeLeftEl) timeLeftEl.textContent = timeLeft;
            updateInstructionTime()
            clearRoundTimer();
            setTimeout(handleTimeout, 100);
            return;
        }
        if (timeLeftEl) timeLeftEl.textContent = timeLeft;
        updateInstructionTime()
    }, 1000);

    displayUpdateInterval = setInterval(() => {
        if (timeLeftEl) timeLeftEl.textContent = timeLeft;
    }, 500);
}
function updateInstructionTime() {
    if (instructionText && isRecalling) {
        instructionText.textContent = `Your turn! Tap the sequence. Time left: ${timeLeft}s`;
    }
}

function handleTimeout() {
    if (!isGameActive || !isRecalling) return;

    isRecalling = false;
    if (actionArea) actionArea.style.display = 'none';

    if (feedbackEl) {
        feedbackEl.textContent = `⏰ Time expired! Sequence length was ${currentLength}.`;
        feedbackEl.classList.add('feedback-fail');
    }

    setTimeout(finishGame, 900);
}

function startGame() {
    level = (levelSelect && levelSelect.value) ? levelSelect.value : level;
    const config = LEVEL_CONFIGS[level] || LEVEL_CONFIGS.easy;

    score = 0;
    currentLength = 2;
    totalTimeTaken = 0;
    isGameActive = true;

    if (scoreEl) scoreEl.textContent = score;
    if (currentLengthEl) currentLengthEl.textContent = currentLength;
    if (feedbackEl) { feedbackEl.textContent = ""; feedbackEl.className = "feedback"; }
    if (timeLeftEl) timeLeftEl.textContent = '0';

    const setup = document.getElementById("setup-area");
    const gameArea = document.getElementById("game-area");
    const resultArea = document.getElementById("result-area");
    if (setup) setup.style.display = "none";
    if (gameArea) gameArea.style.display = "block";
    if (resultArea) resultArea.style.display = "none";

    generateGrid(config.gridSize);

    startRound();
}

function startRound() {
    clearRoundTimer();
    isRecalling = false;
    userSequence = [];
    if (currentLengthEl) currentLengthEl.textContent = currentLength;

    currentSequence = generateSequence(LEVEL_CONFIGS[level].gridSize, currentLength);

    updateUIForShowing();
    setTimeout(showSequence, 700);
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

    sequenceInterval = setInterval(() => {
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
            clearInterval(sequenceInterval);
            sequenceInterval = null;
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
    if (actionArea) actionArea.style.display = 'none';

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

        if (scoreEl) scoreEl.textContent = score;
        if (feedbackEl) {
            feedbackEl.textContent = `✅ Correct! (+${points} pts)`;
            feedbackEl.classList.add('feedback-success');
        }

        currentLength++;

        setTimeout(startRound, 700);
    } else {
        if (feedbackEl) {
            feedbackEl.textContent = `❌ Incorrect! Game Over.`;
            feedbackEl.classList.add('feedback-fail');
        }

        setTimeout(finishGame, 900);
    }
}

function finishGame(silent = false) {
    if (!isGameActive) return;
    isGameActive = false;
    isRecalling = false;
    isShowingSequence = false;

    clearRoundTimer();

    document.querySelectorAll('.grid-cell').forEach(cell => cell.classList.remove('active', 'user-tap'));

    const gameArea = document.getElementById("game-area");
    if (gameArea) gameArea.style.display = "none";

    if (!silent) {
        const finalLength = Math.max(0, currentLength - 1);
        const avgTime = finalLength > 0 ? (totalTimeTaken / finalLength) : 0;

        const resultArea = document.getElementById("result-area");
        if (resultArea) resultArea.style.display = "block";

        const finalScoreEl = document.getElementById("final-score");
        const finalLengthEl = document.getElementById("final-length");
        if (finalScoreEl) finalScoreEl.textContent = score;
        if (finalLengthEl) finalLengthEl.textContent = finalLength;

        if (resultLevelSelect) resultLevelSelect.value = level;

        fetch("/game/tapping_memory/save_result", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ level: level, score: score, time: totalTimeTaken, rounds: finalLength, avg_time: avgTime.toFixed(2) })
        }).catch(() => { });
    } else {
        const setup = document.getElementById("setup-area");
        if (setup) setup.style.display = "block";
    }
}

function restartGame() {
    const setup = document.getElementById("setup-area");
    const resultArea = document.getElementById("result-area");
    if (resultArea) resultArea.style.display = "none";
    if (setup) setup.style.display = "block";
}
