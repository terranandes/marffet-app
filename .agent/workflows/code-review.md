---
description: execute code-review
---

# /code-review - review the code

$ARGUMENTS

---

## Purpose
Based on $ARGUMENTS,
[CV] conduct a detailed code review using
skill `requesting-code-review` to execute the code-review.
Other agents [CODE]/[UI], use skill 'receiving-code-review' to respond the feedbacks from [CV].
[PL] use skill `code-review-checklist` to conclude the code-review, and conclude the review at `./docs/code_review`.