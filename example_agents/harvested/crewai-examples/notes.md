# Notes

This source is useful because it expresses agent behavior as small YAML role/task pairs instead of large framework prose. The meeting assistant flow and email responder flow are the strongest harvests: both combine an agent definition, a task definition, explicit input placeholders, and a concrete expected output.

The main Doctrine pressure here is orchestration and output shape. These examples are good raw material for examples that need a clear agent role, a narrow task, and a downstream artifact the reader can trust. They are also useful for branch-like cases because the email responder task has an explicit proceed vs reject split.

Selected artifacts:
- `raw/README.md`
- `raw/flows/meeting_assistant_flow/src/meeting_assistant_flow/crews/meeting_assistant_crew/config/agents.yaml`
- `raw/flows/meeting_assistant_flow/src/meeting_assistant_flow/crews/meeting_assistant_crew/config/tasks.yaml`
- `raw/flows/email_auto_responder_flow/src/email_auto_responder_flow/crews/email_filter_crew/config/agents.yaml`
- `raw/flows/email_auto_responder_flow/src/email_auto_responder_flow/crews/email_filter_crew/config/tasks.yaml`
