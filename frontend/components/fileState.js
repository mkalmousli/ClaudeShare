// Per-window state of a file manager plus pure helpers over it.
import { baseName, joinPath } from "../format.js";

export function createState(path = "/") {
    return { cwd: path, entries: [], selected: new Set(), anchor: null, filter: "", hidden: false,
        sort: { key: "name", asc: true }, back: [], forward: [], hover: null };
}

const compare = {
    name: (a, b) => a.name.localeCompare(b.name, undefined, { numeric: true, sensitivity: "base" }),
    size: (a, b) => a.size - b.size,
    mtime: (a, b) => a.mtime - b.mtime,
    mode: (a, b) => a.mode - b.mode,
};

export function visibleEntries(state) {
    const needle = state.filter.toLowerCase();
    const shown = state.entries.filter((e) => (state.hidden || !e.name.startsWith(".")) && e.name.toLowerCase().includes(needle));
    const dir = state.sort.asc ? 1 : -1;
    return shown.sort((a, b) => (a.isDir === b.isDir ? dir * compare[state.sort.key](a, b) : a.isDir ? -1 : 1));
}

export const pathOf = (state, name) => joinPath(state.cwd, name);
export const selectedPaths = (state) => [...state.selected].map((name) => pathOf(state, name));
export const selectedEntries = (state) => state.entries.filter((e) => state.selected.has(e.name));

const ARCHIVE = /\.(zip|tar|tar\.gz|tgz|tar\.bz2|tbz2|tar\.xz|txz)$/i;
const IMAGE = /\.(png|jpe?g|gif|webp|svg|bmp|ico)$/i;
export const isArchive = (name) => ARCHIVE.test(name);
export const isImage = (name) => IMAGE.test(name);
export const iconFor = (entry) => (entry.isDir ? "folder" : isImage(entry.name) ? "image" : isArchive(entry.name) ? "archive" : "file");

export function selectRow(state, name, ev) {
    const order = visibleEntries(state).map((e) => e.name);
    if (ev.shiftKey && state.anchor && order.includes(state.anchor)) {
        const [from, to] = [order.indexOf(state.anchor), order.indexOf(name)].sort((a, b) => a - b);
        state.selected = new Set(order.slice(from, to + 1));
    } else if (ev.ctrlKey || ev.metaKey) {
        state.selected.has(name) ? state.selected.delete(name) : state.selected.add(name);
        state.anchor = name;
    } else {
        state.selected = new Set([name]);
        state.anchor = name;
    }
}

export const defaultArchiveName = (state) => (state.selected.size === 1 ? baseName([...state.selected][0]) : baseName(state.cwd) === "/" ? "archive" : baseName(state.cwd)) + ".zip";
