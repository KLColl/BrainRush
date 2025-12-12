// BrainRush: Color Rush
let score = 0;
let round = 0;
let seconds = 0;
let timerInterval;
let roundStartTime;
let isGameActive = false;
let correctColor = ''; 
let level = 'easy';
let roundTimerTimeout;
let isRoundActive = false;

const MAX_ROUNDS = 10;
const COLOR_OPTIONS_ALL = [
    { name: 'RED', css: 'red' },
    { name: 'GREEN', css: 'green' },
    { name: 'BLUE', css: 'blue' },
    { name: 'ORANGE', css: 'orange' },
    { name: 'PURPLE', css: 'purple' },
    { name: 'BROWN', css: 'brown' },
    { name: 'PINK', css: 'deeppink' },
    { name: 'CYAN', css: 'cyan' }
];

const LEVEL_CONFIGS = {
    easy: { colorCount: 4, timeLimit: 5, baseScore: 10, penalty: 5 },
    medium: { colorCount: 6, timeLimit: 4, baseScore: 20, penalty: 10 },
    hard: { colorCount: 8, timeLimit: 2.5, baseScore: 30, penalty: 15 }
};

const startBtn = document.getElementById("start-btn");
const restartBtn = document.getElementById("restart-btn");
const levelSelect = document.getElementById("level-select");
const colorWordEl = document.getElementById("color-word");
const scoreEl = document.getElementById("score");
const timeEl = document.getElementById("time");
const roundEl = document.getElementById("current-round");
const feedbackEl = document.getElementById("feedback");
const answerButtonsContainer = document.getElementById("answer-buttons");

startBtn.addEventListener("click", startGame);
restartBtn.addEventListener("click", restartGame);

answerButtonsContainer.addEventListener("click", (e) => {
    if (e.target.classList.contains('color-choice')) {
        handleAnswer(e);
    }
});

// Автозбереження
window.addEventListener("beforeunload", () => {
    if (isGameActive) finishGame(true);
});

function startGame() {
    level = levelSelect.value;
    score = 0;
    round = 0;
    seconds = 0;
    isGameActive = true;

    document.getElementById("setup-area").style.display = "none";
    document.getElementById("game-area").style.display = "block";
    document.getElementById("result-area").style.display = "none";

    scoreEl.textContent = score;
    roundEl.textContent = `${round}/${MAX_ROUNDS}`;
    feedbackEl.textContent = "";

    generateAnswerButtons(LEVEL_CONFIGS[level].colorCount);

    startTimer();
    startRound();
}

function generateAnswerButtons(count) {
    // Створення кнопок з кольорами
    answerButtonsContainer.innerHTML = '';
    const availableColors = COLOR_OPTIONS_ALL.slice(0, count);
    
    shuffleArray(availableColors);

    availableColors.forEach(color => {
        const button = document.createElement('button');
        button.className = 'btn color-choice';
        button.dataset.color = color.name;
        button.textContent = color.name;
        answerButtonsContainer.appendChild(button);
    });
}

function startRound() {
    if (round >= MAX_ROUNDS) {
        finishGame();
        return;
    }

    if (roundTimerTimeout) clearTimeout(roundTimerTimeout);

    round++;
    roundEl.textContent = `${round}/${MAX_ROUNDS}`;

    // Генеруємо слово одним кольором, показуємо іншим
    const { word, color } = generateProblem();
    correctColor = color; 

    colorWordEl.textContent = word;
    colorWordEl.style.color = color;
    
    feedbackEl.textContent = "Click the font color.";
    roundStartTime = performance.now(); 

    isRoundActive = true;

    const timeLimitMs = LEVEL_CONFIGS[level].timeLimit * 1000;
    roundTimerTimeout = setTimeout(handleTimeout, timeLimitMs);
}

function handleAnswer(event) {
    if (!isGameActive || !isRoundActive) return;

    isRoundActive = false;

    if (roundTimerTimeout) clearTimeout(roundTimerTimeout);

    const userAnswer = event.target.dataset.color;
    const isCorrect = (userAnswer.toLowerCase() === correctColor.toLowerCase());

    if (isCorrect) {
        const timeTaken = (performance.now() - roundStartTime) / 1000;
        
        const roundScore = calculateScoreForTime(level, timeTaken);
        score += roundScore;
        scoreEl.textContent = score;
        
        feedbackEl.textContent = `✅ Correct! (+${roundScore} pts in ${timeTaken.toFixed(2)}s)`;
        feedbackEl.style.color = "green";
        
        setTimeout(() => {
            startRound();
        }, 500); 

    } else {
        const penalty = LEVEL_CONFIGS[level].penalty;
        score = Math.max(0, score - penalty);
        scoreEl.textContent = score;

        feedbackEl.textContent = `❌ Incorrect! -${penalty} pts. Game Over.`;
        feedbackEl.style.color = "red";
        finishGame(); 
    }
}

function handleTimeout() {
    if (!isGameActive || !isRoundActive) return;

    isRoundActive = false;

    const penalty = LEVEL_CONFIGS[level].penalty;
    score = Math.max(0, score - penalty);
    scoreEl.textContent = score;

    feedbackEl.textContent = `⏰ Time's up! -${penalty} pts.`;
    feedbackEl.style.color = "orange";
    
    setTimeout(() => {
        if (round >= MAX_ROUNDS) {
            finishGame();
        } else {
            startRound();
        }
    }, 1000);
}

function generateProblem() {
    const availableOptions = COLOR_OPTIONS_ALL.slice(0, LEVEL_CONFIGS[level].colorCount);
    
    const wordOption = getRandomElement(availableOptions);
    
    const colorOption = getRandomElement(availableOptions);
    
    return { 
        word: wordOption.name, 
        color: colorOption.css 
    };
}

function calculateScoreForTime(level, timeTaken) {
    // Бонус за швидкість
    const config = LEVEL_CONFIGS[level];
    const base = config.baseScore;
    const limit = config.timeLimit;

    const bonusFactor = Math.max(0, (limit - timeTaken) / limit); 
    const gained = Math.round(base + bonusFactor * base / 2);

    return Math.max(Math.round(base / 2), gained);
}

function getRandomElement(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function startTimer() {
    clearInterval(timerInterval);
    seconds = 0;
    timerInterval = setInterval(() => {
        seconds++;
        timeEl.textContent = seconds;
    }, 1000);
}

function finishGame(silent = false) {
    if (!isGameActive) return;
    isGameActive = false;
    clearInterval(timerInterval);
    if (roundTimerTimeout) clearTimeout(roundTimerTimeout); 

    if (!silent) {
        document.getElementById("game-area").style.display = "none";
        document.getElementById("result-area").style.display = "block";
        document.getElementById("final-score").textContent = score;
        document.getElementById("final-time").textContent = seconds;
        
        saveResultToServer(score, seconds, MAX_ROUNDS, level); 
    } else {
        document.getElementById("setup-area").style.display = "block";
    }
}

function restartGame() {
    document.getElementById("setup-area").style.display = "block";
    document.getElementById("result-area").style.display = "none";
}

function saveResultToServer(finalScore, finalTime, totalRounds, gameLevel) {
    fetch("/game/color_rush/save_result", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            level: gameLevel,
            score: finalScore,
            time: finalTime,
            rounds: totalRounds
        })
    })
    .then(response => {
        if (!response.ok) {
            console.error("Failed to save result. Status:", response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log("Result saved successfully:", data);
    })
    .catch(error => {
        console.error("Error during fetch operation:", error);
    });
}