// Edge and corner resize handles.
import { WINDOW } from "../consts.js";
import { el } from "../dom.js";
import { apply, area } from "./windowLayout.js";

const HANDLES = {
    n: ["ns-resize", { top: "0px", left: "0px", right: "0px", height: WINDOW.edge + "px" }],
    s: ["ns-resize", { bottom: "0px", left: "0px", right: "0px", height: WINDOW.edge + "px" }],
    w: ["ew-resize", { left: "0px", top: "0px", bottom: "0px", width: WINDOW.edge + "px" }],
    e: ["ew-resize", { right: "0px", top: "0px", bottom: "0px", width: WINDOW.edge + "px" }],
    nw: ["nwse-resize", { left: "0px", top: "0px", width: "12px", height: "12px" }],
    ne: ["nesw-resize", { right: "0px", top: "0px", width: "12px", height: "12px" }],
    sw: ["nesw-resize", { left: "0px", bottom: "0px", width: "12px", height: "12px" }],
    se: ["nwse-resize", { right: "0px", bottom: "0px", width: "12px", height: "12px" }],
};

function resized(rect, dir, dx, dy) {
    const next = { ...rect };
    const space = area();
    if (dir.includes("e")) next.w = Math.min(rect.w + dx, space.w - rect.x);
    if (dir.includes("s")) next.h = Math.min(rect.h + dy, space.h - rect.y);
    if (dir.includes("w")) { next.w = rect.w - dx; next.x = rect.x + dx; }
    if (dir.includes("n")) { next.h = rect.h - dy; next.y = rect.y + dy; }
    if (next.w < WINDOW.minW) { if (dir.includes("w")) next.x -= WINDOW.minW - next.w; next.w = WINDOW.minW; }
    if (next.h < WINDOW.minH) { if (dir.includes("n")) next.y -= WINDOW.minH - next.h; next.h = WINDOW.minH; }
    next.x = Math.max(0, next.x);
    next.y = Math.max(0, next.y);
    return next;
}

export function addResizeHandles(win, scope) {
    Object.entries(HANDLES).forEach(([dir, [cursor, place]]) => {
        const handle = el("div", { position: "absolute", cursor, zIndex: "2", touchAction: "none", ...place });
        let start = null;
        scope.on(handle, "pointerdown", (ev) => {
            if (win.maximized) return;
            start = { x: ev.clientX, y: ev.clientY, rect: { ...win.rect } };
            handle.setPointerCapture(ev.pointerId);
        });
        scope.on(handle, "pointermove", (ev) => {
            if (!start) return;
            win.rect = resized(start.rect, dir, ev.clientX - start.x, ev.clientY - start.y);
            apply(win);
        });
        scope.on(handle, "pointerup", () => { start = null; });
        win.el.appendChild(handle);
    });
}
