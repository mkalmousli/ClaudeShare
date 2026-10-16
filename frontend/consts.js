// Named constants: sizes, breakpoints, layers, timings. No magic numbers elsewhere.
export const GQL_URL = "/graphql";
export const UPLOAD_URL = "/files/upload";
export const DOWNLOAD_URL = "/files/download";

export const SPACE = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24 };
export const RADIUS = { sm: 6, md: 10 };
export const FONT = {
    ui: "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
    mono: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
    size: { sm: 12, md: 13, lg: 15, xl: 20 },
};
export const SIZE = { taskbar: 46, titlebar: 34, control: 30, icon: 18, row: 30, sidebar: 0 };
export const WINDOW = { w: 760, h: 480, minW: 300, minH: 200, cascade: 28, edge: 6, snapZone: 14, originX: 110, originY: 24 };
export const PHONE_BREAKPOINT = 720;
export const LAYER = { windows: 10, taskbar: 100000, menu: 100001, dialog: 100002, toast: 100003 };
export const TIMING = { fast: "120ms", toast: 3200, clock: 15000, poll: 5000 };
export const METER = { width: 120, height: 6, warn: 90 };
export const FILE_LIMITS = { editorBytes: 2 * 1024 * 1024 };
export const FONT_SIZE_TERM = 14;
