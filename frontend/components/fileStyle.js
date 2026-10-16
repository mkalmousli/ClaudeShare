// Row painting for the file list (kept apart so fileList.js stays focused on behaviour).
import { palette } from "../styles.js";

export const styled = {
    row(node, selected, hovered, dropping) {
        const pal = palette();
        Object.assign(node.style, {
            background: selected ? pal.select : hovered ? pal.hover : "transparent",
            boxShadow: dropping ? `inset 0 0 0 2px ${pal.accent}` : "none",
            color: pal.text,
        });
    },
};
