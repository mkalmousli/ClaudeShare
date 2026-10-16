// Minimal graphql-transport-ws client: one socket, many subscriptions, auto-reconnect.
import { GQL_URL } from "./consts.js";

const RETRY_MS = 1500;
const subs = new Map();
let socket = null;
let ready = false;
let counter = 0;

const url = () => (location.protocol === "https:" ? "wss://" : "ws://") + location.host + GQL_URL;
const send = (msg) => socket && ready && socket.send(JSON.stringify(msg));
const start = (id) => send({ id, type: "subscribe", payload: subs.get(id).payload });

function onMessage(ev) {
    const msg = JSON.parse(ev.data);
    if (msg.type === "connection_ack") {
        ready = true;
        subs.forEach((_sub, id) => start(id));
        return;
    }
    const sub = subs.get(msg.id);
    if (!sub) return;
    if (msg.type === "next") sub.handlers.next(msg.payload.data, msg.payload.errors);
    if (msg.type === "error") sub.handlers.error && sub.handlers.error(msg.payload);
    if (msg.type === "complete") subs.delete(msg.id);
}

function connect() {
    socket = new WebSocket(url(), "graphql-transport-ws");
    socket.onopen = () => socket.send(JSON.stringify({ type: "connection_init" }));
    socket.onmessage = onMessage;
    socket.onclose = () => {
        ready = false;
        socket = null;
        if (subs.size) setTimeout(connect, RETRY_MS);
    };
}

export function subscribe(payload, handlers) {
    const id = String(++counter);
    subs.set(id, { payload, handlers });
    if (!socket) connect();
    else start(id);
    return () => {
        send({ id, type: "complete" });
        subs.delete(id);
    };
}
