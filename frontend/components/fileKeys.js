// Keyboard shortcuts inside the file list.
import { parentPath } from "../format.js";
import { clip, openEntry, paste, remove, rename } from "./fileActions.js";
import { selectedEntries, visibleEntries } from "./fileState.js";

function move(fm, step) {
    const order = visibleEntries(fm.state);
    if (!order.length) return;
    const current = order.findIndex((e) => fm.state.selected.has(e.name));
    const next = order[Math.max(0, Math.min(order.length - 1, current + step))];
    fm.state.selected = new Set([next.name]);
    fm.state.anchor = next.name;
    fm.paintSelection();
}

export function handleKeys(fm, ev) {
    const mod = ev.ctrlKey || ev.metaKey;
    const keys = {
        ArrowDown: () => move(fm, 1), ArrowUp: () => move(fm, -1),
        Enter: () => selectedEntries(fm.state).forEach((e) => openEntry(fm, e)),
        Delete: () => remove(fm), F2: () => rename(fm), Backspace: () => fm.go(parentPath(fm.state.cwd)),
        Escape: () => { fm.state.selected.clear(); fm.paintSelection(); },
    };
    const combos = {
        a: () => { fm.state.selected = new Set(visibleEntries(fm.state).map((e) => e.name)); fm.paintSelection(); },
        c: () => clip(fm, "copy"), x: () => clip(fm, "cut"), v: () => paste(fm),
    };
    const action = mod ? combos[ev.key.toLowerCase()] : keys[ev.key];
    if (action) { ev.preventDefault(); action(); }
}
