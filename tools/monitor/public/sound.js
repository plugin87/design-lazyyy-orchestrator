/**
 * sound — the room's score, synthesised in the browser.
 *
 * The first version was bare oscillators, which is exactly what a 1980s console
 * was, and it sounded like one. What separates that from a film cue is not the
 * notes, it is everything around them:
 *
 *   - brass is not one saw wave, it is a stack of detuned saws pushed through a
 *     lowpass that opens as the note is blown
 *   - a hall is not an effect on top, it is the reason separate notes sound like
 *     one orchestra — so everything here runs through a generated impulse
 *   - percussion has a pitch that falls, and a body longer than its attack
 *
 * No audio files: the room has to work from a folder on a laptop with no
 * network, and eight roles each needing their own cue is a lot of megabytes for
 * something an oscillator bank does in a few hundred lines.
 *
 * The theme is original. It is written to sit in the same heroic register as a
 * superhero film cue — rising fourth, minor-to-major turn, wide brass — without
 * quoting one.
 */
export const Sound = (() => {
  let ctx = null, master = null, hall = null, dry = null, enabled = false;
  let bed = null, bedGain = null, playing = false;

  /* ── hall ────────────────────────────────────────────────────────────────
     A convolver needs an impulse. Generating one — noise decaying over a few
     seconds, darker as it dies — costs nothing and is what makes a handful of
     oscillators read as an ensemble in a room rather than a phone speaker. */
  function impulse(seconds = 3.1, decay = 2.4) {
    const rate = ctx.sampleRate;
    const len = Math.floor(rate * seconds);
    const buf = ctx.createBuffer(2, len, rate);
    for (let c = 0; c < 2; c++) {
      const d = buf.getChannelData(c);
      for (let i = 0; i < len; i++) {
        const t = i / len;
        // early reflections, then a smooth tail
        const early = i < rate * 0.06 ? (Math.random() * 2 - 1) * 0.6 : 0;
        d[i] = ((Math.random() * 2 - 1) * 0.85 + early) * Math.pow(1 - t, decay);
      }
    }
    return buf;
  }

  function arm() {
    if (ctx) { if (ctx.state === 'suspended') ctx.resume(); return; }
    ctx = new (window.AudioContext || window.webkitAudioContext)();

    master = ctx.createGain();
    master.gain.value = 0.24;
    const ceiling = ctx.createDynamicsCompressor();
    ceiling.threshold.value = -12;
    ceiling.knee.value = 18;
    ceiling.ratio.value = 4;
    ceiling.attack.value = 0.006;
    ceiling.release.value = 0.22;
    master.connect(ceiling).connect(ctx.destination);

    const verb = ctx.createConvolver();
    verb.buffer = impulse();
    hall = ctx.createGain(); hall.gain.value = 0.46;
    dry  = ctx.createGain(); dry.gain.value = 0.55;
    hall.connect(verb).connect(master);
    dry.connect(master);

    startBed();
  }

  const now = () => ctx.currentTime;
  const send = node => { node.connect(dry); node.connect(hall); };

  /* ── instruments ─────────────────────────────────────────────────────── */



  function noise({ at = 0, dur = 0.12, gain = 0.15, freq = 900, q = 1, type = 'bandpass', sweep = null }) {
    if (!ctx || !enabled) return;
    const t = now() + at;
    const frames = Math.max(1, Math.ceil(ctx.sampleRate * dur));
    const buf = ctx.createBuffer(1, frames, ctx.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < frames; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / frames);
    const src = ctx.createBufferSource(); src.buffer = buf;
    const f = ctx.createBiquadFilter();
    f.type = type; f.Q.value = q;
    f.frequency.setValueAtTime(freq, t);
    if (sweep) f.frequency.exponentialRampToValueAtTime(sweep, t + dur);
    const amp = ctx.createGain();
    amp.gain.setValueAtTime(gain, t);
    amp.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    src.connect(f).connect(amp); send(amp);
    src.start(t);
  }

  function bell(freq, at, gain = 0.12, dur = 1.6) {
    if (!ctx || !enabled) return;
    const t = now() + at;
    for (const [mult, g] of [[1, 1], [2.76, .35], [5.4, .16]]) {
      const osc = ctx.createOscillator();
      osc.type = 'sine'; osc.frequency.value = freq * mult;
      const amp = ctx.createGain();
      amp.gain.setValueAtTime(0.0001, t);
      amp.gain.exponentialRampToValueAtTime(gain * g, t + 0.012);
      amp.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      osc.connect(amp); send(amp);
      osc.start(t); osc.stop(t + dur + 0.05);
    }
  }

  /* ── the bed: a low sustained fifth, the room breathing ───────────────── */
  function startBed() {
    bedGain = ctx.createGain();
    bedGain.gain.value = 0;
    send(bedGain);
    bed = [];
    for (const f of [55, 82.5, 110, 164.81]) {
      const osc = ctx.createOscillator();
      osc.type = 'sawtooth';
      osc.frequency.value = f;
      osc.detune.value = (Math.random() * 12) - 6;
      const flt = ctx.createBiquadFilter();
      flt.type = 'lowpass'; flt.frequency.value = 260; flt.Q.value = .7;
      const g = ctx.createGain(); g.gain.value = f < 100 ? 0.09 : 0.045;
      osc.connect(flt).connect(g).connect(bedGain);
      osc.start();
      bed.push(osc);
    }
    const swell = ctx.createOscillator();
    const swellAmt = ctx.createGain();
    swell.frequency.value = 0.055; swellAmt.gain.value = 0.055;
    swell.connect(swellAmt).connect(bedGain.gain);
    swell.start();
    bedGain.gain.setTargetAtTime(0.05, now(), 8);
  }

  /* ── the theme ────────────────────────────────────────────────────────────
     Original motif: a rising fourth into a suspended second that resolves up —
     the shape heroic cues use, without being any particular one. */
  const A3 = 220, C4 = 261.63, D4 = 293.66, E4 = 329.63, F4 = 349.23,
        G4 = 392.00, A4 = 440, C5 = 523.25, D5 = 587.33, E5 = 659.25, G5 = 783.99;


  return {
    arm,
    get enabled() { return enabled; },
    toggle() {
      enabled = !enabled;
      if (master) master.gain.setTargetAtTime(enabled ? 0.24 : 0, now(), 0.25);
      return enabled;
    },

    /* Cues are deliberately quiet and sparse.
       The first pass was brass and timpani on every event, which is exciting
       once and exhausting by the fourth file written — and the room can fire
       dozens of events a minute. What is left is a small set of soft bells in
       one key, low enough to sit under a voice, with the noisy layers gone. */

    /** the owner gives the order */
    order() { bell(C4, 0, 0.05, 2.4); bell(G4, 0.14, 0.035, 2.2); },

    /** a role is dispatched */
    dispatch() { bell(G4, 0, 0.035, 1.8); },

    /** they begin */
    wake() { bell(C5, 0, 0.026, 1.4); },

    /** footsteps — almost subliminal, or eight of them become a drum machine */
    step(right = false) {
      noise({ dur: 0.05, gain: 0.012, freq: right ? 300 : 260, q: 1.2, sweep: 140, type: 'lowpass' });
    },

    /** a file was written — this fires most often, so it is the quietest */
    tick() { bell(E5 * (Math.random() < .5 ? 1 : 1.2), 0, 0.012, 0.7); },

    /** work handed back */
    handoff() { bell(G4, 0, 0.03, 1.6); bell(C4, 0.1, 0.026, 2.0); },

    /** correcter: the work stands — warm, resolved, still soft */
    pass() {
      [[C4, 0], [E4, .1], [G4, .2], [C5, .3]].forEach(([f, at]) => bell(f, at, 0.032, 2.6));
    },

    /** correcter: do it again — unresolved, but not an alarm */
    corrected() {
      [[F4, 0], [D4 * 1.0595, .13]].forEach(([f, at]) => bell(f, at, 0.034, 2.2));
    },

    /** correcter: stopped. low and long, no buzzer */
    blocked() {
      [[A3 / 2, 0], [A3 * 0.944, .18]].forEach(([f, at]) => bell(f, at, 0.04, 3.4));
      strings(A3 / 2, 0, 2.6, 0.035);
    },

    /** a gate is cleared */
    gate() { [[G4, 0], [C5, .11], [E5, .22]].forEach(([f, at]) => bell(f, at, 0.03, 2.4)); },
  };
})();
