# Java Programming Practice

Small coursework and practice programs from an Eclipse workspace, covering object-oriented programming, Swing interfaces, exceptions and concurrency. Each subfolder is an independent program or exercise set; source packages and class names are preserved.

| Folder | Exercise | Entry point |
| --- | --- | --- |
| `inheritance-animals` | Inheritance, overriding, field hiding and casts | `Animals` |
| `leap-year` | Console leap-year classification | `Check_Leap_Year` |
| `rectangle-basics` | Rectangle constructors, area and perimeter | `Rectangles` |
| `rectangle-containment` | Interactive point containment and a static object counter | `MainClass` |
| `fuel-tank-exceptions` | Tank filling with custom validation exceptions | `mainPacket.MainClass` |
| `staff-salaries` | Staff hierarchy, enums, salary calculations and linked-list/hash-map searches | `mainPacket.MainClass` |
| `swing-layouts` | Six small Swing frame, form, label and layout examples | Classes in `gui_packet` each provide `main` |
| `executor-threads` | Two Runnable tasks submitted to an ExecutorService | `packet1.Prac1` |
| `water-production` | Shared hydrogen/oxygen counters using synchronized, wait and notifyAll | `waterProd.WaterProduction` |

## Build and run

A Java Development Kit is required. The examples use the Java standard library, including Swing/AWT and `java.util.concurrent`; no external libraries are bundled. Compile and run each subfolder separately because several projects reuse class names.

For example, from `executor-threads/`:

```sh
javac -encoding UTF-8 -d out src/packet1/*.java
java -cp out packet1.Prac1
```

For a project with several packages, compile all of its source files together. In PowerShell, from that project folder:

```powershell
$javaSources = Get-ChildItem -LiteralPath src -Recurse -Filter *.java | ForEach-Object FullName
javac -encoding UTF-8 -d out $javaSources
java -cp out mainPacket.MainClass
```

Swing examples require a graphical desktop. `swing-layouts` requests the optional `Arcade Classic` font in one example; the font is not bundled.

## Archive status

These are preserved learning exercises, including unfinished behavior, not a tested application suite. Sources and imports were inspected; compilation and runtime behavior were not validated because `javac` was not available on the archiving environment's PATH.

Two visible limitations are retained in the original source:

- `water-production` never decrements its fixed target count, and its producers loop indefinitely; it requires manual termination.
- `staff-salaries` tests the permanent-staff branch twice when generating records and retains TODO/debug comments. Its example creates 100,000 randomized records.

Some examples use or adapt course demonstration code. In particular, `staff-salaries/src/randomize/Randomize.java` matches the helper in the local `ClassFilesForWeek4` starter archive and is retained because the exercise depends on it. This collection does not claim that all teaching scaffolding was independently authored.

Eclipse metadata, compiled classes, archives, duplicate starter bundles, empty/hello-world scratch projects, incomplete access-modifier snippets, and earlier copies of the calculator, spaceship and pizzeria projects are omitted. The latter projects are documented elsewhere in this repository.
