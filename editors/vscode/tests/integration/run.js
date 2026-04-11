const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const {
  downloadAndUnzipVSCode,
  runTests,
  TestRunFailedError,
} = require("@vscode/test-electron");
const CACHE_PATH_ENV = "DOCTRINE_VSCODE_TEST_CACHE";
const EXECUTABLE_PATH_ENV = "DOCTRINE_VSCODE_EXECUTABLE_PATH";
const MAX_STARTUP_ATTEMPTS = 4;
const EXTENSION_COPY_EXCLUDE_NAMES = new Set([".vscode-test", "node_modules"]);

function makeTempDir(prefix) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  process.on("exit", () => {
    fs.rmSync(dir, { recursive: true, force: true });
  });
  return dir;
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function stageExtension(sourceDir) {
  const stageRoot = makeTempDir("doctrine-vscode-extension-");
  const stagedExtensionDir = path.join(stageRoot, "extension");
  fs.cpSync(sourceDir, stagedExtensionDir, {
    recursive: true,
    filter: (sourcePath) => {
      const relativePath = path.relative(sourceDir, sourcePath);
      if (!relativePath) {
        return true;
      }
      const pathSegments = relativePath.split(path.sep);
      if (pathSegments.some((segment) => EXTENSION_COPY_EXCLUDE_NAMES.has(segment))) {
        return false;
      }
      return !sourcePath.endsWith(".vsix");
    },
  });
  return stagedExtensionDir;
}

function listCompletedInstallDirs(cachePath) {
  if (!fs.existsSync(cachePath)) {
    return [];
  }
  return fs
    .readdirSync(cachePath, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && entry.name.startsWith("vscode-"))
    .map((entry) => path.join(cachePath, entry.name))
    .filter((installDir) => fs.existsSync(path.join(installDir, "is-complete")));
}

function seedCacheFromLocalInstall(targetCachePath, sourceCachePaths) {
  if (listCompletedInstallDirs(targetCachePath).length > 0) {
    return;
  }

  for (const sourceCachePath of sourceCachePaths) {
    if (!sourceCachePath || path.resolve(sourceCachePath) === path.resolve(targetCachePath)) {
      continue;
    }

    const installDirs = listCompletedInstallDirs(sourceCachePath);
    if (installDirs.length === 0) {
      continue;
    }

    for (const installDir of installDirs) {
      const targetInstallDir = path.join(targetCachePath, path.basename(installDir));
      if (!fs.existsSync(targetInstallDir)) {
        fs.cpSync(installDir, targetInstallDir, { recursive: true });
      }
    }
    return;
  }
}

async function resolveVSCodeExecutablePath({ extensionDevelopmentPath, repoCachePath }) {
  const injectedExecutablePath = process.env[EXECUTABLE_PATH_ENV];
  if (injectedExecutablePath) {
    return path.resolve(injectedExecutablePath);
  }

  const configuredCachePath = process.env[CACHE_PATH_ENV]
    ? path.resolve(process.env[CACHE_PATH_ENV])
    : makeTempDir("doctrine-vscode-test-");
  const cachePath = ensureDir(configuredCachePath);
  seedCacheFromLocalInstall(cachePath, [repoCachePath]);

  return downloadAndUnzipVSCode({
    cachePath,
    extensionDevelopmentPath,
  });
}

function isRetriableStartupAbort(error) {
  if (error instanceof TestRunFailedError) {
    return error.signal === "SIGABRT";
  }
  return String(error).includes("SIGABRT");
}

function makeLaunchArgs() {
  const workspaceDir = makeTempDir("doctrine-vscode-workspace-");
  const userDataDir = makeTempDir("doctrine-vscode-user-");
  const extensionsDir = makeTempDir("doctrine-vscode-ext-");
  return [
    workspaceDir,
    `--user-data-dir=${userDataDir}`,
    `--extensions-dir=${extensionsDir}`,
    "--disable-extensions",
    "--disable-gpu",
    "--use-mock-keychain",
  ];
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const sourceExtensionDevelopmentPath = path.resolve(__dirname, "../..");
  const repoRoot = path.resolve(sourceExtensionDevelopmentPath, "../..");
  const repoCachePath = path.join(sourceExtensionDevelopmentPath, ".vscode-test");

  for (let attempt = 1; attempt <= MAX_STARTUP_ATTEMPTS; attempt += 1) {
    const extensionDevelopmentPath = stageExtension(sourceExtensionDevelopmentPath);
    const extensionTestsPath = path.join(
      extensionDevelopmentPath,
      "tests/integration/suite/index.js",
    );
    const vscodeExecutablePath = await resolveVSCodeExecutablePath({
      extensionDevelopmentPath,
      repoCachePath,
    });
    try {
      await runTests({
        extensionDevelopmentPath,
        extensionTestsPath,
        vscodeExecutablePath,
        // Keep the VS Code profile paths short so macOS IPC socket creation
        // and cached executable install below the platform path-length limits
        // that can trip extension-host startup in cloned audit worktrees.
        launchArgs: makeLaunchArgs(),
        extensionTestsEnv: {
          DOCTRINE_REPO_ROOT: repoRoot,
        },
      });
      return;
    } catch (error) {
      if (attempt === MAX_STARTUP_ATTEMPTS || !isRetriableStartupAbort(error)) {
        throw error;
      }
      console.error(
        `VS Code integration hit transient ${error.signal || "SIGABRT"} startup abort on attempt ${attempt}/${MAX_STARTUP_ATTEMPTS}; retrying.`,
      );
      await delay(500);
    }
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
