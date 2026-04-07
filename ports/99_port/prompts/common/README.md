# Common Prompt Layers For The 99 Port

This directory now has seven separate jobs.

- `role_home.prompt` defines the shared ordered role-home shell.
- `support.prompt` defines reusable non-skill support-section stubs such as attached-checkout guidance.
- `skills.prompt` defines reusable skill contracts that agent prompts can reference directly, including poker grounding and PokerKB.
- `handoffs/` defines shared and role-specific handoff comment outputs.
- `artifacts/` defines the single output artifact each agent owns.
- `surfaces/` defines reusable readable contracts and support surfaces that later lanes may consume.
- `inputs/` defines consumer-side lane prerequisites only.

The key rule is simple: a producing lane's own artifact does not belong in that
lane's required input bundle unless the role prompt explicitly says the lane
must resume from its own prior artifact as an input.

That separation keeps the port aligned with the examples:

- role-home workflows define shared rendered section order
- support workflows hold shared non-skill support prose stubs
- skills describe reusable capabilities a role can run
- handoff outputs define the current comment truth a downstream owner should trust
- inputs describe how a turn gets what it consumes
- outputs describe what a turn produces
- readable reusable surfaces are modeled separately from both
