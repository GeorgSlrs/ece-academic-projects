# Python Programming Practice

Two collections of Python exercises trace the progression from input, variables and branching to functions, collections, files, recursion and object-oriented programs. The day-based practice folders retain their original names, including `Day 19`; [lessons/](lessons/) adds a separate set organized by course lesson.

## Lesson-based coursework

The [lesson guide](lessons/README.md) maps the course sequence: language fundamentals, strings and collections, functions and recursion, file/JSON handling, then classes, stacks, comparisons and operator overloading. `lesson16.exercise14` contains a multi-file turn-based battle exercise using `Character` and `Arena` classes. Local imports refer to neighboring lesson modules, so run each exercise from its own directory.

## What to explore

- Early folders: input/output, type conversion, conditionals and loops.
- [Day23](Day23/): small numerical exercises and a NumPy/Matplotlib plotting example.
- [Day28](Day28/): a character-fighting game exercise.
- [Day35](Day35/) and [Day45](Day45/): to-do-list revisions.
- [Day43](Day43/) and [Day46](Day46/): two-dimensional lists and dictionaries.
- [Day48](Day48/)–[Day51](Day51/): file writing/reading, score and idea storage, and calendar/to-do autosave/autoload experiments.

## Run individual scripts

Use Python 3 and run the chosen file from its day directory, for example:

```bash
python characters_fighting.py
```

Most scripts use only the standard library; `Day23/plottingwithpython.py` also needs NumPy and Matplotlib. Interactive exercises read from the terminal, and file exercises use relative paths and may create or replace local data files.

Some autoload exercises expect a previously created file such as `calendar.txt` or `to.do`, and use `eval` to read its contents. Keep those inputs local and trusted. These are learning-stage experiments with varying completeness, not a single maintained application.

The lesson archive also includes unfinished attempts and examples with syntax/runtime errors. Some external text/JSON inputs are omitted and need suitable sample replacements. Original comments and instructional attributions are retained; the collection does not claim sole authorship of every teaching example.
