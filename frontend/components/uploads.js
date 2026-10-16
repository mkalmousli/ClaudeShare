// Uploads via streaming PUT (per file), including whole folders from drag-and-drop.
import { UPLOAD_URL } from "../consts.js";
import { joinPath } from "../format.js";

function putFile(file, destPath, onBytes) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("PUT", `${UPLOAD_URL}?path=${encodeURIComponent(destPath)}`);
        xhr.upload.onprogress = (ev) => onBytes(ev.loaded);
        xhr.onload = () => (xhr.status === 200 ? resolve() : reject(new Error(`Upload of ${file.name} failed`)));
        xhr.onerror = () => reject(new Error(`Upload of ${file.name} failed`));
        xhr.send(file);
    });
}

export async function uploadAll(items, destDir, onProgress) {
    const total = items.reduce((sum, item) => sum + item.file.size, 0) || 1;
    let done = 0;
    for (const item of items) {
        await putFile(item.file, joinPath(destDir, item.rel), (loaded) => onProgress(Math.min(1, (done + loaded) / total)));
        done += item.file.size;
        onProgress(Math.min(1, done / total));
    }
}

const readEntries = (reader) => new Promise((resolve, reject) => reader.readEntries(resolve, reject));
const toFile = (entry) => new Promise((resolve, reject) => entry.file(resolve, reject));

async function walk(entry, prefix, out) {
    if (entry.isFile) return out.push({ file: await toFile(entry), rel: prefix + entry.name });
    const reader = entry.createReader();
    for (let batch = await readEntries(reader); batch.length; batch = await readEntries(reader)) {
        for (const child of batch) await walk(child, `${prefix}${entry.name}/`, out);
    }
}

export async function collectDropped(dataTransfer) {
    const out = [];
    const entries = [...dataTransfer.items].map((item) => item.webkitGetAsEntry && item.webkitGetAsEntry()).filter(Boolean);
    for (const entry of entries) await walk(entry, "", out);
    return out;
}

export const fromFileList = (list) => [...list].map((file) => ({ file, rel: file.webkitRelativePath || file.name }));
