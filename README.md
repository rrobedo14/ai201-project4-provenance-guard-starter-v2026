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

A real writer submits a piece, maybe edits it and resubmits a few times. Five
a minute covers that, even with a couple of quick retries, and 50 a day is
more than anyone posting their own work would need. A script mapping my
thresholds needs hundreds or thousands of variations. At 5 a minute it gets
about one probe every 12 seconds, and at 50 a day it can't build up enough
data points to find the 0.35 and 0.70 lines in any useful time. A lower limit,
like 2 a minute, would start blocking a writer who fixes a typo and resubmits.
A higher one, like 20 a minute, would let a script map the bands in an
afternoon.

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

Per `creator_id`, falling back to IP address. `app.py::rate_limit_key` uses
`creator_id` when it's a non-empty string, and the caller's IP address
otherwise: when the body isn't JSON, has no `creator_id`, or the `creator_id`
isn't a string. The weak spot is that `creator_id` is whatever the caller
types, so one script can send a new `creator_id` with every request and look
like a thousand different writers, each with a fresh limit. The attack run
showed the other side of the fallback: RQ10 and RQ11 got 429s because earlier
anonymous requests had already used up my IP's 5 a minute.

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

From `logs/audit.jsonl`, written by `audit.py`. The first nine are from the
before run. The last one, a rate-limit rejection, is from the after run: in the
before run, rejections were only logged with six fields, which I fixed in
`audit.py::log_rejection` so they carry all nine.

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
{"timestamp": "2026-11-11T00:52:06+00:00", "content_id": null, "creator_id": "attacker_flood", "guess": null, "model_score": null, "style_score": null, "combined_score": null, "label": null, "status": "rejected", "event": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
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

From `results/run_2026-11-10_1928_before.md`, produced by `run_eval.py::main`
against `app.py::submit`. Criterion 4 can't be sent from `scenarios.py`, so I
tested it by hand (below the table).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives | ≤ 1 of 10 of my own pieces at 0.70+ | 4 of 10 | 4 of 10 | 4 of 10 | **MISSED** |
| 2. Score spread | AI avg ≥ 0.70, human avg ≤ 0.35, gap ≥ 0.35 | AI 0.781 / human 0.677 / gap 0.105 | AI 0.781 / human 0.677 / gap 0.105 | AI 0.781 / human 0.677 / gap 0.105 | **MISSED** |
| 3. Label coverage | each label ≥ 2 times in 15 inputs | human 4 · unsure 6 · AI 5 | human 4 · unsure 6 · AI 5 | human 4 · unsure 6 · AI 5 | **MET** |
| 4. Appeal path | 100% of valid appeals change status and get logged | 1 of 1 | 1 of 1 | 1 of 1 | **MET** (see note) |
| 5. Bad input | 100% of missing / empty / oversized text get a 400 | 4 of 5 (80%) | 4 of 5 (80%) | 4 of 5 (80%) | **MISSED** |

The three trials are identical to four decimal places. GPT-2 scoring with no
sampling is deterministic, so the repeats show the results are stable, not
that they vary.

**How I decided each verdict**
- **Criterion 1: MISSED.** I counted how many of my ten pieces scored 0.70 or
  higher in each trial. It was 4 every time, and the target allows at most 1,
  so all three trials fail. My ten pieces are four from an old use-case
  assignment, five short pieces I wrote fresh for this test, and my five "Why
  this target" sentences from `criteria.md`. Pieces 4, 8 and 9 scored exactly
  0.69. They count as passes, but only because the disagreement cap held them
  under the line.
- **Criterion 2: MISSED.** I averaged the combined score for each side in each
  trial. The AI side averaged 0.781, which passes its half. The human side
  averaged 0.677 against a target of 0.35 or lower, and the gap was 0.105
  against a target of 0.35, so it fails in all three trials. The AI side is ten
  paragraphs generated by Claude in the generic "several key strategies"
  register. The human side is the same ten pieces as criterion 1.
- **Criterion 3: MET.** I counted each label across the 15 inputs in each
  trial: 4 human, 6 unsure and 5 AI every time. Every label appears at least
  twice in all three trials. My criterion calls the labels `likely_ai` /
  `uncertain` / `likely_human`; the service returns `ai` / `unsure` / `human`.
  They're the same three labels with different names.
- **Criterion 4: MET.** I tested it by hand three times: `POST /submit`, then
  `POST /appeal` with the returned content_id, then `GET /log`. It passes if
  the appeal returns 200, the status changes, and an appeal entry appears in
  the log. All three did, so it holds 3 of 3. An unknown content_id correctly
  returns 404. My original criterion said the status becomes `"appealed"`,
  a status my service never uses (it sets `"under_review"`). I revised it in
  `criteria.md`, keeping the original line, because it measured the wrong
  thing. The verdict is against the revised line, and the target is still
  100%.
- **Criterion 5: MISSED.** I counted how many of the five bad bodies got a
  400. Missing text, null, empty and whitespace-only all did, but the
  ~60,000-character body got a 200 and was labelled AI at 0.998. That's 4 of 5
  (80%) in every trial against a target of 100%.

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

All of it is from trial 1 in `results/run_2026-11-10_1928_before.md`, written
by `run_eval.py::main` from responses returned by `app.py::submit` (scores from
`detector.model_signal`, `stylometry.style_signal` and
`scoring.combine_signals`). Trials 2 and 3 are identical. Criterion 4 is from
my hand test against `app.py::appeal` and `app.py::get_log`.

*Criterion 1: false positives.* Piece 7 (my "why computer science" paragraph)
was called AI. Piece 6 (my extension email) was not:

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8193,
    "model_score": 0.7217,
    "style_score": 0.9657,
    "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
    "sent": "I picked computer science because in high school I took a computer cla"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3607,
    "model_score": 0.2635,
    "style_score": 0.5066,
    "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
    "sent": "Hello this is Rogelio, I was emailing you regarding on an extension fo"
  }
]
```

*Criterion 2: score spread.* Two from the AI side: one labelled AI, one held at
0.69 by the disagreement cap.

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7819,
    "model_score": 0.8728,
    "style_score": 0.6455,
    "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
    "sent": "Effective leadership is essential for the success of any organization."
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.69,
    "model_score": 0.8537,
    "style_score": 0.4948,
    "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
    "sent": "A healthy diet is a fundamental component of overall well-being. Consu"
  }
]
```

Two from the human side (my own writing): my login/register piece called AI,
and my criteria "why" sentences, which were not.

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8227,
    "model_score": 0.7212,
    "style_score": 0.975,
    "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
    "sent": "Registering a user for access to the application using the proper form"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4896,
    "model_score": 0.2182,
    "style_score": 0.8968,
    "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
    "sent": "I allow at most 1 false positive in 10 because on a publishing platfor"
  }
]
```

*Criterion 3: label coverage.* One input from each band. All three labels
appear.

```json
[
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.309,
    "model_score": 0.4445,
    "style_score": 0.1058,
    "label": "We think this was probably written by a person.",
    "sent": "I didn't sleep. Not properly, anyway — I lay there listening to the bo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.412,
    "model_score": 0.3489,
    "style_score": 0.5066,
    "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
    "sent": "Time management matters more than people admit, especially now that wo"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9594,
    "model_score": 0.9792,
    "style_score": 0.9296,
    "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
    "sent": "The importance of effective communication in the workplace cannot be o"
  }
]
```

*Criterion 4: appeal path.* The `/appeal` response, then the log entry it wrote
(from `GET /log`):

```json
{"content_id": "c_890eed53ed90", "message": "Your appeal has been received. A person will review this decision, and the original label is now marked as under review.", "status": "under_review"}
{"content_id": "c_890eed53ed90", "creator_id": "eval_appeal_1", "event": "appeal", "reasoning": "I wrote this myself.", "status": "under_review", "timestamp": "2026-11-11T00:28:55+00:00"}
```

*Criterion 5: bad input.* A missing text field got a 400. The ~60,000-character
body got a 200:

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_bad_missing\"}"
  }
]
```

```json
{
  "status": 200,
  "guess": "ai",
  "confidence": 0.9981,
  "model_score": 0.9969,
  "style_score": 1.0,
  "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
  "sent": "We got to the campsite about four and the pitch was fine. We got to th"
}
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
Stage: signal one or signal two (whichever the edit hits), then the combining
rule.**
The unedited AI paragraph scores about 0.96 (EV10 still did: model 0.98,
style 0.93). Every cheap edit pulled at least one signal down:
- Typos (EV01) dropped the *model* score to 0.16, not the style score the
  attack aimed at. GPT-2 finds misspelled words surprising, which reads as
  human.
- "Really." after every sentence (EV02) and "; and, moreover," padding (EV07)
  dropped *style* to 0.39 and 0.29, because they add sentence-length spread and
  punctuation, which are two of my three style measures.
- Swapping in rare words like "efficacious" and "desiderata" (EV04) did what it
  aimed at: GPT-2 finds them unpredictable, so the model score fell to 0.61.
- One very long sentence next to one very short one (EV06) raised
  sentence-length spread, so style fell to 0.43.
- A pasted quotation (EV03) changed the text's shape and lowered both signals a
  little (model 0.67, style 0.55). That was enough on its own: 0.618.
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

**Criterion misses from the run log**

**Criterion 1 missed (4 of 10). Stage: signal two, the whole signal
saturating.** Three misses are spec-style assignment writing, the
same mechanism as FP02–FP07 above. Piece 7 is the new finding. It's casual,
has typos, and is clearly personal, and it still scored 0.82 with a style
score of 0.97. My writing uses long run-on sentences with very few commas or
dashes. `punctuation_density` counts commas, dashes, colons and brackets per
word and treats *few* as machine-like. AI text is low on them because it's
tidy. My writing is low on them because I under-punctuate. The measure can't
tell the two apart. And it isn't only punctuation. When I broke the style
score down, sentence spread and word variety also scored 0.85–1.0 "AI" on
almost every piece. The scaling ranges in `stylometry.style_signal` were
set from a handful of sample files and are too narrow, so ordinary writing
pins all three measures at the top. Every one of my ten pieces had a style score of 0.83–1.0
except the one-sentence email, where the style signal falls back to neutral.
The model signal on my four flagged pieces was only moderate (0.70–0.72), so
signal two is what pushed them over.

**Criterion 2 missed (gap 0.105, needs 0.35). Stage: signal two, then the
combining rule.** The AI side passed with an average of 0.781. The human side
averaged 0.677, nowhere near 0.35, because it's the same ten pieces as
criterion 1, so the same style-signal problem applies. There's a second,
smaller cause in the combining rule: two of the ten AI paragraphs scored
exactly 0.69 because the disagreement cap pulled them down. The cap only ever
lowers scores, never raises them, so it shrinks the gap from the AI side.

**Criterion 5 missed (80%). Stage: the route.** `app.py::submit` checks that
`text` is a non-empty string and nothing else. There is no maximum length, so
60,000 characters went straight to the detector. GPT-2 only reads the first
400 tokens (`DETECTOR_MAX_TOKENS`), and the text is one sentence repeated, so
it scored 0.998 AI. This is the same gap as MF08 in the attack run.

**The pattern across everything that failed**

The 20 broken attacks and 3 missed criteria come down to three problems, not
23.

1. **Signal two can't tell plain human writing from AI writing.** It is behind
   FP02–FP07, MF08, criterion 1 and criterion 2. My style signal scores three
   things: even sentence lengths, little punctuation, and repeated words. Plain
   human writing has all three, whether it's a formal report, a non-native
   speaker writing carefully, or my own run-on sentences. Signal one reads the
   same texts as predictable, so the two signals agree. That means the
   disagreement cap, my only safeguard in the combining rule, never fires on
   exactly the texts it was meant to protect.
2. **The combining rule lets one moved signal decide the result.** It is
   behind EV01–EV07, EV09 and PI02. Each attack pushed one signal down: style
   for EV02, EV06 and EV07, and the model signal for EV01, EV04 and PI02. A
   0.6/0.4 weighted average with no floor means one signal moving far enough
   drags the total under 0.70. If the two signals end up more than 0.30 apart,
   the disagreement cap guarantees "unsure" anyway. The cap is meant to
   protect writers, and it protects attackers just as well.
3. **The route doesn't validate input before scoring it.** It is behind MF02,
   MF03, MF04, MF08, RQ06 and criterion 5. `app.py::submit` checks one thing,
   that `text` is a non-empty string. It never checks that the text is long
   enough to score, short enough to be reasonable, or that `creator_id` is a
   string. Everything the route lets through gets scored, and a score on junk
   text is a confident label on nothing.

The label mapping (`scoring.score_to_label`) didn't cause any failure. Every
wrong label came from a wrong score upstream.



---

## The Improvement

**What I changed:**

One setting in `config.py`, used by `scoring.py::combine_signals`:
`WEIGHT_MODEL_SIGNAL` went from **0.6 to 0.8**, and `WEIGHT_STYLE_SIGNAL` from
**0.4 to 0.2**. Signal two now counts half as much. Thresholds (0.35 / 0.70),
the disagreement gap (0.30) and the route are unchanged, so any difference in
the after run comes from the weights alone.

**Which diagnosis pointed at it:**

Pattern 1 and the criterion 1 and 2 diagnoses: signal two can't tell plain
human writing from AI writing. On my own pieces, all three style measures
(sentence spread, punctuation, word variety) scored 0.85–1.0 "AI" on almost
every piece, so the style score sat at 0.83–1.0 whatever I wrote. If one
signal is saturated, the fix that follows is to let it count less.

Before changing anything, I replayed my recorded scores through every weighting
from 0.6/0.4 to 1.0/0.0. None of them got criterion 1 under 2 of 10. Even with
the style signal switched off entirely, 3 of my 10 pieces stay above 0.70,
because signal one also scores them 0.70–0.72. I chose 0.8/0.2 anyway because
it was the best trade for criterion 2: it widens the gap without throwing signal
two away. I went in expecting criterion 1 not to move.

### Attack Run — After

From `results/attack_run_2026-11-10_1952_after.md`, produced by
`run_attacks.py::main` against `app.py::submit` with the new weights. Verdicts
use the same rules as the before run. **20 broke, 36 held, the same as
before.**

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_ec08191ae0b2` | human | 0.285 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_7eede6d6690d` | unsure | 0.554 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_f7c801ceb038` | unsure | 0.642 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_30e40ff06023` | unsure | 0.633 | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_41652478cf19` | human | 0.334 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_97fee1cf085e` | unsure | 0.544 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_fa2ba1426f96` | unsure | 0.526 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | `c_4f2d0e3f5f0c` | unsure | 0.356 | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_0dcc93bc8a3d` | unsure | 0.686 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_83e6b2cc7d31` | ai | 0.969 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_12dc18b45850` | unsure | 0.653 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `c_38f47177de1f` | ai | 0.773 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_ddc0675520d0` | ai | 0.820 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_5a7d6445a528` | ai | 0.823 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_844a9dad9b68` | ai | 0.840 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_6e617d00cbaa` | ai | 0.851 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_34d694cb58b8` | ai | 0.841 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `c_5a672b64c99c` | unsure | 0.398 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_8630ed59feb1` | unsure | 0.476 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_839d2ea94289` | human | 0.267 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_882dab45a3f6` | unsure | 0.616 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_1b2570d096a9` | unsure | 0.512 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_85a582101439` | unsure | 0.576 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_c3c3e62eccaf` | unsure | 0.608 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 500 | `—` | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | `c_bda4941f8547` | human | 0.100 | BROKE |
| MF04 | malformed | text is only punctuation | 200 | `c_66565bc550d9` | human | 0.109 | BROKE |
| MF05 | malformed | text is a very long single word | 200 | `c_75258ca4dc4f` | unsure | 0.690 | HELD |
| MF06 | malformed | text is emoji only | 200 | `c_76f9b685aeb0` | unsure | 0.690 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `c_637ed64b4451` | unsure | 0.690 | HELD |
| MF08 | malformed | text is 60,000 characters | 200 | `c_46ae290f3873` | ai | 0.971 | BROKE |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `c_074ed6878d55` | human | 0.307 | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 200 | `c_026643dd240f` | human | 0.139 | BROKE |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_24be0370f3f8` | human | 0.138 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_c38f0820f774` | human | 0.138 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_4a4e21f96305` | human | 0.138 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_028a34c2e358` | human | 0.138 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_ab22190aa97a` | human | 0.138 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

Only two attacks changed label, and neither changed verdict:

| Attack | Before | After | Verdict |
|---|---|---|---|
| EV01 (typos) | unsure 0.406 | **human** 0.285 | BROKE → BROKE, now worse |
| RQ02 (no creator_id) | unsure 0.374 | human 0.307 | HELD → HELD |

EV01 got *worse*. Its typos had already pushed signal one down to 0.16, and
the high style score (0.77) was the only thing holding it in "unsure". With
style at 0.2, that brake is mostly gone, and the typo'd AI text now gets a
confident "probably written by a person."

**Did it help, and how do I know:**

Partly. It helped criterion 2, did nothing for criterion 1, and made one
evasion worse. From `results/run_2026-11-10_1951_after.md` (3 trials,
identical again):

| Criterion | Before | After | Verdict |
|---|---|---|---|
| 1. False positives (≤ 1 of 10) | 4 of 10 | 4 of 10 | MISSED → MISSED |
| 2. Score spread (gap ≥ 0.35) | AI 0.781 / human 0.677 / gap 0.104 | AI 0.801 / human 0.629 / gap **0.172** | MISSED → MISSED |
| 3. Label coverage (each ≥ 2) | human 4 · unsure 6 · AI 5 | human 3 · unsure 7 · AI 5 | MET → MET |
| 4. Appeal path | 3 of 3 | not rerun (weights don't touch `/appeal`) | MET |
| 5. Bad input (100% → 400) | 4 of 5 | 4 of 5 | MISSED → MISSED |

What it fixed:
- **The gap in criterion 2 grew by 65%** (0.104 → 0.172). Human scores came
  down (0.677 → 0.629) and AI scores went up (0.781 → 0.801), because a
  saturated signal was pulling both towards the same number. It's still about
  half the 0.35 target.
- **Every one of my ten pieces scored lower or the same.** My extension email
  moved from unsure to human, and my criteria sentences went from 0.490 to
  0.354, just above the human line.

What it didn't fix:
- **Criterion 1 stayed at 4 of 10.** My four flagged pieces dropped by 0.02–0.05
  but stayed above 0.70 (0.729–0.772). Signal one scores them 0.70–0.72 on its
  own, so no weighting gets them out. This is the part of my diagnosis I had
  wrong at first: I treated it as a signal two problem only, and it's both.
- **The false-positive attacks stayed at 6 of 8, and three got worse.** FP02,
  FP03 and FP05 dropped a little (FP03, my worst outcome, went 0.835 → 0.820)
  but stayed above 0.70. FP04, FP06 and FP07 went *up* (FP07 0.800 → 0.841),
  because for those texts the model score is higher than the style score, so
  giving the model more weight pushes them further into the AI band.

What it cost:
- **EV01 went from unsure to human.** Turning signal two down means signal one
  decides more on its own, and signal one is the one that typos fool.
- **One genuinely human sample lost its human label.** `samples/clearly_human.json`
  (the "I didn't sleep" piece) went from human 0.309 to unsure 0.377. Its
  style score was very human (0.11), and that now counts for less. A writer
  whose *style* is clearly human gets less credit for it.

How I know: the before and after runs use the same inputs and the same
`scenarios.py`, and the only change between them was the two weights.
Both runs were identical across all three trials, so the differences above
come from the change, not from noise.

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

After the reweight, 20 attacks still break and criteria 1, 2 and 5 still
miss. They fall into the same three problems as the diagnosis, so I've
grouped them that way.

**1. Real writers still get called AI: FP02–FP07, criterion 1 (4 of 10) and
criterion 2 (gap 0.172).**
- *What I'd do:* raise `AI_THRESHOLD` from 0.70 to 0.85. Replaying my recorded
  scores, that takes criterion 1 from 4 of 10 to 0 of 10, and the
  false-positive attacks from 6 of 8 to 1 of 8. The longer-term fix is to
  re-scale `stylometry.style_signal` on a much bigger set of human writing, so
  plain writing stops pinning all three measures at the top. For criterion 2,
  the threshold won't help, because averages don't move when a threshold does.
  Only better signals will close that gap.
- *Why I stopped:* the brief allowed one improvement, and I chose reweighting.
  The threshold change also has a big cost I haven't tested in a real run: in
  the replay, 9 of my 10 AI paragraphs drop to "unsure" as well. Re-scaling
  the style signal properly needs far more human samples than the ten I have.

**2. Edited AI text still gets through: EV01–EV07, EV09 and PI02.**
- *What I'd do:* stop letting one signal decide on its own. Right now a
  0.6/0.4 (now 0.8/0.2) weighted average means pushing one signal far enough
  drags the total down. I'd add a rule that a very low score on one signal
  can't produce "human" unless the other signal agrees, so a split lands in
  "unsure" in both directions, not just the AI one. Typos and fake system lines
  fool signal one, so I'd also strip or flag text with a high rate of
  misspellings before scoring.
- *Why I stopped:* every evasion fix makes the detector stricter, and stricter
  means more real writers get flagged. My criteria say a wrong accusation
  costs more than a missed detection, so I fixed false positives first. My
  reweight also made EV01 worse (unsure → human), which is a sign this needs a
  rule, not another weighting.

**3. The route still scores input it shouldn't: MF02, MF03, MF04, MF08, RQ06
and criterion 5 (4 of 5).**
- *What I'd do:* validate in `app.py::submit` before either signal runs.
  - Require at least 5 real words, which rejects MF02 (`"a"`), MF03 (control
    characters) and MF04 (punctuation only).
  - Reject text over about 10,000 characters, which fixes MF08 and criterion 5.
  - Reject a `creator_id` that isn't a string, which fixes RQ06.
  - Catch `ValueError` from the detector, so nothing can turn into a 500 again.
  All of these return a 400 and get logged as rejections.
- *Why I stopped:* this is the easiest fix on the list, but it wasn't the one
  my biggest diagnosis pointed at, and I could only make one change. One
  trade-off to settle first: a 5-word minimum would also reject the emoji and
  Arabic inputs (MF06, MF07). They only "held" by luck at 0.69, but a clear 400
  is still a worse experience for a real Arabic writer than an honest "we can't
  check this language."

**Held only by luck: MF05, MF06, MF07.** These scored exactly 0.69 because the
style signal fell back to 0.5 and the disagreement cap held them under the AI
line. They count as held, but nothing in my service actually handles them.
Input validation (problem 3) is the real fix.

**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

I'd raise the AI threshold to 0.85, so far fewer real writers get accused,
including people like FP03, a non-native writer who did nothing wrong. The cost
is that most AI text would be labelled "unsure" instead of "AI", and the people
who pay for that are honest writers and readers on the platform, who end up
sharing it with AI-written work the system won't name.


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
