const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const childProcess = require("node:child_process");

const {
  downloadAndUnzipVSCode,
  runTests,
  TestRunFailedError,
} = require("@vscode/test-electron");
const CACHE_PATH_ENV = "DOCTRINE_VSCODE_TEST_CACHE";
const EXECUTABLE_PATH_ENV = "DOCTRINE_VSCODE_EXECUTABLE_PATH";
const PACKAGED_VSIX_ENV = "DOCTRINE_VSCODE_PACKAGED_VSIX";
const MAX_STARTUP_ATTEMPTS = 4;
const EXTENSION_COPY_EXCLUDE_NAMES = new Set([".vscode-test"]);

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

function createHarnessExtension() {
  const harnessDir = makeTempDir("doctrine-vscode-packaged-harness-");
  fs.writeFileSync(
    path.join(harnessDir, "package.json"),
    JSON.stringify(
      {
        name: "doctrine-language-packaged-smoke-harness",
        publisher: "aelaguiz",
        version: "0.0.0",
        engines: { vscode: "^1.105.0" },
        main: "./extension.js",
        activationEvents: ["*"],
      },
      null,
      2,
    ),
  );
  fs.writeFileSync(
    path.join(harnessDir, "extension.js"),
    [
      "function activate() {}",
      "function deactivate() {}",
      "",
      "module.exports = { activate, deactivate };",
      "",
    ].join("\n"),
  );
  return harnessDir;
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

function makeLaunchContext({ disableExtensions }) {
  const workspaceDir = makeTempDir("doctrine-vscode-workspace-");
  const userDataDir = makeTempDir("doctrine-vscode-user-");
  const extensionsDir = makeTempDir("doctrine-vscode-ext-");
  const launchArgs = [
    workspaceDir,
    `--user-data-dir=${userDataDir}`,
    `--extensions-dir=${extensionsDir}`,
    "--disable-gpu",
    "--use-mock-keychain",
  ];
  if (disableExtensions) {
    launchArgs.splice(3, 0, "--disable-extensions");
  }
  return {
    extensionsDir,
    launchArgs,
    userDataDir,
    workspaceDir,
  };
}

function runCommand(command, args) {
  const result = childProcess.spawnSync(command, args, {
    stdio: "inherit",
  });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} exited with status ${result.status}.`);
  }
}

function resolveVSCodeCliPath(vscodeExecutablePath) {
  const candidate = path.resolve(
    path.dirname(vscodeExecutablePath),
    "../Resources/app/bin/code",
  );
  return fs.existsSync(candidate) ? candidate : vscodeExecutablePath;
}

function installPackagedVsix(vscodeExecutablePath, vsixPath, launchContext) {
  runCommand(resolveVSCodeCliPath(vscodeExecutablePath), [
    "--install-extension",
    vsixPath,
    "--force",
    `--extensions-dir=${launchContext.extensionsDir}`,
    `--user-data-dir=${launchContext.userDataDir}`,
    "--no-sandbox",
    "--disable-gpu",
    "--use-mock-keychain",
  ]);
}

function resolvePackagedVsixPath() {
  const configuredPath = process.env[PACKAGED_VSIX_ENV];
  if (!configuredPath) {
    return undefined;
  }
  return path.resolve(configuredPath);
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const sourceExtensionDevelopmentPath = path.resolve(__dirname, "../..");
  const repoRoot = path.resolve(sourceExtensionDevelopmentPath, "../..");
  const repoCachePath = path.join(sourceExtensionDevelopmentPath, ".vscode-test");
  const packagedVsixPath = resolvePackagedVsixPath();
  if (packagedVsixPath && !fs.existsSync(packagedVsixPath)) {
    throw new Error(`Packaged VSIX not found: ${packagedVsixPath}`);
  }

  for (let attempt = 1; attempt <= MAX_STARTUP_ATTEMPTS; attempt += 1) {
    const extensionDevelopmentPath = packagedVsixPath
      ? createHarnessExtension()
      : stageExtension(sourceExtensionDevelopmentPath);
    const extensionTestsPath = path.join(
      sourceExtensionDevelopmentPath,
      "tests/integration/suite/index.js",
    );
    const launchContext = makeLaunchContext({
      disableExtensions: !packagedVsixPath,
    });
    const vscodeExecutablePath = await resolveVSCodeExecutablePath({
      extensionDevelopmentPath,
      repoCachePath,
    });
    if (packagedVsixPath) {
      installPackagedVsix(vscodeExecutablePath, packagedVsixPath, launchContext);
    }
    try {
      await runTests({
        extensionDevelopmentPath,
        extensionTestsPath,
        vscodeExecutablePath,
        // Keep the VS Code profile paths short so macOS IPC socket creation
        // and cached executable install below the platform path-length limits
        // that can trip extension-host startup in cloned audit worktrees.
        launchArgs: launchContext.launchArgs,
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
