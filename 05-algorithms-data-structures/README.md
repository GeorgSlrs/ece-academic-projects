# Algorithms & Data Structures Coursework

Two Python assignments examine how algorithm and data-structure choices affect computation on arrays and streams of synthetic measurements. Both include source code, a driver and a coursework report.

## Projects

| Project | What to inspect |
| --- | --- |
| [Maximum Subarray](maximum-subarray/) | Cubic enumeration, quadratic accumulation, divide-and-conquer and Kadane's algorithm. `max_subarray.py` contains the implementations; `main.py` generates inputs and measures runtime. |
| [Running Median](running-median/) | Custom heap operations and synthetic temperature measurements associated with 2D points. `ex3.py` contains the data models, heap logic and driver. |

## Running the exercises

Python 3 is sufficient; the source uses the standard library. Follow the corresponding subproject README and run its driver from that directory.

The configured experiments can generate large arrays and measurement streams. Review the input-size settings before running a benchmark. Timing output describes a particular execution and machine; the archived reports are the place to compare the original coursework observations.

The implementations are preserved as academic exercises, including historical design choices. See the repository-level authorship note for the broader portfolio context.
