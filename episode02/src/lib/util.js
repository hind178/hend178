// Shared math / path helpers for the 2D vector engine.
const f = (n) => (Math.round(n * 10) / 10).toString();
const lerp = (a, b, t) => a + (b - a) * t;
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const ease = (t) => { t = clamp(t); return t * t * (3 - 2 * t); };
const easeInOut = (t) => { t = clamp(t); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const easeOut = (t) => { t = clamp(t); return 1 - Math.pow(1 - t, 3); };
const easeIn = (t) => { t = clamp(t); return t * t * t; };
/** progress of t inside [a,b] */
const prog = (t, a, b) => clamp((t - a) / (b - a));
/** keyframe interpolation: keys = [[t, value], ...] with smooth easing */
function kf(t, keys, fn = easeInOut) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [t0, v0] = keys[i], [t1, v1] = keys[i + 1];
    if (t <= t1) {
      const p = fn((t - t0) / (t1 - t0));
      if (Array.isArray(v0)) return v0.map((v, j) => lerp(v, v1[j], p));
      return lerp(v0, v1, p);
    }
  }
  return keys[keys.length - 1][1];
}
function mkRng(seed) { let s = seed >>> 0 || 1; return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; }
/** Smooth curve through points (Catmull-Rom -> cubic Bezier). */
function smooth(p, closed = false, tension = 1) {
  const n = p.length;
  let d = `M${f(p[0][0])},${f(p[0][1])}`;
  const get = (i) => closed ? p[(i + n) % n] : p[Math.max(0, Math.min(n - 1, i))];
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = get(i - 1), p1 = get(i), p2 = get(i + 1), p3 = get(i + 2);
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6 * tension, p1[1] + (p2[1] - p0[1]) / 6 * tension];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6 * tension, p2[1] - (p3[1] - p1[1]) / 6 * tension];
    d += ` C${f(c1[0])},${f(c1[1])} ${f(c2[0])},${f(c2[1])} ${f(p2[0])},${f(p2[1])}`;
  }
  return closed ? d + ' Z' : d;
}
/** Tube along segment A->B whose width follows wfn(t) (t in 0..1); rounded ends. */
function tube(A, B, wfn, n = 10) {
  const dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy) || 1;
  const nx = -dy / L, ny = dx / L, ux = dx / L, uy = dy / L;
  const left = [], right = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, w = wfn(t) / 2, x = A[0] + dx * t, y = A[1] + dy * t;
    left.push([x + nx * w, y + ny * w]); right.push([x - nx * w, y - ny * w]);
  }
  const w0 = wfn(0) / 2, w1 = wfn(1) / 2;
  const capEnd = [B[0] + ux * w1 * 0.55, B[1] + uy * w1 * 0.55];
  const capStart = [A[0] - ux * w0 * 0.55, A[1] - uy * w0 * 0.55];
  return smooth([...left, capEnd, ...right.reverse(), capStart], true, 0.9);
}
const rad = (d) => d * Math.PI / 180;
const deg = (r) => r * 180 / Math.PI;
/** rotate a point around origin */
const rot = (p, a, o = [0, 0]) => { const c = Math.cos(a), s = Math.sin(a), x = p[0] - o[0], y = p[1] - o[1]; return [o[0] + x * c - y * s, o[1] + x * s + y * c]; };
module.exports = { f, lerp, clamp, ease, easeInOut, easeOut, easeIn, prog, kf, mkRng, smooth, tube, rad, deg, rot };
