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
