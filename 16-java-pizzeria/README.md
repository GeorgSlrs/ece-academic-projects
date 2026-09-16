# Java Pizzeria / Order Processing Coursework

A Java desktop coursework project modelling pizzeria orders and comparing FIFO, random and profit-oriented processing strategies. The source explores object-oriented design, a Swing/AWT interface, worker threads, enums and file output.

## Source map

The main project is [up1092584_11/Exercise11/](up1092584_11/Exercise11/), whose README provides a more detailed guide.

- `src/mainPacket/MainClass.java` — entry point that constructs the main GUI.
- `src/GUI/` — application interface.
- `src/orderPacket/` — order representation.
- `src/Pizzeria/` — processing/scheduling strategies.
- `src/threads/` — associated worker classes.
- `src/enums/`, `src/writeToFile/` — supporting types and output helper.

The class diagram and use-case PDF are stored one level above `Exercise11`. `README5.txt` preserves the original implementation reflection, and `waterGenerator.rar` is an additional archived artifact.

## Opening the project

Use a JDK and a Java IDE or compiler with the package structure under `src` intact. No third-party Java library is evident in the source. The application entry class is `mainPacket.MainClass`; see the nested README for the original run guidance.

This is an unfinished learning artifact. Both the original notes and source comments describe difficulties with the design and threading, so the presence of a GUI and scheduling classes should not be read as a claim that all workflows function correctly.
