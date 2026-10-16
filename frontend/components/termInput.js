// Ordered, batched keyboard input to the server (HTTP calls could otherwise reorder keystrokes).
import { terminals } from "../api.js";

export function createInputQueue(id) {
    let pending = "";
    let busy = false;
    const flush = async () => {
        if (busy || !pending) return;
        busy = true;
        const chunk = pending;
        pending = "";
        try { await terminals.input(id, chunk); } catch (err) { /* terminal is gone; exit event handles it */ }
        busy = false;
        flush();
    };
    return (data) => { pending += data; flush(); };
}
