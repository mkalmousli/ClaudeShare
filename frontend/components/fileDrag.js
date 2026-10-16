// Drag-and-drop in the file list: move within the app, upload from the OS.
import { joinPath } from "../format.js";
import { moveInto, upload } from "./fileActions.js";
import { collectDropped } from "./uploads.js";

export const DRAG_TYPE = "application/x-claudeshare-paths";

export function attachDrag(fm, body, { rowOf, entryOf, dropTarget, paintSelection }) {
    const { scope, state } = fm;
    scope.on(body, "dragstart", (ev) => {
        const node = rowOf(ev);
        if (!state.selected.has(node.dataset.name)) { state.selected = new Set([node.dataset.name]); fm.paintSelection(); }
        ev.dataTransfer.setData(DRAG_TYPE, JSON.stringify([...state.selected].map((n) => joinPath(state.cwd, n))));
    });
    scope.on(body, "dragover", (ev) => {
        ev.preventDefault();
        const node = rowOf(ev);
        dropTarget.name = node && entryOf(node).isDir ? node.dataset.name : null;
        paintSelection();
    });
    scope.on(body, "dragleave", () => { dropTarget.name = null; paintSelection(); });
    scope.on(body, "drop", (ev) => {
        ev.preventDefault();
        const dest = dropTarget.name ? joinPath(state.cwd, dropTarget.name) : state.cwd;
        dropTarget.name = null;
        const moved = ev.dataTransfer.getData(DRAG_TYPE);
        if (moved) return moveInto(fm, JSON.parse(moved).filter((p) => p !== dest), dest);
        collectDropped(ev.dataTransfer).then((items) => items.length && upload(fm, items, dest));
    });
}
