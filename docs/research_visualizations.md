# Visualizing complex agent workflows: the definitive open-source toolkit landscape

**React Flow + ELK.js is the dominant stack for interactive agent workflow visualization, used by virtually every major AI workflow platform (Dify, Langflow, Flowise, n8n, ComfyUI).** For your Doctrine compiler's output, the most effective architecture is generating a JSON node/edge data structure that React Flow consumes, with ELK.js computing hierarchical layouts that handle sub-workflows, typed ports, and conditional routing. However, a newer contender — ByteDance's FlowGram — is purpose-built for exactly this use case and deserves serious evaluation. For static diagram-as-code output, D2 (Terrastruct) produces the most beautiful results of any text-to-diagram tool. No standalone, agent-specific visualization library exists yet that simply ingests a workflow definition and renders an interactive graph — this remains a gap the ecosystem is racing to fill.

---

## React Flow reigns as the undisputed foundation

**React Flow** (now part of the xyflow monorepo) has become the substrate layer for agent workflow visualization across the industry. With **~35,500 GitHub stars**, **4.3M+ weekly npm downloads**, and daily commits as of April 2026, it is the most actively maintained option by a wide margin.

The library renders nodes as arbitrary React components (enabling rich typed I/O port displays, status badges, agent metadata panels) and edges as customizable SVG paths (supporting conditional labels, animated flow indicators, and back-edges for review loops). It provides full interactivity — zoom, pan, drag, minimap, snap-to-grid, box selection, and virtualized rendering that only processes visible viewport elements. The critical architectural feature for Doctrine is that **React Flow is entirely data-driven**: you pass JSON arrays of nodes and edges, and it renders them. This makes it ideal as a compile-step visualization target.

The key limitation is that React Flow has **no built-in auto-layout**. This is by design — it delegates layout to external engines. The official integration path is:

- **Dagre** (~4,900 stars, semi-maintained) for simple hierarchical DAGs. Fast, minimal configuration, but **cannot handle compound/nested nodes** (sub-workflows) and has known bugs with cross-edge routing.
- **ELK.js** (~2,400 stars, maintained by Kiel University) for complex workflows. This is the only JS layout engine that properly handles **hierarchical compound graphs with port constraints** — exactly what Doctrine's typed inputs/outputs, sub-workflow grouping, and handoff chains require. It supports orthogonal edge routing, configurable layering strategies, and port-based connection points. The React Flow team warns that "its complexity makes it difficult for us to support folks," but engineering teams at Pinpoint and others have confirmed it's **the only layout engine that handles complex branching workflows well**.
- **d3-hierarchy** for single-root tree variants and **d3-force** for physics-based exploration (neither is appropriate for structured workflow DAGs).

**The recommended Doctrine integration pattern**: compile your DSL to a JSON structure containing `{ nodes: [...], edges: [...], elkOptions: {...} }`, run ELK.js layout computation (async, can run server-side via Node.js), then feed the positioned nodes/edges to React Flow. For sub-workflows, use React Flow's group node feature with ELK's native compound graph support. Framework alternatives exist: **Svelte Flow** (same xyflow team, Svelte 5 rewrite complete) and **Vue Flow** (~4,000 stars, community-maintained, endorsed by xyflow but single-maintainer risk).

A hidden gem worth noting: **Overflow** (overflow.dev) provides 40+ production-ready React Flow components — reshapeable edges, ELK.js auto-layout integration, grouping, undo/redo — features teams repeatedly rebuild from scratch. Built by Synergy Codes, a 70-person team with 13+ years of diagramming experience.

---

## FlowGram is the most promising embeddable AI workflow framework

**FlowGram** (github.com/bytedance/flowgram.ai, **~5,400 stars**, MIT license) is ByteDance's open-source workflow development framework that powers Coze Studio's frontend canvas. Unlike React Flow, which is a generic node graph library, FlowGram is **purpose-built for AI workflow platforms** and ships with agent-specific primitives.

What makes FlowGram uniquely relevant for Doctrine is its built-in **variable engine with scope constraints, type inference, and data-flow tracking** — closely mirroring Doctrine's typed inputs/outputs. It provides pre-built node types for LLM calls, conditional branching, code execution, HTTP requests, and loops. The framework supports both free-layout (drag anywhere) and fixed-layout (structured pipeline) modes, with a node configuration form engine that auto-generates settings panels from node schemas.

FlowGram is actively maintained (commits through August 2025), backed by ByteDance's engineering resources, and explicitly designed to be embedded in third-party applications. The trade-off is that it's relatively new, the community is smaller than React Flow's, and documentation skews toward Chinese-language resources. But for a compile-step visualization that needs typed I/O annotations, hierarchical grouping, conditional routing, and parallel branches **out of the box**, FlowGram eliminates months of custom React Flow component development.

---

## AntV G6 and X6 offer powerful alternatives from Alibaba's ecosystem

**AntV G6** (github.com/antvis/G6, **~11,000 stars**, MIT) underwent a complete v5.0 rewrite with a triple-renderer architecture supporting Canvas, SVG, and WebGL — even mixed across layers. Its standout feature for Doctrine is native **"combo" (compound node) support** with built-in collapse/expand, directly modeling sub-workflows. G6 implements layout algorithms in **Rust compiled to WASM** and WebGPU for high performance, and includes a Level-of-Detail system that intelligently shows/hides text and icons based on zoom level.

**AntV X6** (github.com/antvis/X6, **~5,600 stars**, MIT) is explicitly designed for DAG diagrams, ER diagrams, and flowcharts with an editing focus. It supports HTML/React/Vue/Angular/Svelte custom nodes, alignment lines, snap-to-grid, and undo/redo. X6 is the editing counterpart to G6's analysis focus — for a workflow inspector/editor, X6 is the more appropriate choice.

Both libraries have strong technical foundations but **primarily Chinese-language documentation and community**. English documentation has improved but remains less comprehensive. Known bugs exist with G6's combo feature (edges disappearing during expand/collapse). If your team is comfortable navigating this ecosystem, G6's combo system + WASM-accelerated layouts represent the most technically advanced option for rendering complex hierarchical agent workflows.

---

## D2 leads the diagram-as-code renaissance

For static or semi-interactive visualization output (documentation, CI-generated diagrams, embeddable SVGs), **D2** (github.com/terrastruct/d2, **~23,400 stars**, MPL-2.0) produces the most beautiful results of any text-based diagram tool. Community consensus on Hacker News calls it "much prettier and more approachable than PlantUML while feeling more powerful and versatile than Mermaid."

D2 offers three layout engines: dagre (default, fast), ELK (bundled, good for port-based diagrams), and **TALA** (commercial, purpose-designed for software architecture diagrams — produces the best-looking output). It supports nested containers for sub-workflows, scenarios/layers for overlaying execution states, variables and imports for modularity, and a programmatic Go API (`d2oracle`) for dynamic generation. Output SVGs include interactive tooltips and links.

**The Doctrine integration pattern**: compile your DSL to `.d2` source text, then use the D2 CLI or Go library to render SVG/PNG. This works well for documentation, CI pipelines, and static previews. D2 cannot match React Flow's full interactivity (no click-to-inspect, no live state updates), but for compile-step documentation output it's the highest-quality option. You can also route D2 through **Kroki** (a universal diagram API supporting 20+ engines) for unified rendering infrastructure.

---

## State machines map naturally to XState's statechart model

**XState** (github.com/statelyai/xstate, **~29,400 stars**, MIT, v5.30.0 released March 2026) provides the strongest formal foundation for visualizing agent routing logic as statecharts. Its actor model maps naturally to multi-agent communication patterns, and statechart semantics — nested/parallel states, guards (conditional transitions), actions, invocations — align closely with Doctrine's routing rules, review gates, and conditional logic.

The **Stately Visualizer** (stately.ai/viz) is free, open-source, and embeddable via iframe with customization options. It renders clean, formal statechart notation with hierarchical state grouping and handles complex nested hierarchies well. The **@statelyai/inspect** package enables runtime inspection of running state machines with sequence diagram visualization of actor communication. XState's JSON-serializable machine definitions make it straightforward to generate from a compiler — emit JSON, render visually.

The limitation is that statecharts model **state transitions**, not **data flow DAGs**. If Doctrine's workflows are primarily stateful routing logic (which agent handoff chains and review gates often are), XState is an excellent fit. If they're primarily data-pipeline DAGs with typed I/O flowing between transformation steps, React Flow is more natural. Many real agent workflows are **both** — a hybrid approach using XState for routing/state logic and React Flow for data flow visualization may be warranted.

---

## BPMN tooling offers surprising maturity for workflow patterns

**bpmn-js** (github.com/bpmn-io/bpmn-js, **~9,000 stars**, v18.13.1) is the most mature embeddable workflow visualization toolkit available. BPMN 2.0's vocabulary — gateways (conditional routing), events (triggers), tasks (agent steps), pools/lanes (agent grouping), sub-processes (hierarchical workflows) — maps remarkably well to agent orchestration patterns. The underlying **diagram-js** library (1,892 stars) is a generic diagramming toolbox that can be extended with custom node types.

bpmn-js supports programmatic construction, event listeners, custom overlays, and rendering extensions (the documentation literally demonstrates "Nyan cats instead of service tasks"). The **bpmn-js-token-simulation** extension animates flow execution through the diagram. If Doctrine's semantics can be mapped to BPMN constructs, this provides the most complete out-of-the-box workflow visualization with the least custom development — at the cost of BPMN's visual vocabulary, which some find overly formal.

---

## The emerging AI-native visualization layer

Several tools are converging on the specific problem of agent workflow visualization, though none yet provides a standalone, drop-in library:

**Langfuse** (open-source, MIT) launched a **Graph View for LangGraph traces** in February 2025, visualizing agent execution paths overlaid on conceptual workflow graphs. **Arize Phoenix** provides visual agent workflow maps with span-level tracing. **Rivet** (github.com/Ironclad/rivet, ~4,000 stars, MIT) is a visual programming environment with 60+ node types for AI agent workflows, including conditional logic, loops, parallel execution, and hierarchical subgraphs — though its Electron desktop app isn't easily embeddable. **Sim Studio** (github.com/simstudioai/sim) earned 196 points on Hacker News as a purpose-built open-source agent workflow GUI, praised for exposing "exactly what's being executed" rather than over-abstracting.

**Cloudflare published a notable engineering blog** demonstrating automatic diagram generation from workflow code via AST parsing — converting minified JavaScript to an intermediate graph representation to visual diagrams. This "compile code to visualization" pattern is exactly what Doctrine needs, and Cloudflare's implementation validates the architecture at scale.

---

## How the pieces fit together for Doctrine

The optimal architecture depends on your output targets. Based on community consensus and the analysis above, here is a decision framework:

- **Interactive web inspector** (primary recommendation): Doctrine compiler → JSON nodes/edges with ELK layout hints → **React Flow + ELK.js** with custom node components showing typed I/O ports, agent metadata, and routing conditions. Use the Overflow component library to accelerate development. If you need AI-specific primitives out of the box, evaluate **FlowGram** as an alternative that trades ecosystem size for domain-specific features.

- **Static documentation output**: Doctrine compiler → D2 source text → **D2 with TALA engine** → SVG/PNG. Beautiful, version-controllable, CI-friendly. Route through Kroki if you want multi-format support.

- **State machine inspection**: Doctrine compiler → XState JSON machine definition → **Stately Visualizer** embed. Best for visualizing routing logic, review gate state transitions, and handoff chain sequencing.

- **Process-oriented view**: Doctrine compiler → BPMN XML → **bpmn-js** embed. Best if your workflows have clear gateway/event/task semantics and you want the richest out-of-the-box workflow visualization.

The critical insight from real-world experience (Splunk engineering, Pinpoint engineering) is that **generic layout algorithms fail for business process visualization** — you will likely need to encode domain-specific layout hints from Doctrine's semantic structure (agent groupings, handoff chain ordering, review gate positioning) into the layout engine's configuration. ELK.js's extensive configuration surface makes this possible; dagre's does not.

| Tool | Stars | Last Active | Layout Quality | Rendering | Interactivity | Embeddable | Agent-Specific |
|------|-------|-------------|---------------|-----------|---------------|------------|----------------|
| **React Flow + ELK.js** | 35.5k | Apr 2026 | ★★★★★ (ELK) | ★★★★★ | Full interactive | ✅ React component | Used by Dify, Langflow, Flowise |
| **FlowGram** | 5.4k | Aug 2025 | ★★★★ | ★★★★ | Full interactive | ✅ Designed for it | Built for AI workflow platforms |
| **D2 (Terrastruct)** | 23.4k | Oct 2025 | ★★★★★ (TALA) | ★★★★★ | Tooltips/links | ✅ CLI/API | Architecture diagrams |
| **AntV G6 v5** | 11k | 2025-2026 | ★★★★ (WASM) | ★★★★★ | Full interactive | ✅ JS library | Graph analysis + viz |
| **XState/Stately** | 29.4k | Mar 2026 | ★★★★ | ★★★★ | Full interactive | ✅ iframe/inspect | State machine modeling |
| **bpmn-js** | 9k | 2025-2026 | ★★★★ | ★★★★ | Full interactive | ✅ npm package | Process orchestration |
| **AntV X6** | 5.6k | 2025 | ★★★ | ★★★★ | Full interactive | ✅ JS library | DAG/flowchart editing |
| **Cytoscape.js** | 10.8k | Active | ★★★★★ (15+ algos) | ★★★ | Full interactive | ✅ JS library | Network analysis |
| **JointJS** | 4.5k | 2025 | ★★★ (paid for auto) | ★★★★ | Full interactive | ✅ JS library | Enterprise diagramming |
| **Rivet** | 4k | Active | ★★★ | ★★★★ | Full interactive | ⚠️ Electron app | AI agent visual programming |
| **Inngest Workflow Kit** | 5k | Active | ★★★ | ★★★ | Full interactive | ✅ React components | Event-driven workflows |

## Conclusion

The visualization ecosystem for complex agent workflows is bifurcated: **mature, general-purpose graph libraries** (React Flow, Cytoscape.js, G6) that require significant customization, and **tightly-coupled AI platforms** (Langflow, Dify, n8n) whose visualization cannot be extracted. FlowGram is the first serious attempt to bridge this gap with an embeddable, AI-workflow-specific framework, and it deserves evaluation despite its youth.

For Doctrine specifically, the compile-step architecture points toward **React Flow + ELK.js** as the pragmatic choice — it's battle-tested across dozens of AI workflow tools, the JSON-based data model maps cleanly to compiler output, and ELK.js is the only layout engine that handles hierarchical compound graphs with typed ports. Invest development time in three custom React Flow components: an agent node (showing typed I/O ports and metadata), a conditional edge (showing routing rules), and a group node (showing sub-workflows with collapse/expand). That foundation, combined with ELK.js layout computation, will handle everything Doctrine needs to express. For beautiful static output alongside the interactive view, add D2 as a secondary compile target — the dual-output pattern (interactive inspector + beautiful documentation diagrams) gives you the best of both worlds.
