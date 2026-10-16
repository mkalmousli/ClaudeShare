// Stroke icons drawn from SVG path data (24x24 grid).
import { SIZE } from "./consts.js";

const SVG_NS = "http://www.w3.org/2000/svg";
const PATHS = {
    terminal: "M4 17l6-6-6-6M12 19h8",
    folder: "M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z",
    file: "M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8zM14 3v5h5",
    image: "M4 5h16v14H4zM8 10a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM4 17l5-5 4 4 3-3 4 4",
    archive: "M4 4h16v4H4zM5 8v12h14V8M10 12h4",
    close: "M6 6l12 12M18 6L6 18",
    minimize: "M5 19h14",
    maximize: "M5 5h14v14H5z",
    up: "M12 19V5M5 12l7-7 7 7",
    back: "M19 12H5M12 19l-7-7 7-7",
    forward: "M5 12h14M12 5l7 7-7 7",
    refresh: "M20 11a8 8 0 10-2.3 5.7M20 4v7h-7",
    plus: "M12 5v14M5 12h14",
    newfile: "M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8zM14 3v5h5M12 12v6M9 15h6",
    upload: "M12 16V4M6 10l6-6 6 6M4 20h16",
    download: "M12 4v12M6 10l6 6 6-6M4 20h16",
    trash: "M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3",
    edit: "M4 20h4L19 9l-4-4L4 16zM13 7l4 4",
    copy: "M8 8h12v12H8zM16 8V4H4v12h4",
    cut: "M6 20a2 2 0 100-4 2 2 0 000 4zM6 8a2 2 0 100-4 2 2 0 000 4zM8 7.5l12 9M8 16.5l12-9",
    paste: "M9 4h6v3H9zM7 5H5v16h14V5h-2M9 12h6M9 16h6",
    spark: "M12 3v6M12 15v6M3 12h6M15 12h6M6 6l3 3M15 15l3 3M18 6l-3 3M9 15l-3 3",
    user: "M12 12a4 4 0 100-8 4 4 0 000 8zM4 21a8 8 0 0116 0",
    logout: "M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9",
    chart: "M4 20V10M10 20V4M16 20v-7M22 20H2",
    sun: "M12 16a4 4 0 100-8 4 4 0 000 8zM12 2v2M12 20v2M4 12H2M22 12h-2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5",
    moon: "M20 14.5A8 8 0 019.5 4 8 8 0 1020 14.5z",
    lock: "M6 11h12v10H6zM8 11V7a4 4 0 018 0v4",
    home: "M3 11l9-8 9 8M5 10v10h14V10",
    eye: "M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM12 15a3 3 0 100-6 3 3 0 000 6z",
};

export function icon(name, size = SIZE.icon) {
    const svg = document.createElementNS(SVG_NS, "svg");
    const path = document.createElementNS(SVG_NS, "path");
    const attrs = { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor",
        "stroke-width": 2, "stroke-linecap": "round", "stroke-linejoin": "round", "aria-hidden": "true" };
    Object.entries(attrs).forEach(([key, value]) => svg.setAttribute(key, value));
    path.setAttribute("d", PATHS[name]);
    svg.appendChild(path);
    svg.style.flexShrink = "0";
    return svg;
}
