---
description: Debugging and fixing/adding functions in a Python module according to the description in functions_describe.txt
argument-hint: [module] [function_name]
allowed-tools: Bash, Write, Read, Edit
---

You are a Python programming specialist. Your task is to complete the job according to the given instructions.

## Task to perform

Module: $1

The CLAUDE.md file contains the project structure and what it is specifically about, what it returns, etc.
The functions_describe.txt file contains the description of this function. Compare the description of this function with the actual implementation.

Write a corrected version of the module $1 FROM SCRATCH. Debug it and check whether it could potentially raise Python or other errors.
If you need to add any helper function, document it in the same style as in functions_describe.txt.
