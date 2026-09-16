# Python Programming Lessons

Lesson-organized exercises covering Python fundamentals, collections, functions, file handling, recursion, and object-oriented programming. This collection complements the separate `Day*` practice folders in the parent directory.

## Contents

| Folders | Topics and examples |
| --- | --- |
| `lesson02`–`lesson08` | Types, arithmetic, input, conditions, loops, and random values |
| `lesson09`–`lesson11` | String operations and collection exercises |
| `lesson12`–`lesson14` | Functions, argument passing, recursion, binary search, and modules |
| `lesson15` | Text/binary files, JSON, and small menu-driven exercises |
| `lesson16`, `lesson17` | Classes, instance methods, stacks, comparisons, and operator overloading |
| `lesson16.exercise14` | A multi-file turn-based battle exercise using `Character` and `Arena` classes |
| `dictionary_reference.py` | Examples of common dictionary methods |

## Use

Use Python 3 and run one exercise from its own directory. Most examples use the standard library; imports such as `module`, `stack`, and `character` refer to neighboring lesson files.

```bash
cd lesson17
python exercise1.py
```

The battle exercise starts with `python main.py` from `lesson16.exercise14`.

This is an archive of learning exercises, including unfinished attempts and examples of invalid syntax or runtime errors. It is not a single application or a passing test suite. Some exercises prompt for input, loop until interrupted, or write files into the current directory. Keep a disposable working copy when experimenting. JSON records containing people or login data and generated file outputs are omitted; exercises that read those records or external text files need suitable sample inputs. The login examples demonstrate elementary file handling, not secure authentication.

Original filenames and source comments are retained. The collection records coursework and practice; it does not assert sole authorship of every instructional example.

Static parsing found one invalid-syntax example: `lesson13/positional.after.keyword.args.py` passes a positional argument after keyword arguments. It is retained as a learning example and cannot be executed as written.
