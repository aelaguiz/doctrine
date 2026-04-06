# Env Input Agent

Core job: locate the tracker checkout from an environment variable before doing any tracker work.

## Inputs

### Tracker Root

- Source: EnvVar
- Variable: `TRACKER_ROOT`
- Shape: Directory path
- Requirement: Required

This environment variable points to the tracker checkout root.

## Your Job

- Look up the tracker root from the environment variable.
- Fail if the environment variable is missing.
