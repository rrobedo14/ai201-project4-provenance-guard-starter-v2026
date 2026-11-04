# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. **Payload Extraction:** Parses the incoming JSON request to safely extract the `text` and `creator_id` fields.
2. **Input Validation:** Checks whether `text` is a valid, non-empty string—returning a `400 Bad Request` error if validation fails.
3. **Two Signals:** Runs `detector.model_signal(text)` (how predictable the text is to a local language model) and `stylometry.style_signal(text)` (the shape of the text). Each returns a 0–1 score where higher means more likely AI.
4. **Combining Rule:** `scoring.combine_signals(model_score, style_score)` merges the two into one combined score, capping it below the AI band when the signals disagree.
5. **Label Mapping:** `scoring.score_to_label(combined_score)` turns the score into a short `guess` (`human`, `unsure` or `ai`) and the full sentence a reader sees.
6. **ID Generation and Audit Logging:** Generates a unique `content_id` from a truncated UUID, then records the decision, both signal scores, the combined score, the label and the status `decided` with `audit.log_decision()`.
7. **Response Delivery:** Returns JSON containing `content_id`, `creator_id`, `guess`, `confidence`, `label`, `model_score`, `style_score` and `combined_score`.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** 
Token predictability and perplexity—running a local model to evaluate how easily it can guess the text, converting that into a 0–1 score where higher means more likely AI.

**Why that might differ between human and AI writing:**
AI generates text by repeatedly picking likely next words, yielding low perplexity (text the model finds easy to predict). Human writing wanders more through odd word choices, abrupt turns, and specific details.

**What it can't see:**
It cannot see authorship or true intent. Instead, it rewards common words in short, ordinary sentences. Because of this, it has a major structural blind spot: it frequently mislabels second-language writers, younger writers, or anyone writing plainly as AI, while dense, ornate human prose with rare words often scores as human.

### Signal two — the style signal

**What it measures:**
The shape of the text without understanding a word, measured through three structural factors: sentence-length spread (whether sentences vary in length or march in step), type_token_ratio (how much of the vocabulary repeats), and punctuation_density (how many commas, semicolons, colons, dashes, brackets, quotes, `!` and `?` there are per word; full stops are left out because every text has them). Each factor is scaled onto 0–1 (sentence-length spread 0.30–0.90, type-token ratio 0.60–0.85, punctuation 0.04–0.12 marks per word) and flipped so higher means more AI-like, then weighted: spread 0.45, punctuation 0.35, type-token ratio 0.20.

**Why that might differ between human and AI writing:**
Generated prose tends toward even, mid-length sentences and a narrower band of vocabulary because that is what the "most likely next word" approach produces on average. Human writing is lumpier—such as placing a three-word sentence right next to a forty-word one.

**What it can't see:**
It cannot read and has no idea what the text actually says. Anything that changes the shape of the text without changing its substance—such as adding typos, breaking up sentences, or pasting in a quotation—moves the score, making it vulnerable to deliberate shape-altering tricks.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**
A weighted average of the two 0–1 signals, leaning on the model signal, plus one rule for disagreement: **if the two signals are far apart, the result can never be labelled AI.** It can still be "unsure", and it can still be "human". Two methods contradicting each other is not enough evidence to accuse someone, and on a writing site a wrong accusation costs more than a missed detection.

The model signal gets more weight because it reads the words. The style signal only sees shape, and shape is the cheapest thing to change on purpose (adding typos or breaking up sentences).

**The numbers:**
- `combined = 0.6 × model_score + 0.4 × style_score`
- If `|model_score − style_score| > 0.30`, the combined score is capped at `AI_THRESHOLD − 0.01` (0.69), which keeps it inside the "unsure" band at most.
- Thresholds: human ≤ 0.35, AI ≥ 0.70 (matching criterion 1).
- All of these live in `config.py`: `WEIGHT_MODEL_SIGNAL`, `WEIGHT_STYLE_SIGNAL`, `DISAGREEMENT_GAP`, `HUMAN_THRESHOLD`, `AI_THRESHOLD`.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**
* **The Case:** `samples/borderline.json`, a human-style rewrite of the AI sample. Model signal `0.35` (the uncommon wording, e.g. "frazzled" and "wreck focus", is hard to predict, so it reads as human). Style signal `0.51` (the sentences are fairly even in length, so it leans AI-ish despite the dashes and semicolons).
* **What the rule does with it:** `0.6 × 0.35 + 0.4 × 0.51 = 0.41`, which is **unsure**. The gap (0.16) is under 0.30, so the cap doesn't trigger; the weighting alone keeps it out of the AI band. The cap is for wider splits: model `0.95` and style `0.60` would combine to `0.81` (an AI label), but the gap is `0.35`, so the cap pulls it down to `0.69`, which is **unsure**.
* **What the rule can't fix:** two signals that agree and are both wrong. The disagreement rule only fires on a split, so writing that fools both signals in the same direction goes straight to whatever label they agree on. Both signals score short, even, plainly worded sentences as AI-like, so a plain human writer is the likely case. None of my samples tests this yet. If it happens, the appeal path is that writer's only protection.

---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | We think this was probably written by a person. |
| unsure | above 0.35, below 0.70 | We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple. |
| high-confidence AI | 0.70 – 1.00 | We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it. |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->
The person reading it may have written every word, so it says straight out that it is "not an accusation" and that being here is common. It names plain writing because both signals score short, even, ordinary sentences as AI-like, so that's the human writing most likely to land here. In testing, `samples/borderline.json`, where the signals split, landed in this band at 0.41. It says "we can't tell" rather than "this may be AI", so the uncertainty sits with the system, not with the writer.



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

`samples/clearly_ai.json`, submitted from the file.

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d @samples/clearly_ai.json
```

```json
{
  "combined_score": 0.7143,
  "confidence": 0.7143,
  "content_id": "c_da3909e428a7",
  "creator_id": "demo_instructor",
  "guess": "ai",
  "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
  "model_score": 0.7544,
  "style_score": 0.6541
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c_da3909e428a7", "reasoning": "Testing the appeal path: disputing the AI label on samples/clearly_ai.json."}'
```

```json
{
  "content_id": "c_da3909e428a7",
  "message": "Your appeal has been received. A person will review this decision, and the original label is now marked as under review.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=2"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.7143,
      "content_id": "c_da3909e428a7",
      "creator_id": "demo_instructor",
      "guess": "ai",
      "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
      "model_score": 0.7544,
      "status": "decided",
      "style_score": 0.6541,
      "timestamp": "2026-11-04T00:25:45+00:00"
    },
    {
      "content_id": "c_da3909e428a7",
      "creator_id": "demo_instructor",
      "event": "appeal",
      "reasoning": "Testing the appeal path: disputing the AI label on samples/clearly_ai.json.",
      "status": "under_review",
      "timestamp": "2026-11-04T00:26:04+00:00"
    }
  ]
}
```

The original decision is untouched; the appeal sits after it with the same `content_id` and the new status `under_review`.

---

## How I Used AI

**Moment 1**
- *What I asked for:* A prompt asking Claude to write a message from a real writer who was caught by the 1-in-10 false-positive error margin, without telling me whether the threshold was right or wrong.
- *What came back:* A stark, frustrated message from an innocent creator whose genuine work was wrongly flagged, highlighting the exact human sting of an unmerited AI accusation.
- *What I changed:* Kept the numeric target defensible (`1 in 10`), but used the emotional perspective from the generated message to sharpen the final rationale for Criterion 1, ensuring the true cost of false positives was fully captured.

**Moment 2**

- *What I asked for:* How to fix my service, after asking the AI to review my acceptance criteria.
- *What came back:* A list of problems in `app.py` and `criteria.md`: `/submit` ran the detector *before* checking for empty text, so bad input would crash instead of returning 400. The response sent `"content_id": "hardcoded"`, so no appeal could ever find a submission. Criterion 1 used 0.70 while `config.py` used 0.65, and criterion 4 expected status `"appealed"` while the code writes `under_review`.
- *What I changed:* I fixed the code: `/submit` now validates `text` and returns 400 before any signal runs, `content_id` is a real ID (`c_` plus 12 hex characters from a UUID) so `/appeal` can find it, and `config.py` now uses `AI_THRESHOLD = 0.70` to match criterion 1. I kept the criteria wording as originally written. Two mismatches remain in `criteria.md`, and I'll fix them as unit 8 revisions underneath the originals instead of editing them in place: criterion 4 expects status `"appealed"` while the code writes `under_review`, and criterion 3 names the labels `likely_ai`, `uncertain` and `likely_human` while the code returns `ai`, `unsure` and `human`.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
