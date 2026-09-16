syms y(t)
Dy = diff(y, t);
D2y = diff(y, t, t);

% Correctly define the differential equation
ode = D2y + 4*Dy + 4*y == heaviside(t);

% Define initial conditions
conds = [y(0) == 0, subs(Dy, t, 0) == 0];

% Solve the ODE
ySolSym = dsolve(ode, conds);

% Convert symbolic solution to a MATLAB function for plotting
ySol = matlabFunction(ySolSym);

% Plot the solution
fplot(ySol, [0, 5])
grid on
xlabel('Time (sec)')
ylabel('Response y(t)')
title('Response of the System to a Unit Step Input')

