const assert = require("assert");
const { autoClassify, normalizeImportedItems } = require("../app/normalize.js");

const auto = autoClassify("step result api");
assert.strictEqual(auto.nature, "Solution");

const input = [
    { title: "One", content: "Some content", tags: "a, b" },
    { title: "", content: "" }
];
const result = normalizeImportedItems(input);
assert.strictEqual(result.errors.length, 1);
assert.strictEqual(result.normalized.length, 2);
assert.strictEqual(result.normalized[0].tags.length, 2);

console.log("normalize test passed");
