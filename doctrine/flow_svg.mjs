// Renders a `.d2` source file to SVG via the pinned D2 bundle.
//
// Determinism contract: the fields pinned in `renderOptions` below are what
// keep the emitted SVG byte-stable across hosts and runs. Every checked-in
// `*.flow.svg` under `examples/*/ref/` is diffed byte-for-byte by
// `verify_corpus`, so changing any of these fields invalidates every flow ref:
//   - `salt="doctrine-flow-v1"`: D2's id-generation seed. Bump this string
//     only when a ref regeneration is the intent.
//   - `animateInterval=0`: no animation timing baked into the SVG.
//   - `center`, `pad`, `sketch`: layout knobs pinned so geometry never drifts.
//
// The Python caller at `doctrine/_flow_render/svg.py` spawns this helper and
// translates exit codes into `FlowRenderDependencyError` / `FlowRenderFailure`.
// This helper's only job is: compile, render with the pinned options, write.

import { readFile, writeFile } from "node:fs/promises";
import { D2 } from "@terrastruct/d2";

async function main() {
  const [inputPath, outputPath] = process.argv.slice(2);
  if (!inputPath || !outputPath) {
    throw new Error("usage: node flow_svg.mjs <input.d2> <output.svg>");
  }

  const source = await readFile(inputPath, "utf8");
  const d2 = new D2();
  const result = await d2.compile(source);
  const renderOptions = {
    ...result.renderOptions,
    animateInterval: 0,
    center: true,
    pad: 24,
    salt: "doctrine-flow-v1",
    sketch: false,
  };
  const svg = await d2.render(result.diagram, renderOptions);
  await writeFile(outputPath, svg, "utf8");
  process.exit(0);
}

main().catch((error) => {
  const detail = error instanceof Error ? error.stack || error.message : String(error);
  process.stderr.write(`${detail}\n`);
  process.exit(1);
});
