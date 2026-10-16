// Sign-in screen.
import { auth } from "../api.js";
import { FONT, RADIUS, SPACE } from "../consts.js";
import { add, colored, column, el } from "../dom.js";
import { button, textField } from "../widgets.js";
import { icon } from "../icons.js";
import { createScope } from "../listeners.js";
import { themeToggle } from "./themeToggle.js";

export function showLogin(host, onSuccess) {
    const scope = createScope(host);
    const page = el("div", { position: "fixed", top: "0px", left: "0px", display: "flex", alignItems: "center", justifyContent: "center", font: `${FONT.size.lg}px ${FONT.ui}` });
    colored(page, (pal) => ({ background: pal.bg, color: pal.text }));
    const card = el("form", { ...column, gap: SPACE.md + "px", padding: SPACE.xl + "px", borderRadius: RADIUS.md + "px" });
    colored(card, (pal) => ({ background: pal.surface, border: `1px solid ${pal.border}`, boxShadow: pal.shadow }));
    const user = textField({ placeholder: "Username", scope });
    const key = textField({ placeholder: "Access key", type: "password", scope });
    user.autocomplete = "username";
    key.autocomplete = "current-password";
    const problem = el("div", { height: "18px", fontSize: FONT.size.md + "px", fontWeight: "600" }, { role: "alert" });
    colored(problem, (pal) => ({ color: pal.accent }));
    const submit = button({ text: "Sign in", icon: icon("lock", 16), kind: "primary", scope });
    submit.type = "submit";
    submit.style.height = "40px";
    const title = el("div", { fontSize: FONT.size.xl + "px", fontWeight: "700" }, { textContent: "ClaudeShare" });
    const subtitle = el("div", { fontSize: FONT.size.md + "px", marginBottom: SPACE.sm + "px" }, { textContent: "Sign in with the username and key you were given." });
    colored(subtitle, (pal) => ({ color: pal.muted }));
    scope.on(card, "submit", async (ev) => {
        ev.preventDefault();
        problem.textContent = "";
        try {
            const me = await auth.login(user.value, key.value);
            scope.dispose();
            page.remove();
            onSuccess(me.username);
        } catch (err) { problem.textContent = err.message; }
    });
    const place = () => {
        page.style.width = window.innerWidth + "px";
        page.style.height = window.innerHeight + "px";
        card.style.width = Math.min(360, window.innerWidth - 32) + "px";
    };
    place();
    scope.on(window, "resize", place);
    const corner = add(el("div", { position: "absolute", top: SPACE.md + "px", right: SPACE.md + "px" }), themeToggle(scope));
    add(card, title, subtitle, user, key, problem, submit);
    add(page, card, corner);
    host.appendChild(page);
    user.focus();
}
