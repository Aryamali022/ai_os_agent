// Browser Agent setup page logic.
// Setup state is remembered locally (localStorage) for now; real auth comes later.

const API_BASE = "http://127.0.0.1:5000";
const SETUP_KEY = "browserAgentSetup";

const readyState = document.getElementById("readyState");
const setupState = document.getElementById("setupState");

const downloadBtn = document.getElementById("downloadBtn");
const doneBtn = document.getElementById("doneBtn");
const reinstallBtn = document.getElementById("reinstallBtn");
const useAgentBtn = document.getElementById("useAgentBtn");

function show(section) {
    readyState.classList.add("hidden");
    setupState.classList.add("hidden");
    section.classList.remove("hidden");
}

// Decide which view to show based on the saved setup flag.
function init() {
    if (localStorage.getItem(SETUP_KEY) === "true") {
        show(readyState);
    } else {
        show(setupState);
    }
}

// Download the extension zip.
async function downloadExtension() {
    downloadBtn.textContent = "Preparing download…";
    try {
        const res = await fetch(`${API_BASE}/download/browser-agent`);
        if (!res.ok) throw new Error("Download failed. Is the app running?");
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "dist.zip";
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    } catch (err) {
        alert(err.message);
    } finally {
        downloadBtn.textContent = "⬇ Download Extension (dist.zip)";
    }
}

// Mark setup complete (locally for now).
function finishSetup() {
    localStorage.setItem(SETUP_KEY, "true");
    show(readyState);
}

downloadBtn.addEventListener("click", (e) => {
    e.preventDefault();
    downloadExtension();
});
doneBtn.addEventListener("click", finishSetup);
reinstallBtn.addEventListener("click", () => show(setupState));
useAgentBtn.addEventListener("click", () => {
    alert(
        "Click the Browser Agent icon in your browser toolbar to open the side panel, " +
        "wait for it to show 'Connected', then type a task.\n\n" +
        "Note: after you send a task, the agent can take 5–10 minutes to start working."
    );
});

init();
