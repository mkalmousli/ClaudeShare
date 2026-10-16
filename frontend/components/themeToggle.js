// Dark/light switch. The icon follows the single `theme` value in state.js.
import { button } from "../widgets.js";
import { icon } from "../icons.js";
import { getTheme, onChange, setTheme } from "../state.js";

export function themeToggle(scope) {
    const node = button({ icon: icon("sun"), title: "Toggle dark / light mode", scope,
        onClick: () => setTheme(getTheme() === "dark" ? "light" : "dark") });
    const sync = () => {
        node.replaceChild(icon(getTheme() === "dark" ? "sun" : "moon"), node.firstChild);
        node.setAttribute("aria-pressed", String(getTheme() === "dark"));
    };
    sync();
    onChange((key) => key === "theme" && sync());
    return node;
}
