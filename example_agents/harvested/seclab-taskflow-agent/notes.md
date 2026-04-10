# Notes

This source is a strong pressure test for Doctrine because it expresses workflows as declarative YAML with multiple layers of behavior: personalities, taskflows, reusable taskflows, inputs, env, toolboxes, and run-mode controls.

The strongest files are the comprehensive grammar test and the CVE review taskflow. The comprehensive test covers almost every grammar feature in one place, while the CVE example pushes evidence-only security review, explicit stop lines, and no-speculation guardrails. The reusable taskflow example is good for inheritance and override pressure. The triage personality is useful as a minimal role-only artifact.

Selected artifacts:
- `raw/README.md`
- `raw/examples/personalities/example_triage_agent.yaml`
- `raw/examples/taskflows/CVE-2023-2283.yaml`
- `raw/examples/taskflows/comprehensive_test.yaml`
- `raw/examples/taskflows/example_reusable_taskflows.yaml`
