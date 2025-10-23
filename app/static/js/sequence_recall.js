// BrainRush: Sequence Recall
let level = 'easy';
let score = 0; 
let seconds = 0;
let isGameActive = false;
let timerInterval;

let currentLength = 0;
let currentSequence = [];
let userSequence = [];
let sequenceDisplayIndex = 0;
let sequenceDisplayInterval;
let recallTimer;
let stage = 'setup';
let displaySpeed = 1500;

function getLevelConfig(level) {
    if (level === 'easy') return { 
        baseTime: 8.0, 
        timeIncrement: 0.8, 
        basePoints: 10, 
        speed: 1500 
    };
    else if (level === 'medium') return { 
        baseTime: 7.0, 
        timeIncrement: 0.7, 
        basePoints: 20,
        speed: 1000 
    };
    return {
        baseTime: 6.0, 
        timeIncrement: 0.6, 
        basePoints: 30,
        speed: 700 
    };
}

function getDisplaySpeedForLevel(level) {
    return getLevelConfig(level).speed;
}

function getRecallTimeLimitForLevelAndLength(level, length) {
    const params = getLevelConfig(level);
    const timeLimit = params.baseTime + ((length - 2) * params.timeIncrement);
    return timeLimit;
}

function calculateRoundPoints(level, length) {
    const config = getLevelConfig(level);
    return config.basePoints + (length - 2) * Math.round(config.basePoints * 0.5);
}


const startBtn = document.getElementById("start-btn");
const finishBtn = document.getElementById("finish-btn");
const restartBtn = document.getElementById("restart-btn");
const levelSelect = document.getElementById("level-select");
const instructionText = document.getElementById("instruction-text");
const numberDisplay = document.getElementById("number-display");
const userInputDisplay = document.getElementById("user-sequence");
const inputArea = document.getElementById("input-area");
const feedback = document.getElementById("feedback");
const submitBtn = document.getElementById("submit-btn");
const clearBtn = document.getElementById("clear-btn");

startBtn.addEventListener("click", startGame);
finishBtn.addEventListener("click", finishGame);
restartBtn.addEventListener("click", restartGame);
submitBtn.addEventListener("click", submitAttempt);
clearBtn.addEventListener("click", () => {
    userSequence = [];
    updateUserInputDisplay();
});

document.querySelectorAll('.btn-number').forEach(button => {
    button.addEventListener("click", (e) => {
        if (stage === 'recalling') {
            userSequence.push(e.target.dataset.value);
            updateUserInputDisplay();
            if (userSequence.length === currentLength) {
                submitAttempt();
            }
        }
    });
});

document.addEventListener("keydown", (e) => {
    if (stage !== 'recalling') return;
    const key = e.key;
    if (key >= '0' && key <= '9') {
        e.preventDefault();
        userSequence.push(key);
        updateUserInputDisplay();
        if (userSequence.length === currentLength) {
            submitAttempt();
        }
    } else if (key === 'Enter') {
        e.preventDefault();
        submitAttempt();
    } else if (key === 'Backspace' || key === 'Delete') {
        e.preventDefault();
        userSequence.pop();
        updateUserInputDisplay();
    }
});



function startGame() {
    level = levelSelect.value;
    score = 0;
    seconds = 0;
    currentLength = 2;
    stage = 'setup';
    isGameActive = true;
    
    displaySpeed = getLevelConfig(level).speed;

    document.getElementById("level-text").textContent = level;
    document.getElementById("points").textContent = score;
    document.getElementById("current-count").textContent = currentLength;
    feedback.textContent = "";

    document.getElementById("setup-area").style.display = "none";
    document.getElementById("game-area").style.display = "block";
    document.getElementById("result-area").style.display = "none";
    
    inputArea.style.display = 'none';
    numberDisplay.textContent = ''; 

    startTimer();
    startRound();
}

function startRound() {
    clearAllTimers();
    userSequence = [];
    updateUserInputDisplay();
    
    document.getElementById("current-count").textContent = currentLength;
    
    currentSequence = generateSequence(currentLength);
    
    prepareToShow(); 
}

function prepareToShow() {
    stage = 'ready';
    instructionText.textContent = `Get Ready for sequence length ${currentLength}...`;
    numberDisplay.textContent = '...';
    
    setTimeout(() => {
        showSequence();
    }, 1000); 
}


function showSequence() {
    stage = 'showing';
    instructionText.textContent = "Memorize the sequence:";
    numberDisplay.textContent = '';
    
    inputArea.style.display = 'none';
    
    sequenceDisplayIndex = 0;
    
    sequenceDisplayInterval = setInterval(displayNextNumber, displaySpeed);
}

function displayNextNumber() {
    if (sequenceDisplayIndex < currentSequence.length) {
        instructionText.textContent = `Number ${sequenceDisplayIndex + 1} of ${currentLength}:`; 
        
        numberDisplay.textContent = currentSequence[sequenceDisplayIndex];
        sequenceDisplayIndex++;
    } else {
        clearInterval(sequenceDisplayInterval);
        hideSequence();
    }
}

function hideSequence() {
    stage = 'recalling';
    
    const timeLimit = getRecallTimeLimitForLevelAndLength(level, currentLength);
    instructionText.textContent = `Enter the sequence (Time limit: ${timeLimit.toFixed(1)}s):`;
    recallTimer = setTimeout(handleRecallTimeout, timeLimit * 1000);
    
    numberDisplay.textContent = '...';
    
    inputArea.style.display = 'grid';
    userInputDisplay.textContent = '';
}

function handleRecallTimeout() {
    if (stage !== 'recalling') return; 

    if (recallTimer) clearTimeout(recallTimer); 
    
    numberDisplay.textContent = 'Time Up!';
    instructionText.textContent = `Time expired!`;
    feedback.textContent = `❌ Time expired! The correct sequence was: ${currentSequence.join('')}`;
    feedback.className = "feedback-fail";
    
    stage = 'finished';
    inputArea.style.display = 'none';
    
    document.getElementById("points").textContent = score;

    setTimeout(() => {
        finishGame();
    }, 3000);
}


function submitAttempt() {
    if (stage !== 'recalling') return;
    
    if (recallTimer) clearTimeout(recallTimer);
    
    const isCorrect = userSequence.join('') === currentSequence.join('');
    
    if (isCorrect) {
        endRound(true);
    } else {
        endRound(false);
    }
}

function endRound(isSuccess) {
    stage = 'finished';
    inputArea.style.display = 'none';
    
    if (isSuccess) {
        const pointsGained = calculateRoundPoints(level, currentLength);
        score += pointsGained;

        feedback.textContent = `✅ Correct! Sequence Length: ${currentLength}. +${pointsGained} points!`;
        feedback.className = "feedback-success";
        
        currentLength++;
        document.getElementById("points").textContent = score;
        
        setTimeout(() => {
            feedback.textContent = "";
            startRound();
        }, 1500);
        
    } else {
        feedback.textContent = `❌ Incorrect! The correct sequence was: ${currentSequence.join(' ')}`;
        feedback.className = "feedback-fail";
        
        document.getElementById("points").textContent = score;
        
        setTimeout(() => {
            finishGame();
        }, 3000);
    }
}


function generateSequence(length) {
    const sequence = [];
    for (let i = 0; i < length; i++) {
        sequence.push(Math.floor(Math.random() * 10).toString());
    }
    return sequence;
}

function updateUserInputDisplay() {
    userInputDisplay.textContent = userSequence.join(' '); 
}

function clearAllTimers() {
    if (sequenceDisplayInterval) clearInterval(sequenceDisplayInterval);
    if (recallTimer) clearTimeout(recallTimer); 
}


function startTimer() {
    clearInterval(timerInterval);
    seconds = 0;
    document.getElementById("time").textContent = seconds; 
    timerInterval = setInterval(() => {
        seconds++;
        document.getElementById("time").textContent = seconds;
    }, 1000);
}

function finishGame(silent = false) {
    if (!isGameActive) return;
    isGameActive = false;
    clearInterval(timerInterval);
    clearAllTimers();
    
    document.getElementById("game-area").style.display = "none";
    if (!silent) {
        document.getElementById("result-area").style.display = "block";
        document.getElementById("final-score").textContent = score;
        document.getElementById("final-time").textContent = seconds;

        fetch("/game/sequence_recall/save_result", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                level: level,
                score: score,
                time: seconds,
                rounds: currentLength - 1
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Result for Sequence Recall has been saved", data);
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