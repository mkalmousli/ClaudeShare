// The apps a user can open, shared by the desktop icons, taskbar and shortcuts.
import { openFileManager } from "./fileManager.js";
import { openTerminal } from "./terminal.js";
import { openUsageWindow } from "./usageWindow.js";

export const APPS = [
    { id: "files", label: "Files", icon: "folder", key: "f", open: () => openFileManager("/") },
    { id: "terminal", label: "Terminal", icon: "terminal", key: "t", open: () => openTerminal() },
    { id: "claude", label: "Claude", icon: "spark", key: "c", open: () => openTerminal({ run: "claude" }) },
    { id: "usage", label: "Usage", icon: "chart", key: "u", open: () => openUsageWindow() },
];
