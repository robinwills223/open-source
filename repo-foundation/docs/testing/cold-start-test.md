# Cold-Start Usability Test Protocol

This document defines the standardized observation protocol for testing how a user experiences `repo-foundation` for the first time without prior coaching.

---

## 1. Test Objectives

1. Measure time required to reach a validated `project.profile.yaml`.
2. Measure time required to run the generated local prototype.
3. Identify every moment of hesitation, misinterpretation, or failure in the user's own words.
4. Verify whether the LLM adheres to intake rules without hallucinating unrequested capabilities.

---

## 2. Test Setup

- **Hardware & Environment:** Participant's personal or lab computer with Python 3.10+ installed.
- **Repository State:** A fresh, clean clone or ZIP download of `repo-foundation` extracted to an empty folder.
- **LLM Interface:** The participant opens their preferred LLM coding interface (e.g. Claude Code, ChatGPT, Antigravity, Cursor) pointed at the repository root.
- **Initial Prompt:** Hand the participant a note card containing the exact opening prompt:
  > *"Help me test my idea using this repo."*
- **No Prior Coaching:** Do not explain the schema, docs, or capabilities beforehand.

---

## 3. Observer Rules: What You May & May Not Say

### What the Observer MAY Say
- *"Please speak your thoughts out loud as you read and type."*
- *"What are you thinking right now?"*
- *"Take as much time as you normally would."*
- *"If you feel stuck or decide to stop, let me know."*

### What the Observer MUST NOT Say
- Do **not** point to specific files, documentation sections, or tools.
- Do **not** explain technical terms or suggest answers to LLM intake questions.
- Do **not** correct command syntax or typos in terminal commands.
- Do **not** intervene when an error occurs unless an OS crash prevents continuing.

---

## 4. What to Record

1. **LLM Tool & Model Version:** Record exact client name and model identifier.
2. **Participant Audience Persona:** Non-technical founder, junior developer, or senior developer.
3. **Time to Validated Profile ($T_{\text{profile}}$):** Clock time from opening prompt to saved, valid profile.
4. **Time to Running Prototype ($T_{\text{app}}$):** Clock time from opening prompt to viewing the local app in a browser.
5. **Direct Quotations:** Record every point of confusion verbatim in the participant's own words.
6. **Task Completion:** Reached running app? (Yes / No).

---

## 5. One-Page Results Template

```markdown
# Cold-Start Test Session Report

- **Date & Time:** [DATE]
- **Participant ID:** [PARTICIPANT-001]
- **Audience Persona:** [ ] Founder  [ ] Junior Dev  [ ] Senior Dev
- **LLM Tool & Version:** e.g. Claude 3.5 Sonnet / Antigravity / Cursor
- **Operating System:** Windows / macOS / Linux

### Quantitative Timing
- Time to Initial Intake Prompt: _____ minutes
- Time to Validated Profile:       _____ minutes
- Time to Scaffold Generation:     _____ minutes
- Time to Running App in Browser:  _____ minutes
- Total Elapsed Time:              _____ minutes
- Final Result: [ ] Success (App Running)  [ ] Abandoned / Blocked

### Verbatim Confusions & Hesitations
1. *[Participant quote upon reading intake Q...]*
2. *[Participant quote when running terminal command...]*
3. *[Participant quote regarding DECISIONS-FOR-FOUNDER.md...]*

### Observations & Bottlenecks
- Intake Friction: (e.g. did user understand question about logins?)
- Generation Friction: (e.g. command path confusion, virtualenv issues)
- Documentation Clarity: (did the user read run-locally.md or ask the LLM?)

### Actionable Fixes Identified
- [ ] Documentation wording change in docs/...
- [ ] Intake prompt clarification in AGENTS.md
- [ ] Tool error message improvement in tools/...
```

