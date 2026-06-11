// ============ 音频能量逐词高亮 ============
// 通过 Web Audio API 分析音频能量，让高亮跟随实际语音节奏
// 使用 .speaking 类避免与原 .active 类冲突

let audioCtx = null, analyser = null;
let energyData = null, energyFrameId = null, isInit = false;
let curWordIdx = -1;

function initEA() {
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 256;
            const src = audioCtx.createMediaElementSource(player);
            src.connect(analyser);
            analyser.connect(audioCtx.destination);
            energyData = new Uint8Array(analyser.frequencyBinCount);
        }
        if (audioCtx.state === 'suspended') audioCtx.resume();
        return true;
    } catch(e) { return false; }
}

function getE() {
    if (!analyser) return 0;
    analyser.getByteFrequencyData(energyData);
    let s = 0;
    for (let i = 3; i < energyData.length; i++) s += energyData[i];
    return s / (energyData.length - 3);
}

let lastE = 0, frames = 0, isVoice = false;

function voiceDetect() {
    const e = getE();
    const rising = e - lastE;
    lastE = e;
    if (e > 3.0 || rising > 1.0) {
        frames = Math.min(frames + 2, 15);
        isVoice = true;
    } else if (e < 1.5) {
        frames = Math.max(frames - 1, 0);
        if (frames === 0) isVoice = false;
    }
    return { on: isVoice, e, rising };
}

function getWord(si, ct) {
    if (si < 0 || !currentContent || si >= currentContent.length) return -1;
    const s = currentContent[si];
    const words = s.text.split(/\s+/).filter(w => w);
    if (!words.length) return -1;
    
    const st = s.start || 0, ed = s.end || (st + 2);
    if (ct < st - 0.05) return -1;
    if (ct >= ed) return words.length - 1;
    
    const elapsed = ct - st;
    const dur = ed - st;
    const progress = Math.max(0, Math.min(1, elapsed / dur));
    
    // 语音权重：短词快、长词慢
    const w = words.map(w => Math.max(0.5, w.length * 0.25));
    const tw = w.reduce((a, b) => a + b, 0);
    let c = 0;
    const thr = w.map(v => { c += v / tw; return c; });
    
    const { on } = voiceDetect();
    let p = on ? Math.min(1, progress * 1.08) : Math.max(0, progress - 0.02);
    
    for (let i = 0; i < thr.length; i++) {
        if (p <= thr[i]) return i;
    }
    return thr.length - 1;
}

function tick() {
    if (player.paused) { energyFrameId = null; isInit = false; return; }
    
    const ct = player.currentTime;
    let si = -1;
    for (let i = 0; i < currentContent.length; i++) {
        const st = currentContent[i].start;
        if (st !== undefined && ct >= st - 0.05 && ct < (currentContent[i].end || st + 2)) {
            si = i; break;
        }
    }
    
    if (si >= 0) {
        const wi = getWord(si, ct);
        if (wi >= 0 && wi !== curWordIdx) {
            document.querySelectorAll('.word.speaking').forEach(el => el.classList.remove('speaking'));
            const el = document.getElementById('sent-' + si);
            if (el) {
                const ws = el.querySelectorAll('.word');
                if (ws[wi]) ws[wi].classList.add('speaking');
            }
            curWordIdx = wi;
        }
    }
    
    energyFrameId = requestAnimationFrame(tick);
}

player.addEventListener('play', () => {
    if (!isInit) {
        isInit = initEA();
        if (isInit) {
            curWordIdx = -1;
            energyFrameId = requestAnimationFrame(tick);
        }
    }
});

player.addEventListener('seeked', () => { curWordIdx = -1; });
player.addEventListener('pause', () => {
    if (energyFrameId) { cancelAnimationFrame(energyFrameId); energyFrameId = null; }
    isInit = false;
});
