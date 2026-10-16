// The sortable, selectable, draggable list of files.
import { FONT, SPACE } from "../consts.js";
import { add, colored, column, el } from "../dom.js";
import { openMenu } from "./menu.js";
import { entryMenu, backgroundMenu } from "./fileMenu.js";
import { openEntry } from "./fileActions.js";
import { attachDrag } from "./fileDrag.js";
import { buildRow } from "./fileRow.js";
import { handleKeys } from "./fileKeys.js";
import { selectRow, visibleEntries } from "./fileState.js";
import { styled } from "./fileStyle.js";
import { isPhone } from "./windowLayout.js";

const COLS = [["name", "Name"], ["size", "Size"], ["mtime", "Modified"], ["mode", "Mode"]];

export function createFileList(fm) {
    const { scope, state } = fm;
    const root = el("div", { ...column, flex: "1", overflow: "hidden", position: "relative" });
    const head = el("div", { display: "grid", padding: `${SPACE.xs}px ${SPACE.md}px`, fontSize: FONT.size.sm + "px", userSelect: "none", flexShrink: "0" });
    const body = el("div", { flex: "1", overflowY: "auto", position: "relative" });
    body.tabIndex = 0;
    body.setAttribute("aria-label", "Files");
    colored(head, (pal) => ({ color: pal.muted, borderBottom: `1px solid ${pal.border}` }));
    const nodes = new Map();
    const dropTarget = { name: null };

    const paintSelection = () => nodes.forEach((node, name) => styled.row(node, state.selected.has(name), state.hover === name, dropTarget.name === name));
    fm.paintSelection = () => { paintSelection(); fm.status(); };
    colored(body, () => { paintSelection(); return {}; });

    function columns() { const grid = isPhone() ? "1fr 80px" : "1fr 90px 150px 60px"; head.style.gridTemplateColumns = grid; return grid; }

    function render() {
        const grid = columns();
        head.textContent = "";
        COLS.slice(0, isPhone() ? 2 : 4).forEach(([key, text]) => {
            const cell = el("span", { cursor: "pointer", fontWeight: state.sort.key === key ? "700" : "400" }, { textContent: text + (state.sort.key === key ? (state.sort.asc ? " ▲" : " ▼") : "") });
            cell.dataset.sort = key;
            head.appendChild(cell);
        });
        body.textContent = "";
        nodes.clear();
        visibleEntries(state).forEach((entry) => { const node = buildRow(entry, grid); nodes.set(entry.name, node); body.appendChild(node); });
        if (!nodes.size) add(body, el("div", { padding: SPACE.xl + "px", textAlign: "center", opacity: "0.55" }, { textContent: state.entries.length ? "No matches" : "This folder is empty — drop files here" }));
        paintSelection();
    }

    const rowOf = (ev) => ev.target.closest("[data-name]");
    const entryOf = (node) => state.entries.find((e) => e.name === node.dataset.name);
    const hover = (name) => { state.hover = name; paintSelection(); };

    scope.on(head, "click", (ev) => {
        const key = ev.target.dataset.sort;
        if (!key) return;
        state.sort = { key, asc: state.sort.key === key ? !state.sort.asc : true };
        render();
    });
    scope.on(body, "click", (ev) => { const node = rowOf(ev); node ? selectRow(state, node.dataset.name, ev) : state.selected.clear(); fm.paintSelection(); });
    scope.on(body, "dblclick", (ev) => { const node = rowOf(ev); node && openEntry(fm, entryOf(node)); });
    scope.on(body, "contextmenu", (ev) => {
        ev.preventDefault();
        const node = rowOf(ev);
        if (node && !state.selected.has(node.dataset.name)) { state.selected = new Set([node.dataset.name]); fm.paintSelection(); }
        openMenu(node ? entryMenu(fm) : backgroundMenu(fm), ev.clientX, ev.clientY);
    });
    scope.on(body, "pointerover", (ev) => { const node = rowOf(ev); hover(node ? node.dataset.name : null); });
    scope.on(body, "pointerleave", () => hover(null));
    scope.on(body, "keydown", (ev) => handleKeys(fm, ev));
    attachDrag(fm, body, { rowOf, entryOf, dropTarget, paintSelection });
    add(root, head, body);
    return { el: root, render, focus: () => body.focus() };
}
