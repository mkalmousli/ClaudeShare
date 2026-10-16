// Terminal window: xterm.js on the front, a server-side persistent PTY behind it.
import { terminals } from "../api.js";
import { FONT, FONT_SIZE_TERM } from "../consts.js";
import { add, colored, el } from "../dom.js";
import { createScope } from "../listeners.js";
import { getTheme, onChange } from "../state.js";
import { TERM_THEME } from "../theme.js";
import { confirmBox } from "./dialog.js";
import { createInputQueue } from "./termInput.js";
import { createKeyBar, isTouch } from "./termKeys.js";
import { toast } from "./toast.js";
import { openWindow } from "./window.js";
import { paintViewport, watchXtermStyles } from "./xtermStyle.js";

function makeTerm(holder) {
    const term = new window.Terminal({ fontFamily: FONT.mono, fontSize: FONT_SIZE_TERM, cursorBlink: true, scrollback: 5000,
        theme: TERM_THEME[getTheme()], allowProposedApi: true });
    const fit = new window.FitAddon.FitAddon();
    term.loadAddon(fit);
    term.open(holder);
    return { term, fit };
}

function handleOutput(term, win, finish) {
    return (data) => {
        const event = data.terminalOutput;
        if (event.kind === "replay") { term.reset(); term.write(event.data); }
        if (event.kind === "data") term.write(event.data);
        if (event.kind === "exit") { finish(); win.close(); }
    };
}

export async function openTerminal({ cwd = null, run = null, existing = null } = {}) {
    const scope = createScope();
    let exited = false;
    let confirmed = false;
    const win = openWindow({ title: existing ? existing.title : "Terminal", iconName: "terminal", onClose: (w) => {
        if (exited || confirmed) return true;
        confirmBox({ title: "Close terminal?", message: "Anything running in it will be stopped.", okText: "Close", danger: true })
            .then((ok) => { if (ok) { confirmed = true; w.close(); } });
        return false;
    } });
    const holder = el("div", { flex: "1", position: "relative", overflow: "hidden", padding: "6px 0px 0px 8px" });
    add(win.body, holder);
    const { term, fit } = makeTerm(holder);
    const stopStyles = watchXtermStyles(holder);
    colored(holder, (pal) => { paintViewport(holder, pal.term); return { background: pal.term }; });
    let info;
    try { info = existing || await terminals.create(cwd, run, term.cols, term.rows); } catch (err) { toast(err.message, true); exited = true; win.close(); return null; }
    const send = createInputQueue(info.id);
    const keys = isTouch() ? createKeyBar(send, scope) : null;
    keys && add(win.body, keys.bar);
    term.onData((data) => send(keys ? keys.withCtrl(data) : data));
    term.onResize(({ cols, rows }) => terminals.resize(info.id, cols, rows).catch(() => {}));
    term.onTitleChange((title) => win.setTitle(title));
    const stop = terminals.output(info.id, { next: handleOutput(term, win, () => { exited = true; }) });
    win.onResize = () => requestAnimationFrame(() => { try { fit.fit(); } catch (err) { /* hidden */ } });
    const offTheme = onChange((key) => key === "theme" && (term.options.theme = TERM_THEME[getTheme()]));
    const originalClose = win.close;
    win.close = () => {
        const wasOpen = win.el.isConnected;
        originalClose();
        if (wasOpen && !win.el.isConnected) {
            stop(); offTheme(); stopStyles(); scope.dispose(); term.dispose();
            exited || terminals.close(info.id).catch(() => {});
        }
    };
    win.onResize();
    term.focus();
    return win;
}

export async function restoreTerminals() {
    const list = await terminals.list();
    for (const existing of list) await openTerminal({ existing });
    return list.length;
}
