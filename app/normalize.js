(function () {
    function autoClassify(text) {
        const t = (text || "").toLowerCase();
        const solutionKeywords = ["step", "result", "deploy", "api", "code"];

        const isSolution = solutionKeywords.some(keyword => t.includes(keyword));

        let domain = "Technical";
        if (/market|roi|sales/.test(t)) domain = "Business";
        else if (/process|workflow|policy/.test(t)) domain = "Process";
        else if (/research|benchmark/.test(t)) domain = "Research";

        let completeness = 0;
        if (t.includes("problem")) completeness += 20;
        if (t.includes("step")) completeness += 30;
        if (t.includes("result")) completeness += 30;
        if (t.length > 200) completeness += 20;
        else completeness += 5;

        return {
            nature: isSolution ? "Solution" : "Blueprint",
            domain: domain,
            status: isSolution ? "Reviewed" : "Draft",
            completeness: Math.min(100, completeness)
        };
    }

    function normalizeImportedItems(rawItems) {
        const errors = [];
        const warnings = [];
        const normalized = [];

        rawItems.forEach((item, index) => {
            if (!item || typeof item !== "object") {
                errors.push(`Item ${index + 1} is not an object.`);
                return;
            }

            const normalizedItem = {};
            const title = typeof item.title === "string" ? item.title.trim() : "";
            const content = typeof item.content === "string" ? item.content : "";

            if (!title) {
                errors.push(`Item ${index + 1} is missing title.`);
            }
            if (!content) {
                warnings.push(`Item ${index + 1} is missing content.`);
            }

            normalizedItem.id = item.id || Math.random().toString(36).slice(2);
            normalizedItem.title = title || "Untitled";
            normalizedItem.author = item.author || "Unknown";
            normalizedItem.content = content || "";

            const auto = autoClassify(normalizedItem.content);
            normalizedItem.nature = item.nature || auto.nature;
            normalizedItem.domain = item.domain || auto.domain;
            normalizedItem.status = item.status || auto.status;
            normalizedItem.completeness = item.completeness || auto.completeness;

            if (Array.isArray(item.tags)) {
                normalizedItem.tags = item.tags.map(tag => String(tag).trim()).filter(Boolean);
            } else if (typeof item.tags === "string") {
                normalizedItem.tags = item.tags.split(",").map(tag => tag.trim()).filter(Boolean);
            } else {
                normalizedItem.tags = [];
            }

            normalizedItem.createdAt = item.createdAt || new Date().toISOString();
            normalized.push(normalizedItem);
        });

        return { normalized, errors, warnings };
    }

    const api = { autoClassify, normalizeImportedItems };

    if (typeof window !== "undefined") {
        window.NamoUtils = api;
    }
    if (typeof module !== "undefined" && module.exports) {
        module.exports = api;
    }
})();
