// Number, size and time formatting.
const SIZE_UNITS = ["B", "KB", "MB", "GB", "TB"];
const MINUTE = 60;
const HOUR = 3600;
const DAY = 86400;

export function formatBytes(bytes) {
    let value = bytes;
    let unit = 0;
    while (value >= 1024 && unit < SIZE_UNITS.length - 1) { value /= 1024; unit += 1; }
    return `${unit === 0 ? value : value.toFixed(1)} ${SIZE_UNITS[unit]}`;
}

export function formatTokens(count) {
    if (count >= 1e9) return (count / 1e9).toFixed(1) + "B";
    if (count >= 1e6) return (count / 1e6).toFixed(1) + "M";
    if (count >= 1e3) return (count / 1e3).toFixed(0) + "k";
    return String(Math.round(count));
}

export function formatCountdown(epochSeconds) {
    const left = Math.max(0, epochSeconds - Date.now() / 1000);
    if (left >= DAY) return `${Math.floor(left / DAY)}d ${Math.floor((left % DAY) / HOUR)}h`;
    if (left >= HOUR) return `${Math.floor(left / HOUR)}h ${Math.floor((left % HOUR) / MINUTE)}m`;
    return `${Math.max(1, Math.floor(left / MINUTE))}m`;
}

export function formatDate(epochSeconds) {
    return new Date(epochSeconds * 1000).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

export const percent = (value) => `${Math.round(value)}%`;
export const baseName = (path) => path.split("/").filter(Boolean).pop() || "/";
export const joinPath = (dir, name) => (dir === "/" ? "" : dir) + "/" + name;
export const parentPath = (path) => "/" + path.split("/").filter(Boolean).slice(0, -1).join("/");
