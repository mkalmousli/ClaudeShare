// Dragging a window by its titlebar, with edge snapping on release.
import { WINDOW } from "../consts.js";
import { apply, area, clampRect, half } from "./windowLayout.js";

const snapTarget = (ev) => {
    const space = area();
    if (ev.clientY <= WINDOW.snapZone) return "max";
    if (ev.clientX <= WINDOW.snapZone) return "left";
    return ev.clientX >= space.w - WINDOW.snapZone ? "right" : null;
};

export function enableDrag(win, handle, scope) {
    let start = null;
    scope.on(handle, "pointerdown", (ev) => {
        if (ev.button !== 0 || ev.target.closest("button") || win.maximized) return;
        start = { x: ev.clientX, y: ev.clientY, rect: { ...win.rect } };
        handle.setPointerCapture(ev.pointerId);
    });
    scope.on(handle, "pointermove", (ev) => {
        if (!start) return;
        const moved = { ...start.rect, x: start.rect.x + ev.clientX - start.x, y: start.rect.y + ev.clientY - start.y };
        win.rect = clampRect(moved);
        apply(win);
    });
    scope.on(handle, "pointerup", (ev) => {
        if (!start) return;
        start = null;
        const target = snapTarget(ev);
        if (target === "max") win.toggleMaximize();
        else if (target) { win.rect = half(target); apply(win); }
    });
}
