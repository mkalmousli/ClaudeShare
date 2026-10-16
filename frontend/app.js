// Wires everything together: global look, session check, login <-> desktop.
import { auth, onUnauth } from "./api.js";
import { FONT } from "./consts.js";
import { showLogin } from "./components/login.js";
import { mountDesktop } from "./components/desktop.js";
import { colored, el } from "./dom.js";
import { setUser } from "./state.js";
import { applyTheme } from "./styles.js";

function prepareDocument() {
    document.title = "ClaudeShare";
    Object.assign(document.body.style, { margin: "0px", overflow: "hidden", font: `${FONT.size.md}px ${FONT.ui}` });
    colored(document.body, (pal) => ({ background: pal.bg, color: pal.text }));
    applyTheme();
}

async function enter(host, username) {
    setUser(username);
    onUnauth(() => window.location.reload());
    await mountDesktop(host);
}

export async function mount() {
    prepareDocument();
    const host = el("div", {});
    document.body.appendChild(host);
    try {
        const me = await auth.me();
        await enter(host, me.username);
    } catch (err) {
        showLogin(host, (username) => enter(host, username));
    }
}
