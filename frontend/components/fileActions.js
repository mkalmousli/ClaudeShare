// File manager actions. `fm` is the window's controller: { state, reload, go, status, win }.
import { DOWNLOAD_URL } from "../consts.js";
import { files } from "../api.js";
import { baseName, joinPath } from "../format.js";
import { getClipboard, setClipboard } from "../state.js";
import { askText, confirmBox } from "./dialog.js";
import { openEditor } from "./editor.js";
import { openImage } from "./imageViewer.js";
import { defaultArchiveName, isArchive, isImage, pathOf, selectedEntries, selectedPaths } from "./fileState.js";
import { toast } from "./toast.js";
import { uploadAll } from "./uploads.js";

async function attempt(fm, job, doneMessage) {
    try { await job(); doneMessage && toast(doneMessage); } catch (err) { toast(err.message, true); }
    await fm.reload();
}

export const download = (path) => { window.location.href = `${DOWNLOAD_URL}?path=${encodeURIComponent(path)}`; };

export async function openEntry(fm, entry) {
    const path = pathOf(fm.state, entry.name);
    if (entry.isDir) return fm.go(path);
    if (isImage(entry.name)) return openImage(path);
    try {
        const content = await files.read(path);
        content.binary ? download(path) : openEditor(path, content.content);
    } catch (err) { toast(err.message, true); }
}

export const newFolder = (fm) => askText({ title: "New folder", label: "Folder name", okText: "Create" })
    .then((name) => name && attempt(fm, () => files.makeDir(joinPath(fm.state.cwd, name))));
export const newFile = (fm) => askText({ title: "New file", label: "File name", okText: "Create" })
    .then((name) => name && attempt(fm, () => files.makeFile(joinPath(fm.state.cwd, name))));

export function rename(fm) {
    const [entry] = selectedEntries(fm.state);
    if (!entry) return;
    askText({ title: "Rename", label: "New name", value: entry.name, okText: "Rename" })
        .then((name) => name && name !== entry.name && attempt(fm, () => files.rename(pathOf(fm.state, entry.name), name)));
}

export async function remove(fm) {
    const paths = selectedPaths(fm.state);
    if (!paths.length) return;
    const noun = paths.length === 1 ? `"${baseName(paths[0])}"` : `${paths.length} items`;
    if (await confirmBox({ title: "Delete", message: `Delete ${noun}? This cannot be undone.`, okText: "Delete", danger: true })) {
        fm.state.selected.clear();
        attempt(fm, () => files.remove(paths));
    }
}

export const clip = (fm, mode) => selectedPaths(fm.state).length && setClipboard({ mode, paths: selectedPaths(fm.state) });

export function paste(fm, dest = fm.state.cwd) {
    const board = getClipboard();
    if (!board) return;
    const job = board.mode === "cut" ? () => files.move(board.paths, dest) : () => files.copy(board.paths, dest);
    board.mode === "cut" && setClipboard(null);
    attempt(fm, job);
}

export const moveInto = (fm, paths, dest) => attempt(fm, () => files.move(paths, dest));

export async function compress(fm) {
    const name = await askText({ title: "Compress", label: "Archive name (.zip or .tar.gz)", value: defaultArchiveName(fm.state), okText: "Compress" });
    name && attempt(fm, () => files.compress(selectedPaths(fm.state), fm.state.cwd, name), "Archive created");
}

export const extract = (fm) => attempt(fm, () => files.extract(selectedPaths(fm.state)[0]), "Extracted");
export const canExtract = (fm) => selectedEntries(fm.state).length === 1 && isArchive(selectedEntries(fm.state)[0].name);

export async function permissions(fm) {
    const [entry] = selectedEntries(fm.state);
    const mode = entry && await askText({ title: `Permissions for ${entry.name}`, label: "Octal mode, e.g. 644", value: entry.mode.toString(8), okText: "Apply" });
    mode && attempt(fm, () => files.chmod(pathOf(fm.state, entry.name), mode));
}

export function upload(fm, items, dest = fm.state.cwd) {
    attempt(fm, () => uploadAll(items, dest, (ratio) => fm.status(`Uploading… ${Math.round(ratio * 100)}%`)), "Upload complete");
}

