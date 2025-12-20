// --- Globals & Initialization ---

const STORAGE_KEY = "namo.hub.v1";
let items = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");

// --- DOM Utility Functions ---

const qs = (selector, element = document) => element.querySelector(selector);
const qsa = (selector, element = document) => [...element.querySelectorAll(selector)];

function setStatus(message, level) {
    const statusEl = qs("#status");
    if (!statusEl) return;
    statusEl.textContent = message || "";
    statusEl.className = level || "";
}

const utils = window.NamoUtils || {};
const autoClassify = utils.autoClassify;
const normalizeImportedItems = utils.normalizeImportedItems;
const hasUtils = typeof autoClassify === "function" && typeof normalizeImportedItems === "function";

// --- Core Data Functions ---

/**
 * Saves the current 'items' array to localStorage.
 */
function saveItems() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

/**
 * Generates a simple unique ID.
 * @returns {string} A random alphanumeric string.
 */
function generateUID() {
    return Math.random().toString(36).slice(2);
}

// --- Rendering Functions ---

/**
 * Main render function that orchestrates rendering based on the current view mode.
 */
function render() {
    const viewContainer = qs("#view");
    const filterNature = qs("#f-nature").value;
    const filterDomain = qs("#f-domain").value;
    const filterStatus = qs("#f-status").value;
    const filterText = qs("#f-text").value.toLowerCase();

    const filteredItems = items.filter(item =>
        (filterNature === "All" || item.nature === filterNature) &&
        (filterDomain === "All" || item.domain === filterDomain) &&
        (filterStatus === "All" || item.status === filterStatus) &&
        (!filterText || (item.title + item.content).toLowerCase().includes(filterText))
    );

    const viewMode = document.body.dataset.view || "matrix";
    viewContainer.innerHTML = ""; // Clear previous view

    if (viewMode === "matrix") {
        renderMatrixView(viewContainer, filteredItems);
    } else if (viewMode === "kanban") {
        renderKanbanView(viewContainer, filteredItems);
    } else {
        renderMindmapView(viewContainer, filteredItems);
    }
}

/**
 * Renders the Matrix view.
 * @param {HTMLElement} root - The container element.
 * @param {Array} list - The list of items to render.
 */
function renderMatrixView(root, list) {
    const domains = ["Technical", "Business", "Process", "Research"];
    const matrixContainer = document.createElement("div");
    matrixContainer.className = "matrix";

    matrixContainer.innerHTML = `
        <div></div>
        ${domains.map(d => `<div class='head'>${d}</div>`).join("")}
        <div class='head'>Blueprint</div>
        ${domains.map(d => `<div class='cell' data-nature='Blueprint' data-domain='${d}'></div>`).join("")}
        <div class='head'>Solution</div>
        ${domains.map(d => `<div class='cell' data-nature='Solution' data-domain='${d}'></div>`).join("")}
    `;

    list.forEach(item => {
        const cell = qs(`.cell[data-nature='${item.nature}'][data-domain='${item.domain}']`, matrixContainer);
        if (!cell) return;
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `<h5>${item.title}</h5><div class='meta'>${item.status} • ${item.completeness || 0}%</div>`;
        cell.appendChild(card);
    });
    root.appendChild(matrixContainer);
}

/**
 * Renders the Kanban board view.
 * @param {HTMLElement} root - The container element.
 * @param {Array} list - The list of items to render.
 */
function renderKanbanView(root, list) {
    const kanbanContainer = document.createElement('div');
    kanbanContainer.className = 'kanban';
    kanbanContainer.innerHTML = ["Draft", "Reviewed", "Final"].map(s => `<div class='col' data-status='${s}'><h4>${s}</h4><div class='drop'></div></div>`).join("");

    const lanes = { "Draft": [], "Reviewed": [], "Final": [] };
    list.forEach(item => lanes[item.status]?.push(item));

    kanbanContainer.querySelectorAll(".col").forEach(col => {
        const status = col.dataset.status;
        const dropZone = qs(".drop", col);

        lanes[status].forEach(item => {
            const cardElement = document.createElement("div");
            cardElement.className = "card draggable";
            cardElement.draggable = true;
            cardElement.dataset.id = item.id;
            cardElement.innerHTML = `<h5>${item.title}</h5><div class='meta'>${item.nature} • ${item.domain}</div>`;
            dropZone.appendChild(cardElement);
        });

        dropZone.ondragover = e => e.preventDefault();
        dropZone.ondrop = e => {
            e.preventDefault();
            const itemId = e.dataTransfer.getData("text/plain");
            const droppedItem = items.find(x => x.id === itemId);
            if (droppedItem) {
                droppedItem.status = status;
                saveItems();
                render();
            }
        };
    });

    kanbanContainer.querySelectorAll(".draggable").forEach(draggable => {
        draggable.ondragstart = e => e.dataTransfer.setData("text/plain", draggable.dataset.id);
    });
    root.appendChild(kanbanContainer);
}

/**
 * Renders the Mindmap view.
 * @param {HTMLElement} root - The container element.
 * @param {Array} list - The list of items to render.
 */
function renderMindmapView(root, list) {
    const groupedByNature = {};
    list.forEach(item => {
        (groupedByNature[item.nature] = groupedByNature[item.nature] || []).push(item);
    });

    const mindmapContainer = document.createElement("div");
    mindmapContainer.className = "mindmap";

    Object.entries(groupedByNature).forEach(([nature, itemsInNature]) => {
        const branch = document.createElement("div");
        branch.className = "branch";
        branch.innerHTML = `<h3>${nature}</h3><div class='sep'></div>`;

        const groupedByDomain = {};
        itemsInNature.forEach(item => {
            (groupedByDomain[item.domain] = groupedByDomain[item.domain] || []).push(item);
        });

        Object.entries(groupedByDomain).forEach(([domain, itemsInDomain]) => {
            const section = document.createElement("div");
            section.innerHTML = `<h4>${domain}</h4>`;
            itemsInDomain.forEach(item => {
                const line = document.createElement("div");
                line.className = "card";
                line.innerHTML = `<h5>${item.title}</h5><div class='meta'>${item.status} • ${item.completeness || 0}%</div>`;
                section.appendChild(line);
            });
            branch.appendChild(section);
        });
        mindmapContainer.appendChild(branch);
    });
    root.appendChild(mindmapContainer);
}

// --- Event Listeners Setup ---

function setupEventListeners() {
    // View mode switching
    qs("#view-matrix").onclick = () => { document.body.dataset.view = "matrix"; render(); };
    qs("#view-kanban").onclick = () => { document.body.dataset.view = "kanban"; render(); };
    qs("#view-mindmap").onclick = () => { document.body.dataset.view = "mindmap"; render(); };

    // Form submission for new items
    qs("#item-form").onsubmit = e => {
        e.preventDefault();
        const newItem = {
            id: generateUID(),
            title: qs("#title").value,
            author: qs("#author").value,
            content: qs("#content").value,
            nature: qs("#nature").value,
            domain: qs("#domain").value,
            status: qs("#status").value,
            tags: qs("#tags").value.split(",").filter(Boolean).map(tag => tag.trim()),
            createdAt: new Date().toISOString()
        };
        if (hasUtils) {
            const auto = autoClassify(newItem.content);
            newItem.completeness = auto.completeness;
        } else {
            newItem.completeness = 0;
        }

        items.push(newItem);
        saveItems();
        e.target.reset();
        render();
        setStatus("Item added.", "ok");
    };

    // Auto-classify button
    qs("#auto").onclick = () => {
        if (!hasUtils) {
            setStatus("Auto-classify unavailable. Reload the page.", "error");
            return;
        }
        const result = autoClassify(qs("#content").value);
        qs("#nature").value = result.nature;
        qs("#domain").value = result.domain;
        qs("#status").value = result.status;
    };

    // Export to JSON
    qs("#btn-export").onclick = () => {
        if (items.length === 0) {
            setStatus("Export aborted: no data to export.", "warn");
            return;
        }
        const dataStr = JSON.stringify(items, null, 2);
        const dataBlob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "namo-hub-items.json";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        setStatus(`Export complete: ${items.length} items`, "ok");
    };

    // Import from JSON
    qs("#file-import").onchange = e => {
        const file = e.target.files[0];
        if (!file) return;
        if (!hasUtils) {
            setStatus("Import utilities missing. Reload the page.", "error");
            e.target.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = () => {
            try {
                const importedItems = JSON.parse(reader.result);
                if (!Array.isArray(importedItems)) {
                    setStatus("Import failed: expected an array of items.", "error");
                    return;
                }

                const result = normalizeImportedItems(importedItems);
                if (result.errors.length) {
                    setStatus(`Import failed: ${result.errors[0]}`, "error");
                    return;
                }

                items = result.normalized;
                saveItems();
                render();
                const warnText = result.warnings.length ? ` (${result.warnings.length} warnings)` : "";
                setStatus(`Import complete: ${items.length} items${warnText}`, result.warnings.length ? "warn" : "ok");
            } catch (error) {
                setStatus("Import failed: invalid JSON.", "error");
                console.error("JSON Parse Error:", error);
            } finally {
                // Reset file input to allow re-uploading the same file
                e.target.value = '';
            }
        };
        reader.readAsText(file);
    };

    // Clear all items
    qs("#btn-clear").onclick = () => {
        if (confirm("Are you sure you want to clear all items? This action cannot be undone.")) {
            items = [];
            saveItems();
            render();
            setStatus("All items cleared.", "warn");
        }
    };

    // Filter listeners to re-render on any change
    qsa("#f-nature, #f-domain, #f-status").forEach(el => {
        el.onchange = render;
    });
    qs("#f-text").oninput = render;
}


// --- Initial Load ---

document.addEventListener("DOMContentLoaded", () => {
    setupEventListeners();
    render(); // Initial render of the application state
    if (!hasUtils) {
        setStatus("Import utilities missing. Reload the page.", "error");
    } else {
        setStatus("Ready", "ok");
    }
});
