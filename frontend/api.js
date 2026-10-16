// Every GraphQL document lives here, grouped by resource.
import { GQL_URL } from "./consts.js";
import { subscribe } from "./ws.js";

export class ApiError extends Error {}
const unauthHandlers = new Set();
export const onUnauth = (fn) => unauthHandlers.add(fn);

async function run(query, variables = {}) {
    const reply = await fetch(GQL_URL, {
        method: "POST", credentials: "same-origin",
        headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query, variables }),
    });
    const body = await reply.json();
    if (body.errors && !body.data) {
        if (body.errors[0].message === "Not signed in") unauthHandlers.forEach((fn) => fn());
        throw new ApiError(body.errors[0].message);
    }
    if (body.errors) throw new ApiError(body.errors[0].message);
    return body.data;
}

const USAGE_FIELDS = `used budget percent period resetsAt blocked
    plan { fiveHour fiveHourResets sevenDay sevenDayResets }
    sessions { id project started last messages tokens live }`;

export const auth = {
    me: () => run("query { me { username } }").then((d) => d.me),
    login: (username, key) => run("mutation($u:String!,$k:String!){ login(username:$u,key:$k){ username } }", { u: username, k: key }).then((d) => d.login),
    logout: () => run("mutation { logout }"),
};

export const terminals = {
    list: () => run("query { terminals { id title } }").then((d) => d.terminals),
    create: (cwd, run_, cols, rows) => run("mutation($c:String,$r:String,$n:Int!,$w:Int!){ createTerminal(cwd:$c,run:$r,cols:$n,rows:$w){ id title } }", { c: cwd, r: run_, n: cols, w: rows }).then((d) => d.createTerminal),
    close: (id) => run("mutation($i:String!){ closeTerminal(id:$i) }", { i: id }),
    input: (id, data) => run("mutation($i:String!,$d:String!){ terminalInput(id:$i,data:$d) }", { i: id, d: data }),
    resize: (id, cols, rows) => run("mutation($i:String!,$c:Int!,$r:Int!){ terminalResize(id:$i,cols:$c,rows:$r) }", { i: id, c: cols, r: rows }),
    output: (id, handlers) => subscribe({ query: "subscription($i:String!){ terminalOutput(id:$i){ kind data } }", variables: { i: id } }, handlers),
};

const ENTRY = "name isDir size mtime mode isLink";
export const files = {
    list: (path) => run(`query($p:String!){ files(path:$p){ path entries { ${ENTRY} } } }`, { p: path }).then((d) => d.files),
    read: (path) => run("query($p:String!){ readFile(path:$p){ binary size content } }", { p: path }).then((d) => d.readFile),
    makeDir: (path) => run("mutation($p:String!){ makeDir(path:$p) }", { p: path }),
    makeFile: (path) => run("mutation($p:String!){ makeFile(path:$p) }", { p: path }),
    write: (path, content) => run("mutation($p:String!,$c:String!){ writeFile(path:$p,content:$c) }", { p: path, c: content }),
    rename: (path, to) => run("mutation($p:String!,$t:String!){ renameEntry(path:$p,to:$t){ path } }", { p: path, t: to }),
    move: (paths, dest) => run("mutation($p:[String!]!,$d:String!){ moveEntries(paths:$p,dest:$d) }", { p: paths, d: dest }),
    copy: (paths, dest) => run("mutation($p:[String!]!,$d:String!){ copyEntries(paths:$p,dest:$d) }", { p: paths, d: dest }),
    remove: (paths) => run("mutation($p:[String!]!){ deleteEntries(paths:$p) }", { p: paths }),
    chmod: (path, mode) => run("mutation($p:String!,$m:String!){ chmodEntry(path:$p,mode:$m) }", { p: path, m: mode }),
    compress: (paths, dest, name) => run("mutation($p:[String!]!,$d:String!,$n:String!){ compress(paths:$p,dest:$d,name:$n){ path } }", { p: paths, d: dest, n: name }),
    extract: (path) => run("mutation($p:String!){ extract(path:$p){ path } }", { p: path }),
};

export const usage = {
    get: () => run(`query { usage { ${USAGE_FIELDS} } }`).then((d) => d.usage),
    watch: (handlers) => subscribe({ query: `subscription { usageUpdates { ${USAGE_FIELDS} } }` }, handlers),
};
