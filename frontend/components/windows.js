// Registry of open windows: z-order, focus, minimise state, cycling.
import { LAYER } from "../consts.js";

const wins = [];
const listeners = new Set();
let top = LAYER.windows;

const notify = () => listeners.forEach((fn) => fn(wins.slice()));
export const onWindowsChange = (fn) => { listeners.add(fn); return () => listeners.delete(fn); };
export const allWindows = () => wins.slice();
export const activeWindow = () => wins.find((w) => w.active) || null;

export function register(win) {
    wins.push(win);
    focusWindow(win);
}

export function unregister(win) {
    wins.splice(wins.indexOf(win), 1);
    const next = [...wins].filter((w) => !w.minimized).sort((a, b) => b.z - a.z)[0];
    next ? focusWindow(next) : notify();
}

export function focusWindow(win) {
    if (win.minimized) { win.minimized = false; win.el.style.display = "flex"; }
    win.z = ++top;
    win.el.style.zIndex = String(win.z);
    wins.forEach((w) => w.setActive(w === win));
    win.onResize && win.onResize();
    notify();
}

export function refresh() {
    notify();
}

export function cycleWindows(step = 1) {
    const order = wins.slice().sort((a, b) => a.z - b.z);
    if (order.length < 2) return;
    focusWindow(step > 0 ? order[0] : order[order.length - 1]);
}
