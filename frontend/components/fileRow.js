// One row of the file list.
import { FONT, SIZE, SPACE } from "../consts.js";
import { add, el, row } from "../dom.js";
import { icon } from "../icons.js";
import { formatBytes, formatDate } from "../format.js";
import { iconFor } from "./fileState.js";
import { isPhone } from "./windowLayout.js";

export function buildRow(entry, grid) {
    const node = el("div", { display: "grid", gridTemplateColumns: grid, alignItems: "center", height: SIZE.row + "px", padding: `0px ${SPACE.md}px`, cursor: "default", userSelect: "none" });
    node.dataset.name = entry.name;
    node.draggable = true;
    const name = add(el("div", { ...row(SPACE.sm), overflow: "hidden" }), icon(iconFor(entry), 16),
        el("span", { overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", opacity: entry.name.startsWith(".") ? "0.6" : "1" }, { textContent: entry.name }));
    const cells = [name, el("span", { opacity: "0.65" }, { textContent: entry.isDir ? "—" : formatBytes(entry.size) })];
    if (!isPhone()) cells.push(el("span", { opacity: "0.65" }, { textContent: formatDate(entry.mtime) }), el("span", { opacity: "0.65", fontFamily: FONT.mono, fontSize: "11px" }, { textContent: entry.mode.toString(8) }));
    return add(node, ...cells);
}
