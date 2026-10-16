// Detailed usage: period totals, plan usage and a table of Claude sessions.
import { FONT, METER, RADIUS, SPACE } from "../consts.js";
import { add, clear, colored, column, el, row } from "../dom.js";
import { formatCountdown, formatDate, formatTokens, percent, baseName } from "../format.js";
import { onUsage } from "../usageStore.js";
import { openWindow } from "./window.js";
import { focusWindow } from "./windows.js";

const COLUMNS = ["Session", "Project", "Last active", "Msgs", "Tokens", ""];
const GRID = "1fr 1.4fr 1.2fr 0.6fr 0.8fr 0.5fr";

function bar(valuePct) {
    const track = el("div", { height: METER.height + 2 + "px", borderRadius: "6px", overflow: "hidden", flex: "1" });
    const fill = el("div", { height: "100%", width: Math.min(100, valuePct) + "%" });
    colored(track, (pal) => ({ background: pal.border }));
    colored(fill, (pal) => ({ background: pal.accent }));
    return add(track, fill);
}

function stat(name, value, pct) {
    const box = el("div", { ...column, gap: SPACE.xs + "px", flex: "1", padding: SPACE.md + "px", borderRadius: RADIUS.md + "px" });
    colored(box, (pal) => ({ border: `1px solid ${pal.border}`, background: pal.raised }));
    const head = add(el("div", { ...row(), justifyContent: "space-between" }), el("span", { opacity: "0.65" }, { textContent: name }), el("b", {}, { textContent: value }));
    return add(box, head, pct == null ? null : bar(pct));
}

function sessionRow(item) {
    const line = el("div", { display: "grid", gridTemplateColumns: GRID, gap: SPACE.sm + "px", padding: `${SPACE.sm}px ${SPACE.md}px`, alignItems: "center" });
    colored(line, (pal) => ({ borderBottom: `1px solid ${pal.border}` }));
    const cells = [item.id.slice(0, 8), baseName(item.project), formatDate(item.last), item.messages, formatTokens(item.tokens), item.live ? "● live" : ""];
    cells.forEach((value, idx) => {
        const cell = el("span", { overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }, { textContent: String(value) });
        if (idx === 5) colored(cell, (pal) => ({ color: pal.accent, fontWeight: "700" }));
        line.appendChild(cell);
    });
    return line;
}

function render(content, data) {
    clear(content);
    const stats = add(el("div", { ...row(SPACE.md), flexWrap: "wrap" }),
        stat(`Your share (${data.share}% of the plan)`, `${data.points.toFixed(1)}% used  (${percent(data.percent)} of your slice)`, data.percent),
        stat("Resets in", formatCountdown(data.resetsAt), null));
    const plan = data.plan ? add(el("div", { ...row(SPACE.md), flexWrap: "wrap" }),
        stat("Plan · 5 hours", data.plan.fiveHour == null ? "n/a" : percent(data.plan.fiveHour), data.plan.fiveHour),
        stat("Plan · 7 days", data.plan.sevenDay == null ? "n/a" : percent(data.plan.sevenDay), data.plan.sevenDay)) : null;
    const head = el("div", { display: "grid", gridTemplateColumns: GRID, gap: SPACE.sm + "px", padding: `${SPACE.sm}px ${SPACE.md}px`, opacity: "0.6", fontSize: FONT.size.sm + "px" });
    COLUMNS.forEach((name) => add(head, el("span", {}, { textContent: name })));
    const empty = el("div", { padding: SPACE.lg + "px", opacity: "0.6" }, { textContent: "No Claude sessions yet this period." });
    add(content, data.blocked ? el("b", {}, { textContent: "Limit reached: Claude is paused until the period resets." }) : null, stats, plan, head,
        ...(data.sessions.length ? data.sessions.map(sessionRow) : [empty]));
}

let open = null;
export function openUsageWindow() {
    if (open) return focusWindow(open);
    const win = openWindow({ title: "Usage", iconName: "chart", width: 640, height: 460, onClose: () => { stop(); open = null; return true; } });
    const content = el("div", { ...column, gap: SPACE.md + "px", padding: SPACE.lg + "px", overflowY: "auto", flex: "1", font: `${FONT.size.md}px ${FONT.ui}` });
    add(win.body, content);
    const stop = onUsage((data) => render(content, data));
    open = win;
    return win;
}
