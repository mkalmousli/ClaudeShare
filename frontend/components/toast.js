// Short-lived status messages at the bottom centre.
import { FONT, LAYER, RADIUS, SIZE, SPACE, TIMING } from "../consts.js";
import { colored, el } from "../dom.js";

const TOAST_WIDTH_RATIO = 0.9;
let host = null;

function ensureHost() {
    if (host && host.isConnected) return host;
    host = el("div", { position: "fixed", left: "0px", right: "0px", bottom: SIZE.taskbar + SPACE.lg + "px", zIndex: String(LAYER.toast),
        display: "flex", flexDirection: "column", alignItems: "center", gap: SPACE.sm + "px", pointerEvents: "none" });
    host.setAttribute("role", "status");
    document.body.appendChild(host);
    return host;
}

export function toast(message, isError = false) {
    const box = el("div", { padding: `${SPACE.sm}px ${SPACE.lg}px`, borderRadius: RADIUS.sm + "px", font: `${FONT.size.md}px ${FONT.ui}` }, { textContent: message });
    colored(box, (pal) => ({ background: isError ? pal.accent : pal.raised, color: isError ? pal.onAccent : pal.text,
        border: `1px solid ${isError ? pal.accent : pal.border}`, boxShadow: pal.shadow }));
    ensureHost().appendChild(box);
    const limit = Math.floor(window.innerWidth * TOAST_WIDTH_RATIO);
    if (box.offsetWidth > limit) box.style.width = limit + "px";
    setTimeout(() => box.remove(), TIMING.toast);
}
