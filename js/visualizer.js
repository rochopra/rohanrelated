/* visualizer.js . live audio visualizer for /sound/
 *
 * Analyses a real MP3 through an AnalyserNode and draws a mirrored spectrum
 * contour. Not a bar chart and not a scrolling waveform: the brief rules out
 * waveform cliches, so the form here is a single smooth curve mirrored about
 * the centre line, with slow decaying peak-hold marks in Safelight above it.
 * At rest it is a flat horizon; playing, it opens like an aperture.
 *
 * Behaviour this file guarantees:
 *   . no autoplay. Audio starts only on a user gesture, which is also what
 *     browser autoplay policy requires.
 *   . AudioContext is created on first play, never on load.
 *   . prefers-reduced-motion: no animation loop at all. The audio still
 *     plays and the canvas shows a static form.
 *   . no JS, no Web Audio, or no audio file: the <figure> falls back to the
 *     static plate and a plain link. Nothing is broken, only quieter.
 *   . the canvas is aria-hidden and the real state lives in a text status
 *     line, so a screen reader gets a description rather than a canvas.
 */
(function () {
  "use strict";

  var root = document.querySelector("[data-visualizer]");
  if (!root) return;

  var audio = root.querySelector("audio");
  var canvas = root.querySelector("canvas");
  var playBtn = root.querySelector("[data-vis-play]");
  var status = root.querySelector("[data-vis-status]");
  var elapsed = root.querySelector("[data-vis-time]");
  if (!audio || !canvas || !playBtn) return;

  // Feature gate: without Web Audio, leave the static plate and the
  // native audio element in place rather than shipping a broken canvas.
  var AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) {
    root.setAttribute("data-vis-mode", "fallback");
    audio.setAttribute("controls", "");
    return;
  }

  root.setAttribute("data-vis-mode", "ready");

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  var ctx = canvas.getContext("2d");
  var css = getComputedStyle(document.documentElement);
  var WALL = css.getPropertyValue("--wall").trim() || "#eeeff1";
  var FOG = css.getPropertyValue("--fog").trim() || "#9fa8b5";
  var SAFELIGHT = css.getPropertyValue("--safelight").trim() || "#9e3a16";
  var GROUND = css.getPropertyValue("--screen-ground").trim() || "#0d1016";

  var audioCtx = null, analyser = null, source = null;
  var freq = null, bins = 0;
  var raf = null;
  var peaks = null;      // peak-hold value per column
  var peakAge = null;    // frames since each peak was set
  var COLUMNS = 96;      // resampled from the FFT, independent of bin count

  /* ---------- sizing: draw at device resolution, lay out in CSS px ---------- */
  var w = 0, h = 0;
  function resize() {
    var rect = canvas.getBoundingClientRect();
    if (!rect.width) return;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = rect.width;
    h = rect.height;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw(true);
  }

  /* ---------- the form ---------- */
  function columnValue(i) {
    if (!freq) return 0;
    // Perceptual spacing: low bins carry most musical information, so map
    // columns to bins on a curve rather than linearly across the spectrum.
    var t0 = Math.pow(i / COLUMNS, 2.1);
    var t1 = Math.pow((i + 1) / COLUMNS, 2.1);
    var a = Math.floor(t0 * bins);
    var b = Math.max(a + 1, Math.floor(t1 * bins));
    var sum = 0, n = 0;
    for (var k = a; k < b && k < bins; k++) { sum += freq[k]; n++; }
    return n ? (sum / n) / 255 : 0;
  }

  function draw(staticFrame) {
    if (!w || !h) return;
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = GROUND;
    ctx.fillRect(0, 0, w, h);

    var mid = h / 2;
    var pad = Math.max(14, w * 0.035);
    var usable = w - pad * 2;
    var maxAmp = h * 0.38;

    // horizon line: the resting state, and the spine of the form
    ctx.strokeStyle = FOG;
    ctx.globalAlpha = 0.35;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(pad, mid);
    ctx.lineTo(w - pad, mid);
    ctx.stroke();
    ctx.globalAlpha = 1;

    if (staticFrame || !freq) {
      // At rest: a flat horizon and nothing else. The plate should look
      // composed when paused, not like a stalled animation.
      return;
    }

    var pts = [];
    for (var i = 0; i < COLUMNS; i++) {
      var v = columnValue(i);
      // gentle ease so quiet passages still register
      v = Math.pow(v, 0.78);
      pts.push({ x: pad + (i / (COLUMNS - 1)) * usable, a: v * maxAmp });
    }

    // mirrored fill, drawn as one closed smooth path
    function contour(sign) {
      ctx.beginPath();
      ctx.moveTo(pts[0].x, mid);
      for (var i = 0; i < pts.length - 1; i++) {
        var p = pts[i], q = pts[i + 1];
        var cx = (p.x + q.x) / 2;
        ctx.quadraticCurveTo(p.x, mid + sign * p.a, cx, mid + sign * (p.a + q.a) / 2);
      }
      ctx.lineTo(pts[pts.length - 1].x, mid);
    }

    var grad = ctx.createLinearGradient(0, mid - maxAmp, 0, mid + maxAmp);
    grad.addColorStop(0, FOG);
    grad.addColorStop(0.5, WALL);
    grad.addColorStop(1, FOG);

    ctx.globalAlpha = 0.16;
    ctx.fillStyle = grad;
    contour(-1); ctx.closePath(); ctx.fill();
    contour(1); ctx.closePath(); ctx.fill();

    ctx.globalAlpha = 0.9;
    ctx.strokeStyle = grad;
    ctx.lineWidth = 1.5;
    ctx.lineJoin = "round";
    contour(-1); ctx.stroke();
    contour(1); ctx.stroke();
    ctx.globalAlpha = 1;

    // peak holds in Safelight: they mark where the track just was, and
    // decay slowly, so the eye reads recent history without a scroll.
    ctx.fillStyle = SAFELIGHT;
    for (var j = 0; j < COLUMNS; j++) {
      var amp = pts[j].a;
      if (amp >= peaks[j]) { peaks[j] = amp; peakAge[j] = 0; }
      else { peakAge[j]++; peaks[j] = Math.max(0, peaks[j] - 0.35 - peakAge[j] * 0.02); }
      if (peaks[j] > 2) {
        var alpha = Math.max(0, 1 - peakAge[j] / 90);
        ctx.globalAlpha = alpha * 0.85;
        ctx.fillRect(pts[j].x - 1, mid - peaks[j] - 1.5, 2, 2);
        ctx.fillRect(pts[j].x - 1, mid + peaks[j] - 0.5, 2, 2);
      }
    }
    ctx.globalAlpha = 1;
  }

  function loop() {
    analyser.getByteFrequencyData(freq);
    draw(false);
    raf = requestAnimationFrame(loop);
  }

  function startLoop() {
    if (reduce.matches) { draw(true); return; }
    if (raf === null) raf = requestAnimationFrame(loop);
  }
  function stopLoop() {
    if (raf !== null) { cancelAnimationFrame(raf); raf = null; }
    draw(true);
  }

  /* ---------- wiring ---------- */
  function ensureGraph() {
    if (audioCtx) return;
    audioCtx = new AC();
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0.82;
    bins = analyser.frequencyBinCount;
    freq = new Uint8Array(bins);
    peaks = new Float32Array(COLUMNS);
    peakAge = new Float32Array(COLUMNS);
    source = audioCtx.createMediaElementSource(audio);
    source.connect(analyser);
    analyser.connect(audioCtx.destination);
  }

  function fmt(t) {
    if (!isFinite(t)) return "0:00";
    var m = Math.floor(t / 60), s = Math.floor(t % 60);
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  function setState(playing) {
    playBtn.setAttribute("aria-pressed", playing ? "true" : "false");
    playBtn.querySelector("[data-vis-label]").textContent = playing ? "Pause" : "Play";
    if (status) {
      status.textContent = playing
        ? "Playing. The plate shows a live frequency reading of the track."
        : "Paused.";
    }
  }

  playBtn.addEventListener("click", function () {
    ensureGraph();
    if (audioCtx.state === "suspended") audioCtx.resume();
    if (audio.paused) {
      audio.play().then(function () { setState(true); startLoop(); })
        .catch(function () {
          // Autoplay refusal or a missing file: degrade, do not pretend.
          root.setAttribute("data-vis-mode", "fallback");
          audio.setAttribute("controls", "");
          if (status) status.textContent = "Audio could not start. Use the player controls.";
        });
    } else {
      audio.pause();
    }
  });

  audio.addEventListener("pause", function () { setState(false); stopLoop(); });
  audio.addEventListener("ended", function () {
    setState(false); stopLoop();
    if (peaks) { peaks.fill(0); peakAge.fill(0); }
    if (elapsed) elapsed.textContent = fmt(0) + " / " + fmt(audio.duration);
  });
  audio.addEventListener("timeupdate", function () {
    if (elapsed) elapsed.textContent = fmt(audio.currentTime) + " / " + fmt(audio.duration);
  });
  audio.addEventListener("loadedmetadata", function () {
    if (elapsed) elapsed.textContent = fmt(0) + " / " + fmt(audio.duration);
  });
  audio.addEventListener("error", function () {
    root.setAttribute("data-vis-mode", "fallback");
    if (status) status.textContent = "Track unavailable.";
  });

  reduce.addEventListener("change", function () {
    if (reduce.matches) stopLoop();
    else if (!audio.paused) startLoop();
  });

  var ro = window.ResizeObserver ? new ResizeObserver(resize) : null;
  if (ro) ro.observe(canvas); else window.addEventListener("resize", resize);
  resize();
  setState(false);
})();
