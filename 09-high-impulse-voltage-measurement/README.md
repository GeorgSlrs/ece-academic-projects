# High-Impulse Voltage Measurement

A laboratory study comparing two ways of measuring the output of an impulse-voltage generator: peak readings from an impulse voltmeter and waveform samples from an oscilloscope. The report and MATLAB analysis connect the measured, reduced voltage to the original signal through the measurement divider and examine the impulse's amplitude and timing characteristics.

## What the report covers

- The impulse-generator circuit and damped capacitive voltage divider.
- A table of repeated voltmeter readings and the supplied oscilloscope measurements.
- Waveform interpretation, peak amplitude, front/rise-time and tail-time discussion.
- Comparison of the two measurement methods and possible sources of disagreement.

## Files and reproducibility

[LAB_REPORT_ELECTRICAL.docx](LAB_REPORT_ELECTRICAL.docx) is the Greek-language report, including the measurement table, plots, calculations and discussion.

[measurement-analysis/](measurement-analysis/) contains the 20 two-column oscilloscope traces (`tek00000.csv`–`tek00019.csv`) and MATLAB scripts `graph_electrical_mes.m` and `graph2.m` for plotting and waveform analysis. Follow that folder's README for the working-directory requirements, because the scripts use relative paths to the `electrical_mes` data directory.

The report records the original laboratory interpretation. The source and measurements are preserved for inspection; their numerical conclusions have not been independently revalidated.
