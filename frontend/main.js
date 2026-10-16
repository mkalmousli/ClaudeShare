"use strict";
// Entry point: load the vendored terminal library, then hand over to the app modules.
const VENDOR_SCRIPTS = ["/vendor/xterm.js", "/vendor/addon-fit.js"];

function loadScript(src) {
    return new Promise((resolve, reject) => {
        const tag = document.createElement("script");
        tag.src = src;
        tag.onload = resolve;
        tag.onerror = () => reject(new Error("Could not load " + src));
        document.head.appendChild(tag);
    });
}

async function start() {
    for (const src of VENDOR_SCRIPTS) await loadScript(src);
    const app = await import("./app.js");
    app.mount();
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
else start();
