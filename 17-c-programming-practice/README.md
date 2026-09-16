# C Programming Practice

A collection of independent C exercises documenting programming practice from basic input/output and control flow through pointers, dynamic allocation and data structures. Small practice programs are available directly in [C/](C/), while [coursework/](coursework/) contains five larger procedural-programming exercises.

## Course projects

The coursework folders cover menu-driven ASCII shapes, matrix/temperature evolution with extrema and histograms, text-file and dictionary processing, linked character-frequency records, and linked integer-list operations. Each contains its own `main.c`; see [the coursework guide](coursework/README.md) for the folder map and input requirements.

## Topics and examples

| Topic | Example files in `C/` |
| --- | --- |
| Arrays, searching and sorting | `binary_search.c`, `argc_argv_insertion_sort.c`, `sorting_algorithms.c`, `2d_array.c` |
| Pointers and allocation | `pointers1.c`, `pointers2.c`, `malloc.c`, `malloc2.c`, `memory_array_1.c` |
| Strings and memory operations | `strcpy.c`, `strcat.c`, `mystrcpy.c`, `memset.c` |
| Structured data | `struct_person.c` and its revisions, `struct_point_distance.c` |
| Recursion and command-line input | `fibonacci.c`, `argc_argv_insertion_sort.c` |

## Compile one exercise

Use a C compiler such as GCC, Clang or MSVC. For example, from `C/` with GCC:

```bash
gcc binary_search.c -o binary_search
```

Run the generated executable using the convention for your operating system. Follow [the collection guide](C/README.md) for additional examples.

Most exercises use the C standard library, but some retain compiler-specific functions or experimental code from the original learning environment. Compile and inspect files individually; they do not share a build system or a claim of uniform correctness.
