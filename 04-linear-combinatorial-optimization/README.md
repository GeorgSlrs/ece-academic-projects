# Linear & Combinatorial Optimization

Coursework in linear and combinatorial optimization, including an individual final project using exercise planning to study two formulations: allocating time with a linear program and ordering activities with a mixed-integer program. The source makes the model construction and solution process visible through printed constraints, Simplex tableaux, solver output and resource measurements.

## Two formulations

| Script | Model and method |
| --- | --- |
| [Lin_Com_Opt_Final_Project_normal_v2.py](Lin_Com_Opt_Final_Project_normal_v2.py) | A nine-variable monthly workout allocation LP. Includes a two-phase tableau Simplex implementation, a PuLP/CBC comparison, dual/sensitivity calculations and a Simplex adjacency visualization. |
| [Lin_Com_Opt_Final_Project_adv_v1.py](Lin_Com_Opt_Final_Project_adv_v1.py) | An ordered circuit containing all 27 exercises. PuLP/CBC minimizes activity and transition time under muscle-use and intensity rules; MTZ constraints exclude subtours so the selected arcs form one Hamiltonian path. |

The report (`Linear_Opt_Final_Project.pdf` / `.docx`), presentation and preparation notes explain the coursework formulation. `Figure_1.png` preserves a result figure.

## Supporting coursework

[coursework/](coursework/) contains earlier homework on graphical feasible regions, primal/dual linear programs, integer optimization and branch-and-bound knapsack search. Its README identifies the homework folders and dependencies; those exercises also use SciPy and SymPy where required.

## Running an experiment

Use Python 3 with NumPy, pandas, Matplotlib and PuLP, plus an available CBC solver. The optional `psutil` package enables additional memory reporting. Dependencies are also listed in `READ_ME.txt`.

```bash
python Lin_Com_Opt_Final_Project_normal_v2.py
python Lin_Com_Opt_Final_Project_adv_v1.py
```

Model data are embedded in the scripts. Expect verbose output from the tableau implementation and MILP solver; runtime depends on the model and solver environment. These are mathematical coursework examples, not personalized exercise prescriptions or general-purpose optimization packages.
