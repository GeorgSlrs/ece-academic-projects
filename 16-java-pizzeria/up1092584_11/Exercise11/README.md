# Java Exercise 11 — Pizzeria / Order Processing

## What this assignment covers
A Java desktop coursework project modelling pizzeria order processing with multiple scheduling strategies, a GUI, threads, enums and file output.

## Source structure
- `src/mainPacket/MainClass.java` — application entry point; creates the main GUI frame.
- `src/GUI/GeneralFrame.java` — Swing/AWT GUI.
- `src/Pizzeria/` — FIFO, profit-oriented and random scheduling implementations.
- `src/orderPacket/OrderClass.java` — order model.
- `src/threads/` — worker/thread classes for scheduling modes.
- `src/enums/` — order/location enums.
- `src/writeToFile/` — output helper.
- `../JavaExercise11-ClassDiagram.pdf` — class diagram.
- `../usecase_java11.pdf` — use-case documentation.

## Requirements
- JDK 8+; a modern JDK such as 17 or 21 is preferable.
- No third-party Java library is evident in the source.
- The `.settings/` directory comes from Eclipse; Eclipse is optional.

## Run
The simplest route is to import/open `Exercise11` as a Java project in Eclipse/IntelliJ and run:

`mainPacket.MainClass`

From the command line you can also compile the package tree into a build directory, then run the fully qualified main class.

## Notes
The source is preserved as coursework, including informal comments and historical implementation choices. This is academic coursework; see the repository-level authorship note for context.
