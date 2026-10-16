// Context-menu contents for the file list.
import { icon } from "../icons.js";
import { getClipboard } from "../state.js";
import { canExtract, clip, compress, download, extract, newFile, newFolder, openEntry, paste, permissions, remove, rename } from "./fileActions.js";
import { pathOf, selectedEntries } from "./fileState.js";
import { openTerminal } from "./terminal.js";

const SEP = { separator: true };
const item = (label, iconName, onSelect, extra = {}) => ({ label, icon: icon(iconName, 16), onSelect, ...extra });

export function entryMenu(fm) {
    const chosen = selectedEntries(fm.state);
    const single = chosen.length === 1;
    const first = chosen[0];
    const folderPath = single && first.isDir ? pathOf(fm.state, first.name) : null;
    return [
        item("Open", "forward", () => chosen.forEach((e) => openEntry(fm, e))),
        folderPath && item("Open terminal here", "terminal", () => openTerminal({ cwd: folderPath })),
        item("Download", "download", () => chosen.forEach((e) => download(pathOf(fm.state, e.name)))),
        SEP,
        item("Cut", "cut", () => clip(fm, "cut"), { hint: "Ctrl+X" }),
        item("Copy", "copy", () => clip(fm, "copy"), { hint: "Ctrl+C" }),
        folderPath && item("Paste into folder", "paste", () => paste(fm, folderPath), { disabled: !getClipboard() }),
        SEP,
        item("Rename", "edit", () => rename(fm), { hint: "F2", disabled: !single }),
        item("Permissions…", "lock", () => permissions(fm), { disabled: !single }),
        item("Compress…", "archive", () => compress(fm)),
        canExtract(fm) && item("Extract here", "archive", () => extract(fm)),
        SEP,
        item("Delete", "trash", () => remove(fm), { hint: "Del" }),
    ].filter(Boolean);
}

export function backgroundMenu(fm) {
    return [
        item("New folder", "plus", () => newFolder(fm)),
        item("New file", "newfile", () => newFile(fm)),
        item("Paste", "paste", () => paste(fm), { hint: "Ctrl+V", disabled: !getClipboard() }),
        SEP,
        item("Open terminal here", "terminal", () => openTerminal({ cwd: fm.state.cwd })),
        item("Refresh", "refresh", () => fm.reload()),
        item(fm.state.hidden ? "Hide hidden files" : "Show hidden files", "eye", () => fm.toggleHidden()),
    ];
}
