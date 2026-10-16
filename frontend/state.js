// Single source of truth for app state. `theme` is the only theme flag in the app.
const THEME_KEY = "cs.theme";
const listeners = new Set();

function initialTheme() {
    try {
        const saved = localStorage.getItem(THEME_KEY);
        if (saved === "dark" || saved === "light") return saved;
    } catch (err) { /* storage unavailable */ }
    return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

const state = { theme: initialTheme(), user: null, clipboard: null };

function notify(key) {
    listeners.forEach((fn) => fn(key, state[key]));
}

export function onChange(fn) {
    listeners.add(fn);
    return () => listeners.delete(fn);
}

export const getTheme = () => state.theme;
export const getUser = () => state.user;
export const getClipboard = () => state.clipboard;

export function setTheme(name) {
    state.theme = name;
    try { localStorage.setItem(THEME_KEY, name); } catch (err) { /* ignore */ }
    notify("theme");
}

export function setUser(name) {
    state.user = name;
    notify("user");
}

export function setClipboard(clip) {
    state.clipboard = clip; // { mode: "copy" | "cut", paths: [] }
    notify("clipboard");
}
