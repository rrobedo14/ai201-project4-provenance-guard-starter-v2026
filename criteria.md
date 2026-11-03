# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---

# Acceptance criteria — Provenance Guard

## 1. False positives

<!-- Your criterion. It must name a number. -->
Out of 10 pieces of plain, authentic human-authored text tested across three separate trial runs, at most 1 receives a high-confidence AI score (0.70 or higher).

**Why this target:** I allow at most 1 false positive in 10 because on a publishing platform, a wrong accusation costs a writer their trust and reputation, whereas a missed detection only lets a piece of AI text slip through.

---

## 2. Score spread

<!-- Your criterion. -->
Across 10 clearly AI-generated samples and 10 clearly human baseline samples, the average combined scores stay separated by at least `0.35` units (AI scoring 0.70 or higher on average, human scoring 0.35 or lower).

**Why this target:** I require a 0.35 gap because a clear separation ensures the system has a distinct boundary between machine and human writing, preventing borderline inputs from collapsing into random guesses.

---

## 3. Label coverage

<!-- Your criterion. -->
Across a test set of 15 diverse inputs, all three system labels (`likely_ai`, `uncertain`, and `likely_human`) appear at least twice.

**Why this target:** I require each label to appear at least twice because every label must be reachable so the system can properly signal ambiguity and nuance instead of forcing every edge case into an artificial binary.

---

## 4. The appeal path

<!-- Your criterion. -->
100% of appeals submitted with a valid `content_id` successfully update the record status to `"appealed"` and write a corresponding entry to the audit log in a single request cycle.

**Why this target:** I set a 100% target because creators disputing a false flag need an ironclad guarantee that their dispute is reliably tracked and recorded for human review without dropping data.

---

## 5. Bad input

<!-- Your criterion. -->
100% of requests with missing text, empty strings, or text exceeding token limits return an HTTP `400 Bad Request` status code without crashing or raising unhandled Python errors.

**Why this target:** I set a 100% interception target because strict input validation protects the core detection models and database backends from failing on malformed or malicious data.


<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
