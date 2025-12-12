// BrainRush: Arithmetic
let currentProblem = null;
let level = 'easy';
let score = 0;
let timerInterval;
let seconds = 0;
let totalProblems = 0;
let currentCount = 0;
let isGameActive = false;
let questionStartTime = 0;
let questionTimer = null;

const startBtn = document.getElementById("start-btn");
const submitBtn = document.getElementById("submit-btn");
const answerInput = document.getElementById("answer-input");
const levelSelect = document.getElementById("level-select");
const finishBtn = document.getElementById("finish-btn");
const restartBtn = document.getElementById("restart-btn");

startBtn.addEventListener("click", startGame);
submitBtn.addEventListener("click", checkAnswer);
finishBtn.addEventListener("click", finishGame);
restartBtn.addEventListener("click", restartGame);

// Enter для відправки відповіді
answerInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        checkAnswer();
    }
});

// Автозбереження при закритті
window.addEventListener("beforeunload", () => {
    if (isGameActive) finishGame(true);
});

function startGame() {
    level = levelSelect.value;
    score = 0;
    seconds = 0;
    currentCount = 0;

    const countSelect = document.getElementById("count-select")
    totalProblems = parseInt(countSelect.value) || 5;

    isGameActive = true;

    // Оновлення UI
    document.getElementById("level-text").textContent = level;
    document.getElementById("points").textContent = score;
    document.getElementById("feedback").textContent = "";
    document.getElementById("current-count").textContent = currentCount;
    document.getElementById("total-count").textContent = totalProblems;

    document.getElementById("setup-area").style.display = "none";
    document.getElementById("game-area").style.display = "block";
    document.getElementById("result-area").style.display = "none";

    startTimer();
    nextProblem();
}

function startTimer() {
    clearInterval(timerInterval);
    seconds = 0;
    timerInterval = setInterval(() => {
        seconds++;
        document.getElementById("time").textContent = seconds;
    }, 1000);
}

function nextProblem() {
    // Генерація наступного прикладу
    if (currentCount >= totalProblems) {
        finishGame();
        return;
    }
    if (questionTimer) clearTimeout(questionTimer);

    currentProblem = generateProblem();
    currentCount++;
    document.getElementById("problem").textContent = currentProblem.expression;
    document.getElementById("current-count").textContent = currentCount;
    answerInput.value = "";
    answerInput.focus();

    questionStartTime = Date.now();

    // Таймер на відповідь
    let timeLimit = getTimeLimitForLevel();
    questionTimer = setTimeout(() => {
        handleTimeout()
    }, timeLimit * 1000)
}

function checkAnswer() {
    // Перевірка відповіді користувача
    if (!isGameActive) return;
    const userAnswer = parseFloat(answerInput.value);
    if (isNaN(userAnswer)) return;

    if (questionTimer) clearTimeout(questionTimer);

    const feedback = document.getElementById("feedback");
    const correctAnswer = Math.round(currentProblem.answer * 10) / 10;

    // diapason: +-0.1
    const isCorrect = Math.abs(userAnswer - correctAnswer) <= 0.1;

    if (isCorrect) {
        const timeTaken = (Date.now() - questionStartTime) / 1000;
        const gained = calculateScoreForTime(level, timeTaken);
        score += gained;
        feedback.textContent = `✅ Correct! +${gained} points (${timeTaken.toFixed(1)}s)`;
        feedback.style.color = "green";
    } else {
        const penalty = Math.round(getBasePoints(level) / 2);
        score -= penalty;
        feedback.textContent = `❌ Incorrect!(${ currentProblem.answer }) - ${ penalty }`;
        feedback.style.color = "red";
    }

    document.getElementById("points").textContent = score;

    setTimeout(() => {
        feedback.textContent = "";
        nextProblem();
    }, 700);
}
function handleTimeout() {
    const feedback = document.getElementById("feedback");
    const penalty = Math.round(getBasePoints(level) / 2);
    score -= penalty;
    document.getElementById("points").textContent = score;
    feedback.textContent = `⏰ Time's up! -${penalty}`;
    feedback.style.color = "orange";

    setTimeout(() => {
        feedback.textContent = "";
        nextProblem();
    }, 1000);
}

function finishGame(silent = false) {
    if (!isGameActive) return;
    isGameActive = false;
    clearInterval(timerInterval);

    document.getElementById("game-area").style.display = "none";
    if (!silent) {
        document.getElementById("result-area").style.display = "block";
        document.getElementById("final-score").textContent = score;
        document.getElementById("final-time").textContent = seconds;

        // Відправка результату на сервер
        fetch("/game/arithmetic/save_result", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                level: level,
                score: score,
                time: seconds,
                rounds: totalProblems
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Result has been saved")
        })
    } else {
        document.getElementById("setup-area").style.display = "block";
    }
}

function restartGame() {
    document.getElementById("setup-area").style.display = "block";
    document.getElementById("result-area").style.display = "none";
}

function generateProblem() {
    let a, b, op, expression, answer;
    const opsEasy = ['+', '-'];
    const opsMedium = ['+', '-', '*'];
    const opsHard = ['+', '-', '*', '/'];

    if (level === 'easy') {
        a = randInt(1, 50);
        b = randInt(1, 50);
        op = randomChoice(opsEasy);
        expression = `${a} ${op} ${b}`;
        answer = Math.round(eval(expression) * 10) / 10; // 0.1
    } else if (level === 'medium') {
        a = randInt(5, 50);
        b = randInt(5, 50);
        let c = randInt(5, 20);
        let op1 = randomChoice(opsMedium);
        if (op1 === '*') b = randInt(1, 10);
        let op2 = randomChoice(opsMedium);
        if (op2 === '*') c = randInt(3, 12);
        expression = `${a} ${op1} ${b} ${op2} ${c}`;
        answer = Math.round(eval(expression) * 10) / 10;
    } else {
        a = randInt(10, 100);
        b = randInt(10, 100);
        let c = randInt(5, 25);
        let d = randInt(1, 10);
        let op1 = randomChoice(opsHard);
        if (op1 === '*') b = randInt(2, 4);
        else if (op1 === '/') b = randInt(2, 3);
        let op2 = randomChoice(opsHard);
        if (op2 === '*') c = randInt(2, 6);
        else if (op2 === '/') c = randInt(2, 5);
        let op3 = randomChoice(opsHard);
        if (op3 === '*') d = randInt(2, 10);
        else if (op3 === '/') d = randInt(2, 5);
        expression = `(${a} ${op1} ${b}) ${op2} (${c} ${op3} ${d})`;
        answer = Math.round(eval(expression) * 10) / 10;
    }

    return { expression, answer };
}

function randInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomChoice(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function getTimeLimitForLevel() {
    if (level === 'easy') return 10;
    if (level === 'medium') return 20;
    return 45;
}

function getBasePoints(level) {
    if (level === 'easy') return 5;
    if (level === 'medium') return 10;
    return 20;
}

function calculateScoreForTime(level, timeTaken) {
    const base = getBasePoints(level);
    const limit = getTimeLimitForLevel();
    const bonusFactor = Math.max(0, (limit - timeTaken) / limit);
    const gained = Math.round(base + bonusFactor * base * 2);
    return Math.max(base, gained);
}
