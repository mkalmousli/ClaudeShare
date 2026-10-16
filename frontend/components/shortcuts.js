// Global keyboard shortcuts (Alt+key opens an app; Alt+` / Alt+Shift+` cycles windows).
import { APPS } from "./launch.js";
import { cycleWindows } from "./windows.js";

export function installShortcuts(scope) {
    scope.on(document, "keydown", (ev) => {
        if (!ev.altKey || ev.ctrlKey || ev.metaKey) return;
        if (ev.code === "Backquote") { ev.preventDefault(); return cycleWindows(ev.shiftKey ? -1 : 1); }
        const app = APPS.find((item) => item.key === ev.key.toLowerCase());
        if (app) { ev.preventDefault(); app.open(); }
    }, true);
}
