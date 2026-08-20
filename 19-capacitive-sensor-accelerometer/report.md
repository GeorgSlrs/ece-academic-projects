# Capacitive Sensor & Accelerometer Design Report

Department of Electrical & Computer Engineering, University of Patras

Coursework for Electrical Measurement Devices & Techniques, academic year 2023-24. Personal student identifiers and teammate details have been removed from this public copy.

## Part 1 — Capacitive sensing and measurement

The work studied the sensitivity and loading behaviour of a capacitive sensor and its associated RC measurement circuit. It considered the effect of cable and oscilloscope capacitance on measurement error and explored an op-amp/buffer-based measurement architecture to limit loading of the sensor.

Two measurement ideas were considered. The more developed approach used an RC circuit and buffered voltage measurements to infer capacitance. The report also discussed how a practical current source could replace an ideal source for better accuracy.

### Phase-to-time conversion and digital timing

The proposed measurement chain included phase-to-time conversion followed by digital timing/counting. An SR flip-flop and clock-pulse counter were used conceptually to measure a time interval, with a latched counter and digital display representing the output stage.

For a nominal measurement range of -1 V to +1 V with 0.01 V resolution, the required number of representable values is about 200. The nearest suitable binary resolution is therefore 8 bits (256 values).

## Part 2 — Accelerometer design

The second part modelled an accelerometer using a mass-spring-damper arrangement coupled to the capacitive sensing concept.

Variables included displacement from equilibrium, plate mass, damping coefficient, spring constant, and acceleration. The displacement-to-acceleration relationship was expressed using a second-order transfer-function model and Laplace-domain analysis.

A cutoff frequency of 400 Hz was treated as the maximum useful operating frequency, corresponding to a target settling time of approximately 2.5 ms. A damping ratio around 0.8 was considered, and a representative spring constant of 150 N/m was used in the design calculations.

The work connected mechanical displacement to capacitance change and examined how the resulting capacitance could be measured through the proposed circuit. MATLAB was used to study step responses for multiple acceleration inputs, with the report noting increased overshoot and roughly 1–2 ms additional settling delay at higher acceleration values. A sinusoidal response was also explored.

## Topics covered

- capacitive sensing and sensitivity
- RC measurement circuits and loading error
- op-amp / buffer concepts
- phase-to-time conversion
- digital timing and quantization
- second-order mass-spring-damper modelling
- Laplace-domain transfer functions
- MATLAB dynamic-response simulation
