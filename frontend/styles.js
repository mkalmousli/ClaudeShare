// Theme application: every themed element registers a paint function here, and
// applyTheme() is the only place that re-applies colours when the theme changes.
import { PALETTES } from "./theme.js";
import { getTheme, onChange } from "./state.js";

const registry = new Map();

export const palette = () => PALETTES[getTheme()];

export function themed(node, paint) {
    registry.set(node, paint);
    paint(palette());
    return node;
}

export function release(root) {
    registry.forEach((_paint, node) => {
        if (root === node || root.contains(node)) registry.delete(node);
    });
}

export function applyTheme() {
    const pal = palette();
    registry.forEach((paint) => paint(pal));
    document.documentElement.style.colorScheme = getTheme();
}

onChange((key) => key === "theme" && applyTheme());
