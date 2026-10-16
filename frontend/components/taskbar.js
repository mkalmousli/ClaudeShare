// Bottom bar: launchers, one button per window, usage meter, theme switch, user menu, clock.
import { auth } from "../api.js";
import { FONT, LAYER, RADIUS, SIZE, SPACE, TIMING } from "../consts.js";
import { add, colored, clear, el, row } from "../dom.js";
import { button, interactive, activateOnKey } from "../widgets.js";
import { icon } from "../icons.js";
import { createScope } from "../listeners.js";
import { getUser } from "../state.js";
import { APPS } from "./launch.js";
import { openMenu } from "./menu.js";
import { themeToggle } from "./themeToggle.js";
import { usageMeter } from "./usageMeter.js";
import { openUsageWindow } from "./usageWindow.js";
import { isPhone } from "./windowLayout.js";
import { focusWindow, onWindowsChange, refresh } from "./windows.js";

function taskButton(win, scope) {
    const node = el("div", { ...row(SPACE.sm), height: SIZE.control + 2 + "px", padding: `0px ${SPACE.md}px`, borderRadius: RADIUS.sm + "px", cursor: "pointer", flexShrink: "0", font: `${FONT.size.md}px ${FONT.ui}` });
    add(node, icon(win.iconName, 16), el("span", { overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", width: isPhone() ? "0px" : "96px", display: isPhone() ? "none" : "block" }, { textContent: win.title }));
    interactive(node, (pal, flags) => ({ background: win.active ? pal.press : flags.hover || flags.focus ? pal.hover : "transparent", color: pal.text,
        boxShadow: flags.focus ? `0 0 0 2px ${pal.accent}` : win.active ? `inset 0 -2px 0 ${pal.accent}` : "none", opacity: win.minimized ? "0.55" : "1" }), scope);
    activateOnKey(node, scope);
    node.setAttribute("aria-pressed", String(win.active));
    node.title = win.title;
    scope.on(node, "click", () => (win.active && !win.minimized ? win.minimize() : focusWindow(win)));
    return node;
}

function clock(scope) {
    const node = el("span", { fontSize: FONT.size.sm + "px", opacity: "0.75", padding: `0px ${SPACE.sm}px`, whiteSpace: "nowrap", display: isPhone() ? "none" : "inline" });
    const tick = () => { node.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); };
    tick();
    const timer = setInterval(tick, TIMING.clock);
    scope.cleanup(() => clearInterval(timer));
    return node;
}

function userButton(scope) {
    return button({ icon: icon("user"), text: isPhone() ? "" : getUser(), title: "Account", scope, onClick: (ev) => {
        const box = ev.currentTarget.getBoundingClientRect();
        openMenu([{ label: "Sign out", icon: icon("logout", 16), onSelect: () => auth.logout().then(() => window.location.reload()) }], box.left, box.top - 56);
    } });
}

export function createTaskbar(scope) {
    const bar = el("div", { ...row(SPACE.sm), position: "fixed", left: "0px", right: "0px", bottom: "0px", height: SIZE.taskbar + "px", padding: `0px ${SPACE.sm}px`, zIndex: String(LAYER.taskbar), boxSizing: "border-box" });
    colored(bar, (pal) => ({ background: pal.surface, borderTop: `1px solid ${pal.border}`, color: pal.text }));
    const launchers = add(el("div", { ...row(2), flexShrink: "0" }), ...APPS.map((app) => button({ icon: icon(app.icon), text: isPhone() ? "" : app.label, title: `${app.label} (Alt+${app.key.toUpperCase()})`, scope, onClick: app.open })));
    const tasks = el("div", { ...row(SPACE.xs), flex: "1", overflowX: "auto", overflowY: "hidden" });
    let taskScope = createScope(tasks);
    scope.cleanup(onWindowsChange((wins) => {
        taskScope.dispose();
        taskScope = createScope(tasks);
        clear(tasks);
        wins.forEach((win) => tasks.appendChild(taskButton(win, taskScope)));
    }));
    scope.cleanup(() => taskScope.dispose());
    add(bar, launchers, el("div", { width: "1px", height: "22px" }), tasks, usageMeter(scope, openUsageWindow), themeToggle(scope), userButton(scope), clock(scope));
    refresh();
    return bar;
}
