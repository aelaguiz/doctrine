const path = require("node:path");

const { runTests } = require("@vscode/test-electron");

async function main() {
  const extensionDevelopmentPath = path.resolve(__dirname, "../..");
  const extensionTestsPath = path.resolve(__dirname, "./suite/index.js");
  const repoRoot = path.resolve(extensionDevelopmentPath, "../..");

  await runTests({
    extensionDevelopmentPath,
    extensionTestsPath,
    launchArgs: [repoRoot, "--disable-extensions"],
  });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
