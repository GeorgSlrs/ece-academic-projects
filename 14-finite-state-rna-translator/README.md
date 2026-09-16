# Finite-State RNA Translator

A computational-linguistics laboratory exercise representing RNA translation as a Mealy transducer in JFLAP. The machine reads the RNA alphabet (`A`, `U`, `C`, `G`), recognizes an `AUG` start sequence, and then uses states representing codon prefixes to emit amino-acid abbreviations.

The transition graph includes a stop state for stop codons. Outputs are attached to transitions, illustrating how a finite-state machine can translate an input sequence while keeping only the partial-codon context needed for the next step.

## Files and use

- [Q1.jff](Q1.jff) — the editable Mealy-machine project, saved by JFLAP 7.1.
- `CL_LAB4.pdf` / `.docx` — laboratory submission material.
- `project-files.zip` — archived project copy.

Open `Q1.jff` in JFLAP and inspect or step through its transitions with RNA strings. A Java runtime compatible with the JFLAP installation is required; there is no separate Python application or command-line pipeline.

This is a formal-language modelling exercise, not a biological sequence-analysis package. The graph is the primary artifact for understanding the encoded start, translation and stop behaviour.
