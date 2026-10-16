// Simple image preview window.
import { DOWNLOAD_URL } from "../consts.js";
import { add, colored, el } from "../dom.js";
import { baseName } from "../format.js";
import { openWindow } from "./window.js";

export function openImage(path) {
    const win = openWindow({ title: baseName(path), iconName: "image", width: 640, height: 480 });
    const holder = el("div", { flex: "1", display: "flex", alignItems: "center", justifyContent: "center", overflow: "auto" });
    colored(holder, (pal) => ({ background: pal.bg }));
    const img = el("img", { objectFit: "contain", width: "100%", height: "100%" }, { src: `${DOWNLOAD_URL}?path=${encodeURIComponent(path)}&inline=1`, alt: baseName(path) });
    add(win.body, add(holder, img));
    return win;
}
