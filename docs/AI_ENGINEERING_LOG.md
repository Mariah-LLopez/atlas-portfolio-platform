# AI Engineering Log

Use this document to show judgment about AI-assisted engineering rather than merely stating that
you use AI tools.

## Entry template

### Date

### Task
What were you trying to build, debug, test, document, or refactor?

### AI tool
Examples: Codex, Claude Code, Cursor, Cline, etc.

### Prompt / delegation strategy
Summarize the task you delegated. Do not paste secrets or proprietary information.

### AI contribution
What did the tool produce?

### Human verification
What did you independently inspect, calculate, test, or challenge?

### Defect or limitation found
What did the AI miss, misunderstand, overcomplicate, or hallucinate?

### Resolution
What changed before the code was accepted?

### Tests added
List the tests that protect against regression.

### Judgment
Would you delegate this kind of task to an AI coding agent again? Why or why not?

---

## Example

### Task
Generate edge-case tests for portfolio weight validation.

### AI contribution
Suggested tests for negative weights, weights above configured maximums, NaNs, and sums not equal
to one.

### Human verification
Reviewed each test against the intended portfolio contract.

### Defect or limitation found
Two suggested tests asserted internal implementation details instead of externally visible behavior.

### Resolution
Rewrote those tests around public function outputs and exceptions.

### Judgment
High leverage for test ideation; lower trust for deciding the software contract.
