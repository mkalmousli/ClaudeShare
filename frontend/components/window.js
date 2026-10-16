// A desktop window: frame, titlebar, controls. Content goes into win.body.
import { FONT, RADIUS, SIZE, SPACE } from "../consts.js";
import { add, colored, column, el, row } from "../dom.js";
import { button } from "../widgets.js";
import { icon } from "../icons.js";
import { createScope } from "../listeners.js";
import { release } from "../styles.js";
import { enableDrag } from "./windowDrag.js";
import { apply, cascade, clampRect, isPhone } from "./windowLayout.js";
import { addResizeHandles } from "./windowResize.js";
import { allWindows, focusWindow, refresh, register, unregister } from "./windows.js";

function buildFrame() {
    const root = el("div", { position: "absolute", pointerEvents: "auto", display: "flex", flexDirection: "column", overflow: "hidden", touchAction: "manipulation" });
    colored(root, (pal) => ({ background: pal.surface, border: `1px solid ${pal.border}`, boxShadow: pal.shadow, color: pal.text }));
    root.style.font = `${FONT.size.md}px ${FONT.ui}`;
    return root;
}

function buildTitlebar(win, parent) {
    const bar = el("div", { ...row(SPACE.sm), height: SIZE.titlebar + "px", padding: `0px ${SPACE.xs}px 0px ${SPACE.md}px`, flexShrink: "0", userSelect: "none", cursor: "default", touchAction: "none" });
    colored(bar, (pal) => ({ background: pal.raised, borderBottom: `1px solid ${pal.border}` }));
    const title = el("span", { flex: "1", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontWeight: "600" });
    win.titleEl = title;
    const ctl = (name, label, fn) => button({ icon: icon(name, 14), title: label, onClick: fn, scope: win.scope });
    add(bar, icon(win.iconName, 16), title,
        ctl("minimize", "Minimize", () => win.minimize()), ctl("maximize", "Maximize", () => win.toggleMaximize()), ctl("close", "Close", () => win.close()));
    parent.appendChild(bar);
    return bar;
}

export function openWindow({ title, iconName, onClose, onResize, width, height }) {
    const scope = createScope();
    const win = { scope, iconName, title, maximized: false, minimized: false, active: false, z: 0, onResize };
    win.el = buildFrame();
    win.rect = clampRect({ ...cascade(allWindows().length), ...(width ? { w: width } : {}), ...(height ? { h: height } : {}) });
    const bar = buildTitlebar(win, win.el);
    win.body = el("div", { ...column, flex: "1", position: "relative", overflow: "hidden" });
    add(win.el, win.body);
    win.setTitle = (value) => { win.title = value; win.titleEl.textContent = value; refresh(); };
    win.setActive = (on) => { win.active = on; win.el.style.opacity = on ? "1" : "0.96"; };
    win.minimize = () => { win.minimized = true; win.el.style.display = "none"; win.setActive(false); refresh(); };
    win.toggleMaximize = () => { if (!isPhone()) { win.maximized = !win.maximized; apply(win); } };
    win.close = () => {
        if (onClose && onClose(win) === false) return;
        unregister(win); scope.dispose(); release(win.el); win.el.remove();
    };
    scope.on(win.el, "pointerdown", () => !win.active && focusWindow(win), true);
    scope.on(bar, "dblclick", (ev) => !ev.target.closest("button") && win.toggleMaximize());
    enableDrag(win, bar, scope);
    addResizeHandles(win, scope);
    win.setTitle(title);
    document.getElementById("windows").appendChild(win.el);
    apply(win);
    register(win);
    return win;
}

