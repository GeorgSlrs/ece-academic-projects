# Machine Learning Coursework

Three assignments connect probabilistic reasoning with numerical learning experiments: classification from known distributions, image reconstruction through a neural generator, and conditional-expectation/value-function approximation. The collection mixes Python and MATLAB and includes reports, figures and supplied assignment data.

## Assignments

| Folder | Objective and methods | Environment |
| --- | --- | --- |
| [HW1](Machine_Learning_HW1/) | Compare Bayes decisions and neural classifiers on synthetic distributions; classify MNIST digits 0 and 8. | Python, NumPy, Matplotlib; raw MNIST IDX files for digit experiments |
| [HW2](Machine_Learning_HW2/) | Recover 28×28 images from incomplete/noisy observations by optimizing latent variables of a supplied neural generator with an ADAM-style loop. | MATLAB; supplied `data21.mat`, `data22.mat`, `data23.mat` |
| [HW3](Machine_Learning_HW3/) | Compare conditional-expectation and value-function calculations with neural approximations and sequential decision/RL-style policies. | MATLAB; some scripts use Statistics and Machine Learning Toolbox functions |

## Exploring the work

Each homework README identifies its executable scripts, report and prerequisites. The experiments are independent; there is no single command or shared training pipeline for the whole folder.

Some MNIST and MATLAB scripts retain absolute paths from the original coursework environment. Update those paths to your local data before running them. Historical filename/function-name differences are documented in the HW3 guide.

This is a coursework archive, including some coding-assistant-supported work, rather than a validated production ML system. Saved figures and reports record the original experiments; no new benchmark results are implied by their inclusion.
