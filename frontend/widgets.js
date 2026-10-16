// Interactive widgets: buttons and inputs with listener-driven hover/focus/pressed styling.
import { FONT, RADIUS, SIZE, SPACE } from "./consts.js";
import { el, label } from "./dom.js";
import { appScope } from "./listeners.js";
import { palette, themed } from "./styles.js";

// Hover / focus / pressed states are tracked with listeners and repainted by styleFor().
export function interactive(node, styleFor, scope = appScope) {
    const flags = { hover: false, focus: false, down: false };
    const paint = () => Object.assign(node.style, styleFor(palette(), flags));
    const set = (key, value) => () => { flags[key] = value; paint(); };
    node.style.webkitTapHighlightColor = "transparent";
    node.style.outline = "none";
    themed(node, paint);
    scope.on(node, "pointerenter", set("hover", true));
    scope.on(node, "pointerleave", () => { flags.hover = false; flags.down = false; paint(); });
    scope.on(node, "pointerdown", set("down", true));
    scope.on(node, "pointerup", set("down", false));
    scope.on(node, "focus", set("focus", true));
    scope.on(node, "blur", set("focus", false));
    return node;
}

export function activateOnKey(node, scope = appScope) {
    node.tabIndex = 0;
    node.setAttribute("role", node.getAttribute("role") || "button");
    scope.on(node, "keydown", (ev) => {
        if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); node.click(); }
    });
}

const focusRing = (pal, flags) => (flags.focus ? `0 0 0 2px ${pal.accent}` : "none");

export function buttonStyle(pal, flags, kind) {
    const primary = kind === "primary";
    const base = primary ? pal.accent : "transparent";
    const hover = primary ? pal.accent : flags.down ? pal.press : pal.hover;
    return {
        background: flags.hover || flags.down ? hover : base,
        color: primary ? pal.onAccent : pal.text,
        boxShadow: focusRing(pal, flags),
        opacity: primary && flags.down ? "0.85" : "1",
    };
}

export function button({ text = "", icon = null, title = "", kind = "ghost", onClick, scope = appScope }) {
    const node = el("button", {
        display: "inline-flex", alignItems: "center", justifyContent: "center", gap: SPACE.sm + "px",
        height: SIZE.control + "px", padding: `0px ${text ? SPACE.md : SPACE.sm}px`, border: "none",
        borderRadius: RADIUS.sm + "px", cursor: "pointer", font: `${FONT.size.md}px ${FONT.ui}`, flexShrink: "0",
    }, { type: "button", title: title || text });
    if (icon) node.appendChild(icon);
    if (text) node.appendChild(document.createTextNode(text));
    label(node, title || text);
    interactive(node, (pal, flags) => buttonStyle(pal, flags, kind), scope);
    if (onClick) scope.on(node, "click", onClick);
    return node;
}

export function textField({ placeholder = "", type = "text", value = "", onEnter, scope = appScope }) {
    const node = el("input", {
        height: SIZE.control + 4 + "px", padding: `0px ${SPACE.md}px`, borderRadius: RADIUS.sm + "px",
        font: `${FONT.size.lg}px ${FONT.ui}`, boxSizing: "border-box", width: "100%",
    }, { type, placeholder, value });
    label(node, placeholder || "field");
    node.style.webkitTapHighlightColor = "transparent";
    interactive(node, (pal, flags) => ({
        background: pal.bg, color: pal.text, border: `1px solid ${flags.focus ? pal.accent : pal.border}`,
        boxShadow: flags.focus ? `0 0 0 1px ${pal.accent}` : "none",
    }), scope);
    if (onEnter) scope.on(node, "keydown", (ev) => ev.key === "Enter" && onEnter());
    return node;
}
