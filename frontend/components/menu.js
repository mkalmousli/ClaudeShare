// Context / dropdown menus with keyboard navigation.
import { FONT, LAYER, RADIUS, SIZE, SPACE } from "../consts.js";
import { add, colored, column, el, row } from "../dom.js";
import { activateOnKey, interactive } from "../widgets.js";
import { createScope } from "../listeners.js";

const MENU_WIDTH = 210;
let closeCurrent = null;

function itemNode(item, scope, close) {
    if (item.separator) return colored(el("div", { height: "1px", margin: `${SPACE.xs}px 0px` }), (pal) => ({ background: pal.border }));
    const node = el("div", { ...row(SPACE.md), height: SIZE.row + "px", padding: `0px ${SPACE.md}px`, borderRadius: RADIUS.sm + "px",
        cursor: item.disabled ? "default" : "pointer", font: `${FONT.size.md}px ${FONT.ui}` });
    add(node, item.icon || null, el("span", { flex: "1" }, { textContent: item.label }), item.hint ? el("span", { opacity: "0.55", fontSize: "11px" }, { textContent: item.hint }) : null);
    node.setAttribute("role", "menuitem");
    interactive(node, (pal, flags) => ({ background: (flags.hover || flags.focus) && !item.disabled ? pal.hover : "transparent",
        color: pal.text, opacity: item.disabled ? "0.4" : "1" }), scope);
    activateOnKey(node, scope);
    node.setAttribute("role", "menuitem");
    scope.on(node, "click", () => { if (item.disabled) return; close(); item.onSelect(); });
    return node;
}

export function openMenu(items, x, y) {
    closeCurrent && closeCurrent();
    const scope = createScope();
    const box = el("div", { ...column, position: "fixed", zIndex: String(LAYER.menu), width: MENU_WIDTH + "px", padding: SPACE.xs + "px", borderRadius: RADIUS.md + "px" });
    colored(box, (pal) => ({ background: pal.raised, border: `1px solid ${pal.border}`, boxShadow: pal.shadow, color: pal.text }));
    box.setAttribute("role", "menu");
    const close = () => { scope.dispose(); box.remove(); closeCurrent = null; };
    closeCurrent = close;
    items.forEach((item) => box.appendChild(itemNode(item, scope, close)));
    document.body.appendChild(box);
    const left = Math.min(x, window.innerWidth - MENU_WIDTH - 8);
    box.style.left = Math.max(8, left) + "px";
    box.style.top = Math.max(8, Math.min(y, window.innerHeight - box.offsetHeight - 8)) + "px";
    scope.on(document, "pointerdown", (ev) => !box.contains(ev.target) && close(), true);
    scope.on(document, "keydown", (ev) => ev.key === "Escape" && close(), true);
    scope.on(window, "blur", close);
    const first = box.querySelector("[role=menuitem]");
    first && first.focus();
    scope.on(box, "keydown", (ev) => {
        const nodes = [...box.querySelectorAll("[role=menuitem]")];
        const at = nodes.indexOf(document.activeElement);
        if (ev.key === "ArrowDown") { ev.preventDefault(); nodes[(at + 1) % nodes.length].focus(); }
        if (ev.key === "ArrowUp") { ev.preventDefault(); nodes[(at - 1 + nodes.length) % nodes.length].focus(); }
    });
    return close;
}
