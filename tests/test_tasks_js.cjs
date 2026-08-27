const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const context = {
    document: {},
    $: () => ({ ready: () => {} })
};
vm.createContext(context);
vm.runInContext(fs.readFileSync("flaskr/static/js/tasks.js", "utf8"), context);

const options = context.buildOwnerOptions([
    { name: "Kim", email: "kim@example.com" },
    { name: "<Lee>", email: "lee@example.com" }
], "Kim");

assert.match(options, /value="Kim" selected/);
assert.match(options, /&lt;Lee&gt;/);
assert.match(context.buildOwnerOptions([], "Legacy"), /value="Legacy" selected/);
