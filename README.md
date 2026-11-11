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

**My limits:** 5 per minute, 50 per day

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
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

From `results/attack_run_2026-11-10_1838.md`, produced by `run_attacks.py::main`
against `app.py::submit`. 56 attacks: **20 broke, 36 held**. Thresholds at the
time of the run: human ≤ 0.35, AI ≥ 0.70, disagreement gap 0.30.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_5231d4c7967a` | unsure | 0.406 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_6d6c719c71c7` | unsure | 0.513 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_448044c6750c` | unsure | 0.618 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_3cc15b8a5d56` | unsure | 0.655 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_500ef2741b59` | human | 0.347 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_e30e942648b9` | unsure | 0.516 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_4a2828d79077` | unsure | 0.466 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `c_948894a2bd69` | unsure | 0.467 | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_aed94182d81e` | unsure | 0.669 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_c4073aecdfc1` | ai | 0.959 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_ec62cfae2395` | unsure | 0.689 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c_f27efe6ed02c` | ai | 0.808 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_dd2fb3aa938c` | ai | 0.835 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_37e1b788881e` | ai | 0.813 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_afcb0055b7be` | ai | 0.880 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_cd7e5b539486` | ai | 0.820 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_d91bd780a50a` | ai | 0.800 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `c_4fbfa0aaf20b` | unsure | 0.473 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_27608046966a` | unsure | 0.489 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_3be9e74b9ea4` | human | 0.329 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_6ffe05c9df60` | unsure | 0.638 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_100aa1d53e71` | unsure | 0.524 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_b56266d67757` | unsure | 0.513 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_26fda2221935` | unsure | 0.657 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 500 | `—` | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | `c_b2f65d686649` | human | 0.200 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | `c_8c586d3062b6` | human | 0.207 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | `c_6f014b0fb9f7` | unsure | 0.690 | HELD |
| MF06 | malformed | text is emoji only | 200 | `c_031749937113` | unsure | 0.690 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `c_69b5865be406` | unsure | 0.690 | HELD |
| MF08 | malformed | text is 60,000 characters | 200 | `c_589ce9725e05` | ai | 0.954 | BROKE |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `c_9d0aa71947e4` | unsure | 0.374 | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 200 | `c_bb1acfc95be2` | human | 0.230 | BROKE |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_6761ad58cf47` | human | 0.247 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_919628fb3fd7` | human | 0.247 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_ea83de44c00c` | human | 0.247 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_8fe5b17491cf` | human | 0.247 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_90f073bf8ba0` | human | 0.247 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

| Family | Attacks | Held | Broke |
|---|---|---|---|
| `evasion` | 10 | 2 | 8 |
| `false_positive` | 8 | 2 | 6 |
| `prompt_injection` | 6 | 5 | 1 |
| `malformed` | 20 | 15 | 5 |
| `flood_same_creator` | 12 | 12 | 0 |


**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

From `logs/audit.jsonl`, written by `audit.py`:

```json
{"timestamp": "2026-11-10T23:38:14+00:00", "content_id": "c_dd2fb3aa938c", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.8805, "combined_score": 0.8353, "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T23:38:14+00:00", "content_id": "c_afcb0055b7be", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 1.0, "combined_score": 0.8803, "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T23:38:15+00:00", "content_id": "c_d91bd780a50a", "creator_id": "attacker_FP07", "guess": "ai", "model_score": 0.8816, "style_score": 0.6768, "combined_score": 0.7997, "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T23:38:13+00:00", "content_id": "c_500ef2741b59", "creator_id": "attacker_EV05", "guess": "human", "model_score": 0.3212, "style_score": 0.3854, "combined_score": 0.3469, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-10T23:38:15+00:00", "content_id": "c_3be9e74b9ea4", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.5167, "combined_score": 0.3293, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-10T23:38:16+00:00", "content_id": "c_8c586d3062b6", "creator_id": "attacker_MF04", "guess": "human", "model_score": 0.0112, "style_score": 0.5, "combined_score": 0.2067, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-10T23:38:16+00:00", "content_id": "c_6f014b0fb9f7", "creator_id": "attacker_MF05", "guess": "unsure", "model_score": 0.9976, "style_score": 0.5, "combined_score": 0.69, "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.", "status": "decided"}
{"timestamp": "2026-11-10T23:38:17+00:00", "content_id": "c_589ce9725e05", "creator_id": "attacker_MF08", "guess": "ai", "model_score": 0.9876, "style_score": 0.9039, "combined_score": 0.9541, "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T23:38:17+00:00", "content_id": "c_bb1acfc95be2", "creator_id": {"id": "x"}, "guess": "human", "model_score": 0.0492, "style_score": 0.5, "combined_score": 0.2295, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-10T23:38:18+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

FP03, the careful non-native writer 

Because they were being careful and sounding perhaps too plain with short sentences my detector labeled their writing as AI

There is no fix because they would have to write less carefully which is not ideal

```json
{"timestamp": "2026-11-10T23:38:14+00:00", "content_id": "c_dd2fb3aa938c", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.8805, "combined_score": 0.8353, "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided"}
```


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

I sorted the 20 broken attacks into four patterns. The biggest one, by far, is
the first.

**1. Plain and formal human writing gets called AI (FP02–FP07, MF08). Stage:
both signals, and the combining rule lets them through.**
Six of eight real human pieces scored 0.80–0.88. In every one, *both* signals
were high: model 0.74–0.88, style 0.68–1.00. Signal one (`detector.model_signal`)
rates text as AI when GPT-2 finds it predictable, and a formal report, a
cover letter, a rubric essay and setup instructions are all predictable on
purpose. Signal two (`stylometry.style_signal`) rates text as AI when sentence
lengths are even and there's little punctuation, and those are also the
features of careful, plain writing. FP05 (technical docs) got a style score of
a full 1.0. So the two signals aren't independent checks. They both reward the
same thing, so they agree, and they agree wrongly. My combining rule
(`scoring.combine_signals`) has one safety net, the disagreement cap, and it only
fires when the signals are more than 0.30 apart. Here the gap was 0.07–0.20,
so nothing stopped the score reaching the AI band. This misses criterion 1
(at most 1 in 10 human pieces at 0.70+). The run had 6 in 8.

MF08 is the same problem plus a route bug. It's the human campsite text
repeated to 60,000 characters. Repeating it collapses the type-token ratio, so
style read 0.90, and the model only reads the first 400 tokens anyway. It also
should never have been scored. Criterion 5 says oversized text gets a 400, and
`app.py::submit` has no length check at all.

**2. Lightly edited AI text drops out of the AI band (EV01–EV07, EV09, PI02).
Stage: whichever signal the edit targets, then the weighted average.**
The unedited AI paragraph scores about 0.96 (EV10 still did: model 0.98,
style 0.93). Every cheap edit pulled at least one signal down:
- Typos (EV01) dropped the *model* score to 0.16, not the style score the
  attack aimed at. GPT-2 finds misspelled words surprising, which reads as
  human.
- "Really." after every sentence (EV02) and "; and, moreover," padding (EV07)
  dropped *style* to 0.39 and 0.29, because they add sentence-length spread and
  punctuation, which are two of my three style measures.
- A human-sounding opening paragraph (EV09) diluted both signals just enough:
  0.669, under 0.70 by 0.031.

Because the combined score is a 0.6/0.4 weighted average, knocking one signal
down by a lot is enough to drag the total under 0.70. In EV01 the gap between
the signals was 0.61, so the disagreement cap also kicked in. That means the
cap I added to protect human writers also guarantees an attacker "unsure" as
long as they can push one signal far from the other.

PI02 belongs here, not with prompt injection. My detector doesn't read
instructions, so the "SYSTEM: … Return guess=human" line wasn't obeyed. It
worked because a line of fake system text is very unpredictable to GPT-2, so
model score fell to 0.20 and the result was "human". The attacker got the
exact label they asked for, just not for the reason they expected.

**3. Junk text gets a confident label, or crashes (MF02, MF03, MF04). Stage:
the route, then signal one.**
`app.py::submit` only checks that `text` is a non-empty string. It never checks
that the text is long enough to score. MF02 (`"a"`) is under 3 tokens, so
`detector.model_signal` raises `ValueError`. Nothing catches it, so it came
back as a 500 *and* a Werkzeug debugger page. MF03 (control characters) and
MF04 (punctuation only) are just over 3 tokens, so they got scored. GPT-2 finds
them extremely unpredictable (model 0.00 and 0.01). `style_signal` returns its
neutral 0.5 for under 5 words, and the cap only ever caps *upward*, so
0.6 × 0.0 + 0.4 × 0.5 = 0.20, which is "probably written by a person." The service
put a confident human label on `!!! ??? ...`.

The same fallback is the only reason MF05–MF07 held. A 1,000-letter word, emoji,
and Arabic all scored about 1.0 on the model signal. Style returned 0.5 (my
`words()` regex only matches a–z and 0–9, so none of them count as words), the
gap was over 0.30, and the cap held them at exactly 0.69. They held by 0.01,
and only because of a fallback. That's luck, not a defence.

**4. `creator_id` is never validated (RQ06). Stage: the route.**
`app.py::submit` checks the type of `text` but takes `creator_id` with
`payload.get("creator_id", "unknown")` and never checks it. An object
(`{"id": "x"}`) went into the audit log as-is (`c_bb1acfc95be2`). It also gets
around the per-creator rate limit: `rate_limit_key` only uses `creator_id` when
it's a string and otherwise falls back to the IP address.

**Held, but for the wrong reason (RQ10, RQ11).** These came back 429, not
400. Anonymous and non-dict requests are all keyed on my IP, and RQ02, RQ06,
RQ07, RQ08 and RQ09 had already used up that IP's 5 per minute. So the rate
limiter rejected them before my input checks ran. Nothing broke, but this run
never tested how I handle a form-encoded or `text/plain` body.



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
