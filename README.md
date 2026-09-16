# ECE Academic Projects

Electrical and Computer Engineering coursework, programming exercises, and thesis work covering robotics, control, optimization, machine learning, numerical methods, signals, and electrical systems.

Each numbered folder is a project or a related coursework collection. The links below lead to descriptions of the methods, available files, dependencies, and entry points. Source code is preserved alongside selected reports, presentations, figures, and small supporting datasets.

## Robotics and control

| Project | Focus | Main tools |
| --- | --- | --- |
| [01 · Introduction to Robotics](01-introduction-to-robotics/) | Kinematics, trajectories, simulation, and manipulator control across four assignments | Python |
| [02 · Particle-Filter SLAM](02-particle-filter-slam/) | A 2D simulation of localization and mapping using particle filtering | Python, Jupyter |
| [03 · Quality-Diversity Quadruped](03-quality-diversity-quadruped/) | Simulation-based exploration of quadruped gait controllers and behavior repertoires | Python, PyBullet |
| [10 · Adaptive Control](10-adaptive-control-coursework/) | Adaptive-control assignments and an Arduino DC-motor laboratory | MATLAB, Arduino |
| [11 · Robotic Systems II](11-robotic-systems-ii/) | Hopper control, planar quadrotor studies, trajectory optimization, and TVLQR | Python |
| [12 · Adaptive Rocket Landing](12-adaptive-rocket-landing/) | Rocket dynamics, controller experiments, and landing simulation | Python |
| [13 · Robust Control](13-robust-control-simulations/) | Inverted-pendulum and dual-rotor studies, with supporting control coursework | MATLAB, Python, HTML |
| [24 · Classical Control](24-classical-control-coursework/) | Control-system analysis and laboratory exercises | MATLAB |
| [26 · Intelligent Control Labs](26-intelligent-control-labs/) | Grid-world learning, neural approximation, policy gradients, and TD3-style control | Python, PyTorch, Jupyter |
| [27 · Robotic Systems I Labs](27-robotic-systems-i-labs/) | Rigid-body transforms, RRT planning, pose trajectories, and Kalman filtering | Python, Jupyter |
| [30 · Rotary Flexible Joint Thesis](30-rotary-flexible-joint-thesis/) | Nonlinear flexible-joint modeling, controller comparisons, and working thesis documentation | Python, MATLAB/Simulink |

## Optimization, learning, and numerical methods

| Project | Focus | Main tools |
| --- | --- | --- |
| [04 · Linear & Combinatorial Optimization](04-linear-combinatorial-optimization/) | Simplex, duality, and constrained activity ordering with a mixed-integer formulation | Python, PuLP/CBC |
| [05 · Algorithms & Data Structures](05-algorithms-data-structures/) | Maximum-subarray algorithms and running-median implementations | Python |
| [06 · Machine Learning](06-machine-learning-coursework/) | Learning algorithms and experiments across three coursework assignments | Python, MATLAB |
| [15 · Concrete Crack Detection](15-concrete-crack-detection/) | A convolutional-network workflow for concrete-surface image classification | Python, TensorFlow/Keras |
| [21 · Numerical Analysis](21-numerical-analysis/) | Newton and Jacobi iteration, interpolation, and curve fitting | MATLAB |

## Signals and electrical engineering

| Project | Focus | Main tools / material |
| --- | --- | --- |
| [08 · Digital Twins Research](08-digital-twins-research/) | A written study of digital-twin concepts and applications | Report |
| [09 · High-Impulse Voltage Measurement](09-high-impulse-voltage-measurement/) | Oscilloscope traces and electrical-measurement laboratory analysis | MATLAB, report |
| [19 · Capacitive Sensor & Accelerometer](19-capacitive-sensor-accelerometer/) | Capacitive sensing, measurement circuits, and accelerometer modeling | Design report |
| [20 · Quantum Computing](20-quantum-computing/) | Quantum-computing presentation and science-communication material | Presentation, notes |
| [22 · Signal Processing](22-signal-processing-coursework/) | Signals-and-systems and digital signal-processing coursework | Python, MATLAB |
| [23 · Telecommunications Labs](23-telecommunications-labs/) | Communication-system laboratory exercises | MATLAB |
| [25 · Electrical Machines Labs](25-electrical-machines-labs/) | Electrical-machine laboratory calculations and analysis | MATLAB, Simulink |

## Programming and software

| Project | Focus | Main tools |
| --- | --- | --- |
| [07 · Frogger](07-frogger-arcade-game/) | A team arcade-game project with graphical assets and reports | Python, turtle |
| [14 · Finite-State RNA Translator](14-finite-state-rna-translator/) | An RNA translation exercise using a finite-state transducer | JFLAP |
| [16 · Java Pizzeria](16-java-pizzeria/) | Object-oriented pizzeria coursework | Java |
| [17 · C Programming Practice](17-c-programming-practice/) | C exercises and coursework source files | C |
| [18 · Python Programming Practice](18-python-programming-practice/) | Day-based exercises and a separate lesson collection covering fundamentals through OOP | Python |
| [28 · Java Calculator](28-java-calculator/) | A Swing interface with infix/postfix conversion and stack-based expression evaluation | Java |
| [29 · Java Spaceship Coursework](29-java-spaceship-coursework/) | Swing ship selection and navigation adapted from supplied course material | Java |
| [31 · Java Programming Practice](31-java-programming-practice/) | Small Java projects and object-oriented exercises | Java |

## Using the repository

Start with the README inside the relevant folder. Projects use independent environments; there is no repository-wide install command. Some need MATLAB toolboxes, simulator packages, graphics libraries, external datasets, or physical hardware. These dependencies are documented where they can be established from the archived material.

This is an academic archive, with completed submissions, prototypes, and learning exercises. Syntax checks or short smoke runs do not establish numerical correctness, controller stability, model accuracy, or hardware readiness. Project READMEs identify known setup issues and untested entry points.

## Authorship and scope

Some projects were completed in teams, some adapt instructor-provided material, and some used coding-assistant support. Original attribution is retained where available; inclusion does not claim sole authorship of every file. Refer to project-level notes for context.

New additions are curated to exclude virtual environments, caches, compiled output, credentials, private records, large third-party datasets, downloaded books/manuals, duplicate backup archives, and selected reports containing student identifiers. Original working files remain outside this curated repository.
