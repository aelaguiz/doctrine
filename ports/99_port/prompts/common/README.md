# Common Prompt Layers For The 99 Port

This directory now has three separate jobs.

- `artifacts/` defines the single output artifact each agent owns.
- `surfaces/` defines reusable readable contracts and support surfaces that later lanes may consume.
- `inputs/` defines consumer-side lane prerequisites only.

The key rule is simple: a producing lane's own artifact does not belong in that
lane's required input bundle unless the role prompt explicitly says the lane
must resume from its own prior artifact as an input.

That separation keeps the port aligned with the examples:

- inputs describe how a turn gets what it consumes
- outputs describe what a turn produces
- readable reusable surfaces are modeled separately from both
