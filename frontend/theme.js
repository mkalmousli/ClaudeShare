// Theme colours live here and nowhere else: blacks/whites plus exactly one accent.
export const ACCENT = "#d97757";

export const PALETTES = {
    dark: {
        bg: "#0a0a0b", surface: "#121214", raised: "#1a1a1d", border: "#2a2a2f",
        text: "#ededef", muted: "#8e8e96", hover: "rgba(255,255,255,0.07)", press: "rgba(255,255,255,0.12)",
        select: "rgba(217,119,87,0.22)", shadow: "0 12px 40px rgba(0,0,0,0.55)",
        accent: ACCENT, onAccent: "#140a06", term: "#0a0a0b", termText: "#e6e6e8", scrim: "rgba(0,0,0,0.55)",
    },
    light: {
        bg: "#f1f1f3", surface: "#fbfbfc", raised: "#ffffff", border: "#dcdce1",
        text: "#18181b", muted: "#6b6b74", hover: "rgba(0,0,0,0.06)", press: "rgba(0,0,0,0.11)",
        select: "rgba(217,119,87,0.20)", shadow: "0 12px 36px rgba(0,0,0,0.18)",
        accent: ACCENT, onAccent: "#ffffff", term: "#fbfbfc", termText: "#1c1c20", scrim: "rgba(0,0,0,0.30)",
    },
};

export const TERM_THEME = {
    dark: { background: PALETTES.dark.term, foreground: PALETTES.dark.termText, cursor: ACCENT, selectionBackground: "#5a3a2d" },
    light: { background: PALETTES.light.term, foreground: PALETTES.light.termText, cursor: ACCENT, selectionBackground: "#f0c9b8" },
};
