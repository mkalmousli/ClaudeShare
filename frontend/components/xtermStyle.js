// xterm.js ships a stylesheet; instead of a CSS file we apply its essential layout rules
// as inline styles, to existing elements and (via MutationObserver) to ones it creates later.
const OFFSCREEN = "-9999em";
const RULES = [
    [".xterm", { position: "relative", userSelect: "none", cursor: "text" }],
    [".xterm-helpers", { position: "absolute", top: "0px", zIndex: "5" }],
    [".xterm-helper-textarea", { padding: "0px", border: "0px", margin: "0px", position: "absolute", opacity: "0", left: OFFSCREEN,
        top: "0px", width: "0px", height: "0px", zIndex: "-5", whiteSpace: "nowrap", overflow: "hidden", resize: "none" }],
    [".composition-view", { display: "none", position: "absolute", whiteSpace: "nowrap", zIndex: "1" }],
    [".xterm-viewport", { overflowY: "scroll", cursor: "default", position: "absolute", right: "0px", left: "0px", top: "0px", bottom: "0px" }],
    [".xterm-screen", { position: "relative" }],
    [".xterm-scroll-area", { visibility: "hidden" }],
    [".xterm-char-measure-element", { display: "inline-block", visibility: "hidden", position: "absolute", top: "0px", left: OFFSCREEN, lineHeight: "normal" }],
];

function styleTree(root) {
    if (root.nodeType !== 1) return;
    RULES.forEach(([selector, styles]) => {
        if (root.matches(selector)) Object.assign(root.style, styles);
        root.querySelectorAll(selector).forEach((node) => Object.assign(node.style, styles));
    });
}

export function watchXtermStyles(holder) {
    styleTree(holder);
    const observer = new MutationObserver((records) => records.forEach((rec) => rec.addedNodes.forEach(styleTree)));
    observer.observe(holder, { childList: true, subtree: true });
    return () => observer.disconnect();
}

export function paintViewport(holder, color) {
    const viewport = holder.querySelector(".xterm-viewport");
    if (viewport) viewport.style.backgroundColor = color;
}
