# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-10 19:52
- Auto-marked BROKE (5xx, crash, no response): **1**
- Left for you to judge: **55**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

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

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 1 | 19 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_ec08191ae0b2",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.2846,
  "model_score": 0.1635,
  "style_score": 0.7691,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_7eede6d6690d",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.5537,
  "model_score": 0.5943,
  "style_score": 0.3915,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_f7c801ceb038",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.6421,
  "model_score": 0.6662,
  "style_score": 0.5456,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_30e40ff06023",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.6332,
  "model_score": 0.6114,
  "style_score": 0.7206,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_41652478cf19",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.334,
  "model_score": 0.3212,
  "style_score": 0.3854,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_97fee1cf085e",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.5442,
  "model_score": 0.5727,
  "style_score": 0.43,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c_fa2ba1426f96",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5262,
  "model_score": 0.5862,
  "style_score": 0.2864,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c_4f2d0e3f5f0c",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.3562,
  "model_score": 0.2452,
  "style_score": 0.8,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_0dcc93bc8a3d",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.6864,
  "model_score": 0.7042,
  "style_score": 0.6154,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_83e6b2cc7d31",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.9693,
  "model_score": 0.9792,
  "style_score": 0.9296,
  "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": "HELD"
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_12dc18b45850",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.653,
  "model_score": 0.6175,
  "style_score": 0.7949,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_38f47177de1f",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.7733,
  "model_score": 0.7387,
  "style_score": 0.9116,
  "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_ddc0675520d0",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.8202,
  "model_score": 0.8051,
  "style_score": 0.8805,
  "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_5a7d6445a528",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.8229,
  "model_score": 0.8329,
  "style_score": 0.7829,
  "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_844a9dad9b68",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.8404,
  "model_score": 0.8005,
  "style_score": 1.0,
  "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_6e617d00cbaa",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.8507,
  "model_score": 0.8814,
  "style_score": 0.7281,
  "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_34d694cb58b8",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.8406,
  "model_score": 0.8816,
  "style_score": 0.6768,
  "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c_5a672b64c99c",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.3979,
  "model_score": 0.3223,
  "style_score": 0.7002,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_8630ed59feb1",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.4756,
  "model_score": 0.4625,
  "style_score": 0.528,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_839d2ea94289",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.2669,
  "model_score": 0.2044,
  "style_score": 0.5167,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_882dab45a3f6",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.6163,
  "model_score": 0.5943,
  "style_score": 0.7041,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_1b2570d096a9",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.5117,
  "model_score": 0.4998,
  "style_score": 0.5593,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_85a582101439",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.5764,
  "model_score": 0.6401,
  "style_score": 0.3214,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_c3c3e62eccaf",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.6076,
  "model_score": 0.5583,
  "style_score": 0.8046,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 500,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>ValueError: Text is too short to score \u2014 a few sentences at least.\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes&a",
  "verdict": "BROKE"
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "c_bda4941f8547",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.1,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "c_66565bc550d9",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.109,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "c_75258ca4dc4f",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.69,
  "model_score": 0.9976,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "c_76f9b685aeb0",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.69,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "c_637ed64b4451",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.69,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with help from AI. This is not an accusation. Lots of human writing ends up here, especially writing that is plain and simple.",
  "error": null,
  "verdict": "HELD"
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "c_46ae290f3873",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.9709,
  "model_score": 0.9876,
  "style_score": 0.9039,
  "label": "We think this was probably written with AI. Our checks can be wrong, especially with plain or simple writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": "BROKE"
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "c_074ed6878d55",
  "creator_id": null,
  "guess": "human",
  "confidence": 0.3066,
  "model_score": 0.2395,
  "style_score": 0.575,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 200,
  "content_id": "c_026643dd240f",
  "creator_id": {
    "id": "x"
  },
  "guess": "human",
  "confidence": 0.1394,
  "model_score": 0.0492,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "c_24be0370f3f8",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.138,
  "model_score": 0.0287,
  "style_score": 0.575,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "c_c38f0820f774",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.138,
  "model_score": 0.0287,
  "style_score": 0.575,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "c_4a4e21f96305",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.138,
  "model_score": 0.0287,
  "style_score": 0.575,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "c_028a34c2e358",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.138,
  "model_score": 0.0287,
  "style_score": 0.575,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c_ab22190aa97a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.138,
  "model_score": 0.0287,
  "style_score": 0.575,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```
