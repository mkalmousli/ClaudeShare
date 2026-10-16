// File manager window: wires state, toolbar, breadcrumbs, list and status bar.
import { files } from "../api.js";
import { FONT, SPACE } from "../consts.js";
import { colored, el } from "../dom.js";
import { baseName } from "../format.js";
import { createCrumbs } from "./fileCrumbs.js";
import { createFileList } from "./fileList.js";
import { createState, visibleEntries } from "./fileState.js";
import { createToolbar } from "./fileToolbar.js";
import { toast } from "./toast.js";
import { openWindow } from "./window.js";

export function openFileManager(path = "/") {
    const win = openWindow({ title: "Files", iconName: "folder", width: 840, height: 520 });
    const fm = { win, scope: win.scope, state: createState(path), message: "" };
    const statusBar = el("div", { padding: `${SPACE.xs}px ${SPACE.md}px`, fontSize: FONT.size.sm + "px", flexShrink: "0" });
    colored(statusBar, (pal) => ({ color: pal.muted, borderTop: `1px solid ${pal.border}`, background: pal.raised }));

    fm.status = (message) => {
        fm.message = message === undefined ? "" : message;
        const { state } = fm;
        const info = `${visibleEntries(state).length} items` + (state.selected.size ? ` · ${state.selected.size} selected` : "");
        statusBar.textContent = fm.message ? `${info} · ${fm.message}` : info;
    };
    const crumbs = createCrumbs(fm);
    const list = createFileList(fm);
    fm.render = () => { crumbs.render(); list.render(); fm.status(); win.setTitle(`Files — ${baseName(fm.state.cwd)}`); };
    fm.go = async (target, record = true) => {
        try {
            const listing = await files.list(target);
            if (record && listing.path !== fm.state.cwd) { fm.state.back.push(fm.state.cwd); fm.state.forward.length = 0; }
            Object.assign(fm.state, { cwd: listing.path, entries: listing.entries, selected: new Set(), anchor: null, filter: "" });
            fm.render();
        } catch (err) { toast(err.message, true); }
    };
    fm.reload = () => files.list(fm.state.cwd).then((listing) => {
        fm.state.entries = listing.entries;
        fm.state.selected = new Set([...fm.state.selected].filter((n) => listing.entries.some((e) => e.name === n)));
        fm.render();
        fm.status("");
    }).catch((err) => toast(err.message, true));
    fm.toggleHidden = () => { fm.state.hidden = !fm.state.hidden; fm.render(); };
    win.body.append(createToolbar(fm, crumbs), list.el, statusBar);
    fm.go(path, false).then(() => list.focus());
    return win;
}
