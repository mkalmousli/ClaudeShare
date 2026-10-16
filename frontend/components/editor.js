// Plain-text editor window (Ctrl/Cmd+S to save, Tab inserts spaces).
import { files } from "../api.js";
import { FONT, SPACE } from "../consts.js";
import { add, colored, el, row } from "../dom.js";
import { button } from "../widgets.js";
import { icon } from "../icons.js";
import { baseName } from "../format.js";
import { confirmBox } from "./dialog.js";
import { toast } from "./toast.js";
import { openWindow } from "./window.js";

const INDENT = "    ";

function toolbar(win, onSave) {
    const bar = el("div", { ...row(), padding: SPACE.xs + "px", flexShrink: "0" });
    colored(bar, (pal) => ({ borderBottom: `1px solid ${pal.border}` }));
    return add(bar, button({ icon: icon("download"), text: "Save", title: "Save (Ctrl+S)", kind: "primary", scope: win.scope, onClick: onSave }));
}

export function openEditor(path, initial) {
    let dirty = false;
    let confirmed = false;
    const win = openWindow({ title: baseName(path), iconName: "file", onClose: (w) => {
        if (!dirty || confirmed) return true;
        confirmBox({ title: "Unsaved changes", message: `Close ${baseName(path)} without saving?`, okText: "Discard", danger: true })
            .then((ok) => { if (ok) { confirmed = true; w.close(); } });
        return false;
    } });
    const area = el("textarea", { flex: "1", border: "none", resize: "none", padding: SPACE.md + "px", font: `${FONT.size.md}px/1.5 ${FONT.mono}`, tabSize: "4", whiteSpace: "pre" },
        { value: initial, spellcheck: false });
    area.setAttribute("aria-label", "File contents");
    colored(area, (pal) => ({ background: pal.surface, color: pal.text }));
    area.style.outline = "none";
    const mark = (state) => { dirty = state; win.setTitle((state ? "● " : "") + baseName(path)); };
    const save = async () => {
        try { await files.write(path, area.value); mark(false); toast("Saved"); } catch (err) { toast(err.message, true); }
    };
    win.scope.on(area, "input", () => !dirty && mark(true));
    win.scope.on(area, "keydown", (ev) => {
        if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "s") { ev.preventDefault(); save(); }
        if (ev.key === "Tab") { ev.preventDefault(); document.execCommand("insertText", false, INDENT); }
    });
    add(win.body, toolbar(win, save), area);
    area.focus();
    return win;
}
