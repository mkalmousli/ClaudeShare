// Element-creation helpers. All markup is built with DOM APIs; styles go through .style.
import { SPACE } from "./consts.js";
import { themed } from "./styles.js";

export function el(tag, styles = {}, props = {}) {
    const node = document.createElement(tag);
    Object.assign(node.style, styles);
    Object.assign(node, props);
    return node;
}

export function add(parent, ...kids) {
    kids.filter(Boolean).forEach((kid) => parent.appendChild(kid));
    return parent;
}

export function label(node, name) {
    node.setAttribute("aria-label", name);
    return node;
}

export function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
    return node;
}

export const fill = { position: "absolute", top: "0px", left: "0px", right: "0px", bottom: "0px" };
export const row = (gap = SPACE.sm) => ({ display: "flex", alignItems: "center", gap: gap + "px" });
export const column = { display: "flex", flexDirection: "column" };

export function text(parent, content, styles = {}) {
    const span = el("span", styles, { textContent: content });
    return parent ? add(parent, span) : span;
}

export function colored(node, pick) {
    return themed(node, (pal) => Object.assign(node.style, pick(pal)));
}
