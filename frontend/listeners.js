// Tracked event listeners: everything added through a scope is removed on dispose().
import { release } from "./styles.js";

export function createScope(root = null) {
    const entries = [];
    const cleanups = [];
    return {
        cleanup(fn) { cleanups.push(fn); },
        on(target, type, handler, options) {
            target.addEventListener(type, handler, options);
            entries.push([target, type, handler, options]);
            return () => target.removeEventListener(type, handler, options);
        },
        dispose() {
            entries.forEach(([target, type, handler, options]) => target.removeEventListener(type, handler, options));
            entries.length = 0;
            cleanups.splice(0).forEach((fn) => fn());
            if (root) release(root);
        },
    };
}

export const appScope = createScope(); // for elements that live as long as the page
