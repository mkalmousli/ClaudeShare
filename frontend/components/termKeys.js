// On-screen helper keys for touch devices (Esc, Tab, Ctrl, arrows).
import { SPACE } from "../consts.js";
import { add, colored, el, row } from "../dom.js";
import { button } from "../widgets.js";

const KEYS = [["Esc", "\x1b"], ["Tab", "\t"], ["Ctrl", null], ["↑", "\x1b[A"], ["↓", "\x1b[B"], ["←", "\x1b[D"], ["→", "\x1b[C"], ["|", "|"], ["~", "~"], ["/", "/"]];

export const isTouch = () => window.matchMedia("(pointer: coarse)").matches;

export function createKeyBar(send, scope) {
    const bar = el("div", { ...row(SPACE.xs), padding: SPACE.xs + "px", overflowX: "auto", flexShrink: "0" });
    colored(bar, (pal) => ({ background: pal.raised, borderTop: `1px solid ${pal.border}` }));
    const state = { ctrl: false };
    KEYS.forEach(([text, seq]) => {
        const node = button({ text, scope, title: text, onClick: () => {
            if (seq === null) { state.ctrl = !state.ctrl; node.setAttribute("aria-pressed", String(state.ctrl)); } else send(seq);
        } });
        add(bar, node);
    });
    const withCtrl = (data) => {
        if (!state.ctrl || data.length !== 1) return data;
        state.ctrl = false;
        return String.fromCharCode(data.toUpperCase().charCodeAt(0) & 31);
    };
    return { bar, withCtrl };
}
