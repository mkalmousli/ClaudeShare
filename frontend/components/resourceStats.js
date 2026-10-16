// Live per-user resource usage (RAM, CPU, processes, disk) against the limits set by the admin.
import { SPACE } from "../consts.js";
import { add, colored, el, row } from "../dom.js";
import { formatBytes } from "../format.js";
import { stat } from "./usageWindow.js";

const MB = 1024 * 1024;
const ratio = (used, limit) => (limit ? (100 * used) / limit : 0);
const size = (megabytes) => formatBytes(megabytes * MB);

export function resourceBlock(res) {
    const line = (name, used, limit, text) => stat(name, text, ratio(used, limit));
    const grid = add(el("div", { ...row(SPACE.md), flexWrap: "wrap" }),
        line("RAM", res.memUsed, res.memLimit, `${size(res.memUsed)} / ${size(res.memLimit)}`),
        line("CPU", res.cpuUsed, res.cpuLimit, `${res.cpuUsed.toFixed(2)} / ${res.cpuLimit} cores`),
        line("Processes", res.procsUsed, res.procsLimit, `${res.procsUsed} / ${res.procsLimit}`),
        line("Disk", res.diskUsed, res.diskLimit, `${size(res.diskUsed)} / ${size(res.diskLimit)}`));
    if (!res.notice) return grid;
    const note = el("div", { fontWeight: "600" }, { textContent: res.notice });
    colored(note, (pal) => ({ color: pal.accent }));
    return add(el("div", { display: "flex", flexDirection: "column", gap: SPACE.sm + "px" }), note, grid);
}
