## Grade-agnostic rubric (applies to every K1-K12 template)

These are the items every grade shares. Twelve items, all binary. Each comes with a one-sentence "what to look for" prompt designed for a 4B vision LM to interpret. Numbered for easy reference in the JSON output schema.

**Engine and rendering integrity**

1. **No template-engine leakage.** The rendered output contains no literal `{{ var }}`, `[a|b|c]`, `{% ... %}`, `<auto>`, or other un-substituted template syntax.
   *Look for:* curly braces, square brackets with pipes, `<auto>` placeholders, percent-brace blocks anywhere in the visible prose.

2. **No filler boilerplate.** The rendered prose does not contain redundant filler phrases like "Please solve this problem" tacked onto a question that's already a question.
   *Look for:* sentences that don't add information and feel like template padding rather than problem content.

3. **Answer matches the question's form.** The fixture answer matches the form the question asks for. If the question asks "how many days?" the answer should be an integer (or "7 days"), not a tuple. If the question asks "which is taller?" the answer should be one of the two options, not a number.
   *Look for:* unit/form mismatches between what's asked and what's in the `Answer:` field of the rendered output.

**Prose coherence**

4. **Subject-verb and article agreement.** Prose obeys English grammar: "an eraser" not "a eraser", "each carton costs" not "each cartons costs", subjects and verbs agree in number.
   *Look for:* article-before-vowel violations, singular/plural mismatches, subject-verb disagreement.

5. **Pronoun consistency.** Pronouns (he/she/they/it) used in prose are consistent with the named subject and consistent across sentences. A character introduced as "Duane" should not be referred to as "they" in the next sentence (unless the template is explicitly using singular-they consistently).
   *Look for:* a named character followed by mismatched or inconsistent pronouns later in the prose.

6. **Entity consistency across sentences.** Entities mentioned in setup ("blocks of cheese and tomatoes") match entities priced or referenced later ("each cheese block costs X, each tomato costs Y"). If the prose introduces items A and B, the math should be about A and B, not about C.
   *Look for:* lists of items in setup that don't appear in pricing/quantity sentences, or pricing for items never mentioned.

**Pedagogical sanity**

7. **Not a tautology.** The prose does not state the answer. If the question is "how many clips long is the eraser?" the prose should not literally say "the eraser is 5 clips long" earlier.
   *Look for:* the answer value or its direct equivalent appearing in the setup prose.

8. **Not a single-fact recall** (unless the template's declared family explicitly tests recall). The problem requires at least one operation, comparison, or transformation, not just retrieval of a definitional fact like "how many days in a week."
   *Look for:* questions answerable purely from a definition or convention with no problem-context computation.

9. **Skill category matches declared topic.** The cognitive work the problem requires aligns with the topic field in the YAML. A template under `measurement.length` should be testing length-measurement, not language-comprehension-of-comparative-adjectives.
   *Look for:* mismatch between what `metadata.topic` claims and what the prose actually requires the student to do.

**Output integrity**

10. **Math-prose-answer triangle.** The displayed answer is consistent with the prose setup. If the prose says "buy 4 of each" and items cost $6.75 and $4.25, the answer should be $44, not $5 or $(6, 5).
    *Look for:* answers that don't plausibly result from the operations the prose describes — even without re-deriving, "is the order of magnitude right?" catches most errors.

11. **No unrendered placeholders or N/A values.** Rendered output contains no "None", "null", "undefined", "N/A" strings where a real value should be.
    *Look for:* literal None/null/undefined in the prose or answer.

12. **Visual integrity (if visual block present).** If the template renders a figure, the figure has no overlapping labels, no labels going off-canvas, no markers placed inconsistently with their data, and no obvious geometric impossibilities.
    *Look for:* labels stacked on each other, labels cropped at the edge, points/markers floating in empty space without leader lines, schematics that contradict their labels (closed circuit labeled "open", etc.).

**Output schema for items 1-12:**

```json
{
  "template_id": "k1_easy_measurement_clips_03",
  "agnostic": [
    {"id": 1, "pass": true,  "note": ""},
    {"id": 2, "pass": false, "note": "Contains 'Please solve this problem' as filler."},
    {"id": 3, "pass": true,  "note": ""},
    {"id": 4, "pass": false, "note": "'a eraser' should be 'an eraser'."},
    ...
  ]
}
```

Each item needs `pass: bool` and `note: string` (one sentence, explaining the failure if `pass: false`, empty if `pass: true`). The note field is what lets you debug the grader — if it consistently fails on item 4 with notes about things that aren't grammar issues, you know the model is misunderstanding the rubric.

---

## K1-specific rubric

K1 has the visual-and-numeral-heavy character we discussed. These items apply *in addition to* the agnostic set. Eight items.

**Visual primacy**

K1.1. **Visual block present.** The template has a `visual:` block with a rendered figure. Pure-prose K1 problems are categorically suspect because most K1 skills are picture-anchored.
*Look for:* presence of an image alongside the prose. Pass = image present.

K1.2. **Visual is load-bearing or prose is sufficient.** Either the figure carries information needed to solve (the canonical K1 case: "count the apples in this picture"), OR the prose alone fully specifies the problem AND the figure illustrates appropriately. The figure should not be cosmetic-only when the topic is something like measurement-with-non-standard-units, where the picture is the whole skill.
*Look for:* topics like `measurement.length`, `numbers.counting`, `geometry.shapes` where the figure is the primary information source. If the figure is missing or merely decorative for these topics, fail.

K1.3. **Visual matches prose.** If the prose says "5 clips" and the figure shows clips, the figure should show 5 clips. Visual quantity matches stated quantity.
*Look for:* mismatches between numerical values stated in prose and quantities shown in the figure.

**Prose constraints**

K1.4. **Prose is brief.** The full problem prose (excluding the answer) is under approximately 25 words. K1 students cannot parse long multi-sentence narratives.
*Look for:* word count of the rendered problem prose. Pass = ≤25 words. Fail = >25 words.

K1.5. **Concrete, age-appropriate nouns.** Entities are concrete, physically-present-in-a-K1-classroom-or-home objects (apples, ducks, blocks, clips, pencils, animals, shapes). Not abstract concepts (investments, rates, percentages, equations).
*Look for:* the nouns in the prose. Pass = all nouns are concrete and age-appropriate. Fail = abstract or age-inappropriate nouns present.

K1.6. **Single-step task.** The problem requires one operation or one observation, not a chain of reasoning. K1 students do not yet do multi-step word problems.
*Look for:* number of distinct operations the student must perform. Pass = single observation/operation. Fail = explicit multi-step chain.

**Numeracy form**

K1.7. **Numerals are within K1 range.** All numerals shown are within roughly 0-20 (the standard K1 numerical range; some curricula extend to 100 for counting). No fractions, no decimals, no negative numbers.
*Look for:* any numbers > 20 (warn-not-fail at >20, hard-fail at >100), any fraction notation, any decimal points, any negative signs.

K1.8. **Answer is a small whole number, a single word, or a simple shape name.** K1 answers are categorically simple: a count (3), a comparison ("taller"), a shape name ("circle"), a position ("on top"). Not tuples, not decimals, not algebraic expressions.
*Look for:* the form of the rendered answer. Pass = single number ≤20, single word, or simple noun. Fail = tuple, decimal, fraction, multi-word phrase that's actually multi-part.
