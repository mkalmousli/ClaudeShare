// One shared usage subscription for the whole UI (meter, usage window).
import { usage } from "./api.js";

const listeners = new Set();
let latest = null;
let stop = null;

export const currentUsage = () => latest;

export function onUsage(fn) {
    listeners.add(fn);
    latest && fn(latest);
    return () => listeners.delete(fn);
}

export function startUsage() {
    stopUsage();
    usage.get().then((value) => publish(value)).catch(() => {});
    stop = usage.watch({ next: (data) => data && publish(data.usageUpdates) });
}

export function stopUsage() {
    stop && stop();
    stop = null;
    latest = null;
}

function publish(value) {
    latest = value;
    listeners.forEach((fn) => fn(value));
}
