# Project collaboration preferences

- At the start of a new chat or resumed milestone, inspect `STATUS.md`, the
  current branch and working tree, the relevant repository files, and the test
  suite before choosing the next exercise.
- Teach the project one small exercise at a time. Do not jump ahead to later
  layers or combine multiple learning objectives unless the user asks.
- After the user completes an exercise, review their implementation, explain
  any correctness or design issues, and run the relevant focused tests plus
  the full suite when appropriate.
- Do not modify exercise code for the user unless they explicitly ask for the
  change. Guidance, review, and diagnostic commands are allowed by default.
- Preserve existing user changes and avoid replacing their implementation
  merely to enforce a stylistic preference.
- Keep the architecture representative of real-world applications while
  explaining new patterns in plain language and introducing complexity in
  small steps.
- Update `STATUS.md` at completed milestone boundaries, not after every small
  exercise.
- Before committing a milestone, review the complete diff, verify the suite,
  and confirm there are no stale imports or superseded paths.
- When the user asks for a resume prompt for a new chat or milestone, begin
  the prompt with a distinct Markdown H1 in the form
  `# Agentic To-Do — <Milestone Name>`.
- Choose a milestone-specific title rather than reusing the current chat's
  title or a generic project title.
