#!/usr/bin/env node
// ═══════════════════════════════════════════════════════════════
// CHITIN-611 — Headless Training Runner
// Plays the crab game against itself. No canvas needed.
// Saves trained profile to chitin611.json for browser loading.
// ═══════════════════════════════════════════════════════════════

const fs = require('fs');
const path = require('path');

// ── Chitin611 Neural Network ──
class Chitin611 {
    constructor(inputSize, hiddenSize, outputSize) {
        this.inputSize = inputSize;
        this.hiddenSize = hiddenSize;
        this.outputSize = outputSize;
        this.W1 = this.randMatrix(hiddenSize, inputSize, Math.sqrt(2 / inputSize));
        this.b1 = new Array(hiddenSize).fill(0);
        this.W2 = this.randMatrix(outputSize, hiddenSize, Math.sqrt(2 / hiddenSize));
        this.b2 = new Array(outputSize).fill(0);
        this.mW1 = this.zeros(hiddenSize, inputSize);
        this.vW1 = this.zeros(hiddenSize, inputSize);
        this.mW2 = this.zeros(outputSize, hiddenSize);
        this.vW2 = this.zeros(outputSize, hiddenSize);
        this.mb1 = new Array(hiddenSize).fill(0);
        this.vb1 = new Array(hiddenSize).fill(0);
        this.mb2 = new Array(outputSize).fill(0);
        this.vb2 = new Array(outputSize).fill(0);
        this.t = 0;
    }
    zeros(r, c) { return Array.from({length: r}, () => new Array(c).fill(0)); }
    randMatrix(r, c, scale) {
        return Array.from({length: r}, () =>
            Array.from({length: c}, () => (Math.random() * 2 - 1) * scale)
        );
    }
    forward(input) {
        this.a1 = [];
        for (let i = 0; i < this.hiddenSize; i++) {
            let sum = this.b1[i];
            for (let j = 0; j < this.inputSize; j++) sum += this.W1[i][j] * input[j];
            this.a1.push(Math.tanh(sum));
        }
        this.a2 = [];
        for (let i = 0; i < this.outputSize; i++) {
            let sum = this.b2[i];
            for (let j = 0; j < this.hiddenSize; j++) sum += this.W2[i][j] * this.a1[j];
            this.a2.push(Math.tanh(sum));
        }
        return this.a2;
    }
    backward(input, targets, lr) {
        this.t++;
        const beta1 = 0.9, beta2 = 0.999, eps = 1e-8;
        const dO = [];
        for (let i = 0; i < this.outputSize; i++) {
            dO.push((this.a2[i] - targets[i]) * (1 - this.a2[i] * this.a2[i]));
        }
        const dH = [];
        for (let j = 0; j < this.hiddenSize; j++) {
            let sum = 0;
            for (let i = 0; i < this.outputSize; i++) sum += this.W2[i][j] * dO[i];
            dH.push(sum * (1 - this.a1[j] * this.a1[j]));
        }
        for (let i = 0; i < this.outputSize; i++) {
            for (let j = 0; j < this.hiddenSize; j++) {
                const g = dO[i] * this.a1[j];
                this.mW2[i][j] = beta1 * this.mW2[i][j] + (1 - beta1) * g;
                this.vW2[i][j] = beta2 * this.vW2[i][j] + (1 - beta2) * g * g;
                const mHat = this.mW2[i][j] / (1 - Math.pow(beta1, this.t));
                const vHat = this.vW2[i][j] / (1 - Math.pow(beta2, this.t));
                this.W2[i][j] -= lr * mHat / (Math.sqrt(vHat) + eps);
            }
            const g = dO[i];
            this.mb2[i] = beta1 * this.mb2[i] + (1 - beta1) * g;
            this.vb2[i] = beta2 * this.vb2[i] + (1 - beta2) * g * g;
            const mHat = this.mb2[i] / (1 - Math.pow(beta1, this.t));
            const vHat = this.vb2[i] / (1 - Math.pow(beta2, this.t));
            this.b2[i] -= lr * mHat / (Math.sqrt(vHat) + eps);
        }
        for (let j = 0; j < this.hiddenSize; j++) {
            for (let k = 0; k < this.inputSize; k++) {
                const g = dH[j] * input[k];
                this.mW1[j][k] = beta1 * this.mW1[j][k] + (1 - beta1) * g;
                this.vW1[j][k] = beta2 * this.vW1[j][k] + (1 - beta2) * g * g;
                const mHat = this.mW1[j][k] / (1 - Math.pow(beta1, this.t));
                const vHat = this.vW1[j][k] / (1 - Math.pow(beta2, this.t));
                this.W1[j][k] -= lr * mHat / (Math.sqrt(vHat) + eps);
            }
            const g = dH[j];
            this.mb1[j] = beta1 * this.mb1[j] + (1 - beta1) * g;
            this.vb1[j] = beta2 * this.vb1[j] + (1 - beta2) * g * g;
            const mHat = this.mb1[j] / (1 - Math.pow(beta1, this.t));
            const vHat = this.vb1[j] / (1 - Math.pow(beta2, this.t));
            this.b1[j] -= lr * mHat / (Math.sqrt(vHat) + eps);
        }
    }
    serialize() {
        return JSON.stringify({W1: this.W1, b1: this.b1, W2: this.W2, b2: this.b2});
    }
    deserialize(data) {
        const d = typeof data === 'string' ? JSON.parse(data) : data;
        this.W1 = d.W1; this.b1 = d.b1; this.W2 = d.W2; this.b2 = d.b2;
    }
}

// ── Headless Game State ──
const W = 1200, H = 800;
const crab = { x: W/2, y: H*0.4, vx: 0, vy: 0, alive: true, panicLevel: 0, size: 40, deathCount: 0, trapdoorOpen: 0, trapdoorTarget: 0 };
const crab2 = { alive: false, x: 0, y: 0, particles: [] };
let mouseX = W/2, mouseY = H/2;

// ── Training Config ──
const stateSize = 12;
const hiddenSize = 32;
const actionSize = 2;
const MAX_EPISODE_FRAMES = 1800;
const AUTO_CLICK_INTERVAL = 2.0;
const NUM_EPISODES = parseInt(process.argv[2]) || 500;

// ── Load existing profile if present ──
let brain = new Chitin611(stateSize, hiddenSize, actionSize);
let epsilon = 1.0;
let episode = 0;
let episodeRewards = [];
let episodeSurvival = [];

const profilePath = path.join(__dirname, 'chitin611.json');
if (fs.existsSync(profilePath)) {
    try {
        const saved = JSON.parse(fs.readFileSync(profilePath, 'utf8'));
        brain.deserialize(saved.brain);
        epsilon = saved.epsilon ?? 1.0;
        episode = saved.episode ?? 0;
        episodeRewards = saved.episodeRewards ?? [];
        episodeSurvival = saved.episodeSurvival ?? [];
        console.log(`[CHITIN-611] Restored from disk — episode ${episode}, epsilon ${epsilon.toFixed(3)}`);
    } catch (e) {
        console.log(`[CHITIN-611] Failed to load profile, starting fresh: ${e.message}`);
    }
}

function extractState() {
    const dx = mouseX - crab.x;
    const dy = mouseY - crab.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx);
    return [
        crab.x / W,
        crab.y / H,
        crab.vx / 10,
        crab.vy / 10,
        mouseX / W,
        mouseY / H,
        dist / 500,
        angle / Math.PI,
        crab.panicLevel / 2,
        0, 0, 0
    ];
}

function computeReward() {
    const dx = mouseX - crab.x;
    const dy = mouseY - crab.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    let reward = 0.5; // survival
    if (dist < 120) reward -= (120 - dist) * 0.15;
    if (dist > 150) reward += 0.3;
    return reward;
}

function runEpisode() {
    let frameCount = 0;
    let totalReward = 0;
    let survivalTime = 0;
    const trajectory = [];
    let framesSinceClick = 0;

    // Reset
    crab.x = W / 2;
    crab.y = H * 0.4;
    crab.vx = 0;
    crab.vy = 0;
    crab.alive = true;
    crab.panicLevel = 0;
    mouseX = W / 2;
    mouseY = H / 2;

    for (let s = 0; s < 600; s++) { // 10 seconds of sim time at 60fps
        frameCount++;
        framesSinceClick++;

        const state = extractState();

        // Epsilon-greedy
        let action;
        if (Math.random() < epsilon) {
            action = [Math.random() * 2 - 1, Math.random() * 2 - 1];
        } else {
            action = brain.forward(state);
        }

        // Apply action
        const force = 4.0;
        crab.vx += action[0] * force;
        crab.vy += action[1] * force;

        // Simulate mouse — chase crab with some speed + randomness
        const mdx = crab.x - mouseX;
        const mdy = crab.y - mouseY;
        const mDist = Math.sqrt(mdx * mdx + mdy * mdy);
        const mouseSpeed = 3.5; // pixels per frame
        if (mDist > 5) {
            mouseX += (mdx / mDist) * mouseSpeed + (Math.random() - 0.5) * 2;
            mouseY += (mdy / mDist) * mouseSpeed + (Math.random() - 0.5) * 2;
        }
        mouseX = Math.max(0, Math.min(W, mouseX));
        mouseY = Math.max(0, Math.min(H, mouseY));

        // Periodically teleport mouse near crab (simulates re-clicking)
        framesSinceClick++;
        if (framesSinceClick > 120) { // every 2s sim time
            framesSinceClick = 0;
            mouseX = crab.x + (Math.random() - 0.5) * 300;
            mouseY = crab.y + (Math.random() - 0.5) * 300;
            mouseX = Math.max(0, Math.min(W, mouseX));
            mouseY = Math.max(0, Math.min(H, mouseY));
        }

        // Reward
        const reward = computeReward();
        totalReward += reward;
        survivalTime += 1/60;
        trajectory.push({ state: [...state], action: [...action], reward });

        // Death check — mouse is within kill radius
        const clickDist = Math.sqrt(
            Math.pow(mouseX - crab.x, 2) + Math.pow(mouseY - crab.y, 2)
        );
        if (clickDist < Math.max(12, crab.size * 0.75)) {
            trajectory[trajectory.length - 1].reward += -50;
            break;
        }

        // Timeout
        if (frameCount > MAX_EPISODE_FRAMES) {
            trajectory[trajectory.length - 1].reward += 20;
            break;
        }

        // Physics
        crab.vx *= 0.93;
        crab.vy *= 0.93;
        crab.x += crab.vx;
        crab.y += crab.vy;
        // Wrap
        if (crab.x < -crab.size) crab.x = W + crab.size;
        if (crab.x > W + crab.size) crab.x = -crab.size;
        if (crab.y < -crab.size) crab.y = H + crab.size;
        if (crab.y > H + crab.size) crab.y = -crab.size;
    }

    // ── REINFORCE train ──
    const T = trajectory.length;
    if (T >= 20) {
        const returns = new Array(T);
        let G = 0;
        for (let t = T - 1; t >= 0; t--) {
            G = trajectory[t].reward + 0.95 * G;
            returns[t] = G;
        }
        let sumR = 0;
        for (let t = 0; t < T; t++) sumR += returns[t];
        const baseline = sumR / T;
        let maxAbsAdv = 0;
        for (let t = 0; t < T; t++) {
            const adv = Math.abs(returns[t] - baseline);
            if (adv > maxAbsAdv) maxAbsAdv = adv;
        }
        if (maxAbsAdv < 1e-6) maxAbsAdv = 1;
        for (let t = 0; t < T; t++) {
            const advantage = (returns[t] - baseline) / maxAbsAdv;
            brain.forward(trajectory[t].state);
            const target = [...trajectory[t].action];
            for (let i = 0; i < actionSize; i++) {
                target[i] = Math.tanh(target[i] + advantage * 0.3);
            }
            brain.backward(trajectory[t].state, target, 0.003);
        }
    }

    return { totalReward, survivalTime };
}

// ── Training Loop ──
console.log(`[CHITIN-611] Training ${NUM_EPISODES} episodes at 20x speed...`);
console.log(`[CHITIN-611] Epsilon: ${epsilon.toFixed(3)} → target 0.05\n`);

const startTime = Date.now();
let bestReward = -Infinity;
let recentRewards = [];

for (let i = 0; i < NUM_EPISODES; i++) {
    episode++;
    const result = runEpisode();
    epsilon = Math.max(0.05, epsilon * 0.995);
    episodeRewards.push(result.totalReward);
    episodeSurvival.push(result.survivalTime);
    recentRewards.push(result.totalReward);
    if (recentRewards.length > 50) recentRewards.shift();

    if (result.totalReward > bestReward) bestReward = result.totalReward;

    // Progress every 50 episodes
    if (episode % 50 === 0 || i === NUM_EPISODES - 1) {
        const avg = recentRewards.reduce((a,b)=>a+b,0) / recentRewards.length;
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        process.stdout.write(
            `\r[EP ${String(episode).padStart(5)}] avg=${avg.toFixed(1).padStart(7)} best=${bestReward.toFixed(1).padStart(7)} eps=${epsilon.toFixed(3)} survival=${result.survivalTime.toFixed(1)}s elapsed=${elapsed}s`
        );
    }

    // Save every episode — profile is always current
    saveProfile();
}

console.log('\n');

function saveProfile() {
    const state = {
        brain: brain.serialize(),
        epsilon,
        episode,
        episodeRewards: episodeRewards.slice(-200),
        episodeSurvival: episodeSurvival.slice(-200),
        graphData: episodeRewards.slice(-100),
        savedAt: new Date().toISOString(),
    };
    fs.writeFileSync(profilePath, JSON.stringify(state));
}

saveProfile();
console.log(`[CHITIN-611] Profile saved to ${profilePath}`);
console.log(`[CHITIN-611] Episodes: ${episode} | Final avg (last 50): ${(recentRewards.reduce((a,b)=>a+b,0)/recentRewards.length).toFixed(1)} | Best: ${bestReward.toFixed(1)}`);
console.log(`[CHITIN-611] Load this file in the browser to continue training or play.`);
