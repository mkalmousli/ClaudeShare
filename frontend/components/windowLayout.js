// Geometry helpers for desktop windows.
import { PHONE_BREAKPOINT, SIZE, WINDOW } from "../consts.js";

export const area = () => ({ w: window.innerWidth, h: window.innerHeight - SIZE.taskbar });
export const isPhone = () => window.innerWidth < PHONE_BREAKPOINT;
const clamp = (value, low, high) => Math.max(low, Math.min(high, value));

export function clampRect(rect) {
    const space = area();
    const w = clamp(rect.w, Math.min(WINDOW.minW, space.w), space.w);
    const h = clamp(rect.h, Math.min(WINDOW.minH, space.h), space.h);
    return { x: clamp(rect.x, 0, space.w - w), y: clamp(rect.y, 0, space.h - h), w, h };
}

export function half(side) {
    const space = area();
    const w = Math.floor(space.w / 2);
    return { x: side === "left" ? 0 : space.w - w, y: 0, w, h: space.h };
}

export function cascade(index) {
    const offset = (index % 8) * WINDOW.cascade;
    return clampRect({ x: WINDOW.originX + offset, y: WINDOW.originY + offset, w: WINDOW.w, h: WINDOW.h });
}

export function apply(win) {
    const full = win.maximized || isPhone();
    const rect = full ? { x: 0, y: 0, ...area() } : win.rect;
    Object.assign(win.el.style, {
        left: rect.x + "px", top: rect.y + "px", width: rect.w + "px", height: rect.h + "px",
        borderRadius: full ? "0px" : "10px",
    });
    win.onResize && win.onResize();
}
