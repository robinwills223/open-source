# Running a Successful Customer Pilot Cohort

## Purpose

For projects reaching `validated_pre_revenue` or early `paying_customers`, a focused pilot cohort of 5 to 10 users provides high-fidelity operational feedback before public launch.

---

## 1. Selecting and Structuring the Pilot

- **Cohort Size:** 5 to 10 active participants. Anything fewer than 5 yields anecdotal feedback; more than 10 creates an unmanageable support burden for a solo builder.
- **Duration:** 2 to 4 weeks. A fixed timeframe creates urgency for both you and your testers.
- **Participant Profile:** Individuals who participated in early interviews or signed up on your demand-test landing page.

---

## 2. Onboarding: Guided vs. Self-Serve

At this stage, **always conduct guided onboarding over a 1:1 video call**:

1. Watch them log in, set up their account, and create their first real record.
2. Do not explain where to click; observe where they hesitate, stumble, or click the wrong button.
3. Take immediate notes on friction points. Self-serve onboarding should only be implemented after 10 users successfully navigate the flow with zero verbal guidance.

---

## 3. Feedback Collection & Observation Cadence

- **Weekly 15-Minute Sync:** Schedule a brief weekly check-in call with each participant.
- **Track Active Usage:** Look at database timestamps (`updated_at`). Do not rely on self-reported usage; verify whether they are actually logging in and entering records each week.
- **Pilot Tracking:** Maintain structured participant records using [pilot-tracker.csv](file:///repo-foundation/templates/validation/pilot-tracker.csv).

---

## 4. Measuring Pilot Success vs. Failure

### Signs of a Successful Pilot
- **Spontaneous Usage:** Testers use the application without you reminding them to log in.
- **Feature Pull:** Testers ask: *"When can I invite my colleague?"* or *"Can you add this one export feature so I can stop using my spreadsheet entirely?"*
- **Conversion Intent:** Testers agree to pay or convert to a subscription at the end of the trial period.

### Signs of a Failing Pilot
- **Chasing Activity:** You have to email them three times to get them to test a feature.
- **Superficial Feedback:** Generic feedback like *"Looks nice!"* without complaints or feature requests indicates they are not using it on real tasks.
- **Reluctance to Commit:** Testers decline to pay even a nominal fee when the trial concludes.

---

## 5. Protecting User Data During the Pilot

Even in an early test cohort, you are handling real people's data:

1. **Activate Minimum Viable Backup:** Follow [backup-and-restore.md](file:///repo-foundation/docs/guides/backup-and-restore.md) to ensure daily snapshots run and are safely stored off-server.
2. **Execute Baseline Security Check:** Run `python manage.py baseline_check` before inviting pilot participants (see [security-baseline.md](file:///repo-foundation/docs/guides/security-baseline.md)).
3. **Be Transparent:** Inform testers that the app is in private beta and how their data is backed up.
