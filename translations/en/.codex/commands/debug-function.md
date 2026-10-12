---
description: Debugging and fixing/adding a function in a Python module according to the description in functions_describe.txt
argument-hint: [module] [function_name]
allowed-tools: Read, Edit, Write, Bash
---

You are a Python specialist.

Module: $1
Function: $2

Project context is in `CODEX.md` (for Codex) / `KIMI.md` (for Kimi) and in `functions_describe.txt`.

Task:
1) Compare the description in `functions_describe.txt` with the implementation.
2) Fix/complete the function $2 in module $1 (minimally, without rewriting everything).
3) Add/fix tests where it makes sense.
