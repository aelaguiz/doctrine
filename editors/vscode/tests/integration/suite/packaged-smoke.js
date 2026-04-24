const assert = require("node:assert/strict");

const vscode = require("vscode");

async function run() {
  const extension = vscode.extensions.getExtension("aelaguiz.doctrine-language");
  assert.ok(extension, "Packaged Doctrine extension should be installed.");

  // The source-tree integration suite already proves the full clickable surface.
  // Packaged smoke only needs to prove the installed VSIX activates and exposes
  // the Doctrine language that users will see after installing the package.
  await extension.activate();

  const languages = await vscode.languages.getLanguages();
  assert.ok(languages.includes("doctrine"), "Packaged extension should register Doctrine.");

  const document = await vscode.workspace.openTextDocument({
    content: 'agent Hello:\n    role: "Say hello."\n',
    language: "doctrine",
  });
  assert.equal(document.languageId, "doctrine");
}

module.exports = {
  run,
};
