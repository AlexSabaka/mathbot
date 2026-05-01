Got it. Let me draft two rubric sets — grade-agnostic and K1-specific — designed to be small enough that a 2-4B local model can actually grade against them reliably.

Before I write them, two design constraints I want to flag because they shape what the rubrics look like:

**Small models grade better with binary items than scaled items.** "Score 1-5 for prose quality" is a vague task that produces inconsistent scores across runs. "Does the prose contain literal `{{ var }}` or `[a|b]` syntax? Yes/No" is a sharp task that produces stable scores. So I'm going to write nearly everything as Yes/No with a one-sentence justification field. If you want a scaled overall score later, derive it from the binary items.

**Each rubric item should be answerable from (rendered text + rendered image + minimal YAML). Not from running the math.** A 4B model can't reliably re-derive 4 × $6.75 + 4 × $4.25 = $44, but it *can* check whether the answer fixture matches the answer shown in the image, and whether the items mentioned in prose match the items priced. Math correctness needs to come from `mathbot test` (which already runs), not from the grader. The grader is for things `mathbot test` can't see — visual quality, prose coherence, pedagogical fit.

## Prompt structure

```plain
You are grading a K1 math problem template against a strict rubric.

You will see:
1. The rendered problem prose (text)
2. The rendered figure (image, if present)
3. The fixture answer

Apply each rubric item below. For each, output JSON: {"id": N, "pass": bool, "note": "one sentence"}.

If the item's criterion is met, pass = true and note = "".
If the criterion is violated, pass = false and note explains why in ≤15 words.

Rubric items:
[paste items 1-12 + grade specific items here]

Rendered prose:
[prose]

Fixture answer:
[answer]

Output a single JSON object with key "items" containing the array. No prose, no markdown.
```

Strict JSON output, low temperature (0.0 or 0.1), and post-validation against a JSON schema. Reject and retry on schema violation.
