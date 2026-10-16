// Modal dialogs: text prompt and confirmation. Both resolve a Promise.
import { FONT, LAYER, RADIUS, SPACE } from "../consts.js";
import { add, colored, column, el, row } from "../dom.js";
import { button, textField } from "../widgets.js";
import { createScope } from "../listeners.js";

function modal(title, buildBody, finish) {
    const scope = createScope();
    const scrim = el("div", { position: "fixed", top: "0px", left: "0px", right: "0px", bottom: "0px", zIndex: String(LAYER.dialog),
        display: "flex", alignItems: "center", justifyContent: "center" });
    colored(scrim, (pal) => ({ background: pal.scrim }));
    const card = el("div", { ...column, gap: SPACE.md + "px", padding: SPACE.xl + "px", borderRadius: RADIUS.md + "px", font: `${FONT.size.md}px ${FONT.ui}` });
    colored(card, (pal) => ({ background: pal.raised, color: pal.text, border: `1px solid ${pal.border}`, boxShadow: pal.shadow }));
    card.setAttribute("role", "dialog");
    card.setAttribute("aria-label", title);
    const size = () => { card.style.width = Math.min(380, window.innerWidth - 32) + "px"; };
    size();
    scope.on(window, "resize", size);
    const close = (value) => { scope.dispose(); scrim.remove(); finish(value); };
    add(card, el("div", { fontSize: FONT.size.lg + "px", fontWeight: "600" }, { textContent: title }), ...buildBody(scope, close));
    scope.on(scrim, "keydown", (ev) => ev.key === "Escape" && close(null));
    add(scrim, card);
    document.body.appendChild(scrim);
    return close;
}

function footer(scope, close, okText, danger, getValue) {
    const ok = button({ text: okText, kind: "primary", scope, title: danger ? okText : "", onClick: () => close(getValue()) });
    const cancel = button({ text: "Cancel", scope, onClick: () => close(null) });
    return { bar: add(el("div", { ...row(), justifyContent: "flex-end" }), cancel, ok), ok };
}

export function askText({ title, label = "", value = "", okText = "OK" }) {
    return new Promise((resolve) => {
        let field = null;
        modal(title, (scope, close) => {
            field = textField({ value, placeholder: label, scope, onEnter: () => close(field.value.trim() || null) });
            const { bar } = footer(scope, close, okText, false, () => field.value.trim() || null);
            return [field, bar];
        }, resolve);
        field.focus();
        field.select();
    });
}

export function confirmBox({ title, message, okText = "OK", danger = false }) {
    return new Promise((resolve) => {
        let okButton = null;
        modal(title, (scope, close) => {
            const { bar, ok } = footer(scope, close, okText, danger, () => true);
            okButton = ok;
            return [el("div", { opacity: "0.85", lineHeight: "1.45" }, { textContent: message }), bar];
        }, (value) => resolve(value === true));
        okButton.focus();
    });
}
