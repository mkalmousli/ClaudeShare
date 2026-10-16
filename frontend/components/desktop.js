// The desktop surface: wallpaper, icons, windows layer, taskbar; restores open terminals.
import { SIZE } from "../consts.js";
import { colored, el } from "../dom.js";
import { createScope } from "../listeners.js";
import { startUsage } from "../usageStore.js";
import { createDesktopIcons } from "./desktopIcons.js";
import { installShortcuts } from "./shortcuts.js";
import { createTaskbar } from "./taskbar.js";
import { restoreTerminals, openTerminal } from "./terminal.js";
import { apply, clampRect, isPhone } from "./windowLayout.js";
import { allWindows, refresh } from "./windows.js";

function layoutAll() {
    allWindows().forEach((win) => { win.rect = clampRect(win.rect); apply(win); });
}

// The taskbar's layout depends on the phone breakpoint, so rebuild it when that is crossed.
function mountTaskbar(host) {
    let scope = null;
    let node = null;
    let phone = null;
    const build = () => {
        scope && scope.dispose();
        scope = createScope();
        const next = createTaskbar(scope);
        node ? node.replaceWith(next) : host.appendChild(next);
        node = next;
        phone = isPhone();
        refresh();
    };
    build();
    return { sync: () => phone !== isPhone() && build() };
}

export async function mountDesktop(host) {
    const scope = createScope(host);
    const surface = el("div", { position: "fixed", top: "0px", left: "0px", overflow: "hidden" });
    colored(surface, (pal) => ({ background: pal.bg }));
    const windows = el("div", { position: "absolute", top: "0px", left: "0px", width: "100%", height: "100%", pointerEvents: "none" }, { id: "windows" });
    const size = () => {
        surface.style.width = window.innerWidth + "px";
        surface.style.height = window.innerHeight - SIZE.taskbar + "px";
        layoutAll();
    };
    surface.append(createDesktopIcons(scope), windows);
    host.appendChild(surface);
    const bar = mountTaskbar(host);
    size();
    scope.on(window, "resize", () => { size(); bar.sync(); });
    installShortcuts(scope);
    startUsage();
    if (!(await restoreTerminals())) openTerminal();
}
