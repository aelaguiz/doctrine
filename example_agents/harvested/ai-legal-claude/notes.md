# Notes

## Source Summary

This source is a markdown-native legal assistant with one orchestration skill
and multiple specialized agent files. The contract-review pipeline is split
into clause extraction, risk scoring, compliance checking, obligation mapping,
and negotiation recommendations.

## High-Signal Patterns

- The flagship review skill launches multiple subagents and merges their
  results into one report.
- Each subagent owns a narrow role, rather than all of them sharing a generic
  contract-review prompt.
- The clause, risk, compliance, terms, and recommendations docs each define a
  separate output shape.
- Legal disclaimers and report templates are mandatory parts of the workflow.
- The repo repeatedly distinguishes analysis, scoring, compliance, and redline
  output as different contracts.

## What This Teaches Doctrine

This source is useful for Doctrine examples that need:

- explicit orchestration with named specialist roles
- portable handoff surfaces between analysis stages
- output templates with strict ordering and disclaimers
- role-specific contract analysis instead of a single monolithic agent
- markdown-native legal-analysis workflows
