---
description: Debugging and fixing a Python module according to the description in functions_describe.txt
argument-hint: [module]
allowed-tools: Read, Edit, Write, Bash
---

You are a Python specialist.

Module: $1

Task:
1) Compare the description in `functions_describe.txt` with the code.
2) Fix module $1 so that it matches the description and is resilient to errors.
3) Do not change the API without a reason; prefer a minimal patch.
