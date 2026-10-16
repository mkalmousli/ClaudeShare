// Breadcrumb path bar; segments are also drop targets for moving files.
import { FONT, SPACE } from "../consts.js";
import { add, clear, el, row } from "../dom.js";
import { button } from "../widgets.js";
import { moveInto } from "./fileActions.js";
import { DRAG_TYPE } from "./fileDrag.js";

export function createCrumbs(fm) {
    const bar = el("div", { ...row(2), flex: "1 1 240px", overflowX: "auto", flexWrap: "nowrap", font: `${FONT.size.md}px ${FONT.ui}`, padding: `0px ${SPACE.xs}px` });
    bar.setAttribute("aria-label", "Path");
    const segmentButton = (text, path) => {
        const node = button({ text, title: path, scope: fm.scope, onClick: () => fm.go(path) });
        fm.scope.on(node, "dragover", (ev) => ev.preventDefault());
        fm.scope.on(node, "drop", (ev) => {
            ev.preventDefault();
            const paths = ev.dataTransfer.getData(DRAG_TYPE);
            paths && moveInto(fm, JSON.parse(paths), path);
        });
        return node;
    };
    const render = () => {
        clear(bar);
        const parts = fm.state.cwd.split("/").filter(Boolean);
        add(bar, segmentButton("Home", "/"));
        parts.forEach((part, idx) => {
            add(bar, el("span", { opacity: "0.4" }, { textContent: "/" }), segmentButton(part, "/" + parts.slice(0, idx + 1).join("/")));
        });
    };
    return { el: bar, render };
}
