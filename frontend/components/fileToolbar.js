// Toolbar: navigation, creation, clipboard, delete, upload, filter.
import { SPACE } from "../consts.js";
import { add, colored, el, row } from "../dom.js";
import { button, textField } from "../widgets.js";
import { icon } from "../icons.js";
import { parentPath } from "../format.js";
import { clip, compress, download, newFile, newFolder, paste, remove, rename, upload } from "./fileActions.js";
import { fromFileList } from "./uploads.js";
import { selectedPaths } from "./fileState.js";
import { openTerminal } from "./terminal.js";

function picker(fm, folder) {
    const input = el("input", { display: "none" }, { type: "file", multiple: true });
    if (folder) input.webkitdirectory = true;
    fm.scope.on(input, "change", () => { upload(fm, fromFileList(input.files)); input.value = ""; });
    return input;
}

export function createToolbar(fm, crumbs) {
    const { scope, state } = fm;
    const pick = picker(fm, false);
    const tool = (name, title, fn) => button({ icon: icon(name), title, scope, onClick: fn });
    const nav = (list, other) => () => {
        const target = list.pop();
        if (target == null) return;
        other.push(state.cwd);
        fm.go(target, false);
    };
    const filter = textField({ placeholder: "Filter…", scope });
    filter.style.width = "130px";
    scope.on(filter, "input", () => { state.filter = filter.value; fm.render(); });
    const group = (...kids) => add(el("div", { ...row(2), flexShrink: "0" }), ...kids);
    const bar = el("div", { ...row(SPACE.sm), flexWrap: "wrap", padding: `${SPACE.xs}px ${SPACE.sm}px`, flexShrink: "0" });
    colored(bar, (pal) => ({ background: pal.raised, borderBottom: `1px solid ${pal.border}` }));
    add(bar,
        group(tool("back", "Back", nav(state.back, state.forward)), tool("forward", "Forward", nav(state.forward, state.back)),
            tool("up", "Up one folder", () => fm.go(parentPath(state.cwd))), tool("refresh", "Refresh", () => fm.reload())),
        crumbs.el,
        group(tool("plus", "New folder", () => newFolder(fm)), tool("newfile", "New file", () => newFile(fm)),
            tool("upload", "Upload files", () => pick.click()), tool("download", "Download selected", () => selectedPaths(state).forEach(download)),
            tool("cut", "Cut", () => clip(fm, "cut")), tool("copy", "Copy", () => clip(fm, "copy")), tool("paste", "Paste", () => paste(fm)),
            tool("edit", "Rename", () => rename(fm)), tool("archive", "Compress", () => compress(fm)), tool("trash", "Delete", () => remove(fm)),
            tool("eye", "Show / hide hidden files", () => fm.toggleHidden()), tool("terminal", "Open terminal here", () => openTerminal({ cwd: state.cwd }))),
        filter, pick);
    return bar;
}
