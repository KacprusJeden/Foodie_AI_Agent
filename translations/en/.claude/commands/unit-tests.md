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

Write unit tests using pytest for all methods of the module $1. Create a new file or overwrite it where needed to create a new test or to fix one you are correcting. You do not need to touch tests that are already written correctly.
