// Launcher icons on the desktop surface (double-click, or Enter; single tap on phones).
import { FONT, RADIUS, SPACE } from "../consts.js";
import { add, column, el } from "../dom.js";
import { interactive, activateOnKey } from "../widgets.js";
import { icon } from "../icons.js";
import { APPS } from "./launch.js";
import { isPhone } from "./windowLayout.js";

const TILE = 84;

export function createDesktopIcons(scope) {
    const holder = el("div", { ...column, position: "absolute", top: SPACE.lg + "px", left: SPACE.sm + "px", gap: SPACE.sm + "px" });
    APPS.forEach((app) => {
        const tile = el("div", { ...column, alignItems: "center", gap: SPACE.xs + "px", width: TILE + "px", padding: SPACE.sm + "px 0px", borderRadius: RADIUS.md + "px", cursor: "pointer", userSelect: "none", font: `${FONT.size.sm}px ${FONT.ui}` });
        add(tile, icon(app.icon, 30), el("span", {}, { textContent: app.label }));
        tile.setAttribute("aria-label", `Open ${app.label}`);
        interactive(tile, (pal, flags) => ({ background: flags.hover || flags.focus ? pal.hover : "transparent", color: pal.text, boxShadow: flags.focus ? `0 0 0 2px ${pal.accent}` : "none" }), scope);
        activateOnKey(tile, scope);
        scope.on(tile, "dblclick", app.open);
        scope.on(tile, "click", (ev) => isPhone() && ev.detail < 2 && app.open());
        holder.appendChild(tile);
    });
    return holder;
}
