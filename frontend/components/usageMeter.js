// Always-visible usage meter in the taskbar. Click for the details window.
import { FONT, METER, RADIUS, SPACE } from "../consts.js";
import { add, colored, el, row } from "../dom.js";
import { interactive, activateOnKey } from "../widgets.js";
import { formatCountdown, percent } from "../format.js";
import { isPhone } from "./windowLayout.js";
import { onUsage } from "../usageStore.js";

export function usageMeter(scope, onOpen) {
    const node = el("div", { ...row(SPACE.sm), height: "32px", padding: `0px ${SPACE.md}px`, borderRadius: RADIUS.sm + "px", cursor: "pointer", flexShrink: "0", font: `${FONT.size.sm}px ${FONT.ui}` });
    node.setAttribute("aria-label", "Claude usage");
    const track = el("div", { width: METER.width + "px", height: METER.height + "px", borderRadius: METER.height + "px", overflow: "hidden", flexShrink: "0" });
    const bar = el("div", { height: "100%", width: "0px" });
    const note = el("span", { whiteSpace: "nowrap" }, { textContent: "Usage" });
    colored(track, (pal) => ({ background: pal.border }));
    colored(bar, (pal) => ({ background: pal.accent }));
    interactive(node, (pal, flags) => ({ background: flags.hover || flags.focus ? pal.hover : "transparent", color: pal.text, boxShadow: flags.focus ? `0 0 0 2px ${pal.accent}` : "none" }), scope);
    activateOnKey(node, scope);
    scope.on(node, "click", onOpen);
    add(track, bar);
    add(node, track, note);
    const sizeTrack = () => { track.style.width = (isPhone() ? METER.width / 2 : METER.width) + "px"; note.style.display = isPhone() ? "none" : "inline"; };
    sizeTrack();
    scope.on(window, "resize", sizeTrack);
    scope.cleanup(onUsage((data) => {
        const pct = Math.min(100, data.percent);
        bar.style.width = pct + "%";
        note.textContent = `You ${data.points.toFixed(1)}% of ${data.share}% · resets ${formatCountdown(data.resetsAt)}` + (data.plan && data.plan.sevenDay != null ? ` · Plan ${percent(data.plan.sevenDay)}` : "");
        note.style.fontWeight = data.percent >= METER.warn ? "700" : "400";
        node.title = data.blocked ? "Limit reached: Claude is paused until the period resets" : "Claude usage this " + data.period;
    }));
    return node;
}
