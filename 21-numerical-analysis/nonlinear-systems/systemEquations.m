function [F, J] = systemEquations(X)
    Tc = X(1);
    Jc = X(2);
    Th = X(3);
    Jh = X(4);

    % System of equations
    F = [5.67e-8 * Tc^4 + 17.41 * Tc - Jc - 5188.18;
         Jc - 0.71 * Jh + 7.46 * Tc - 2352.71;
         5.67e-8 * Th^4 + 1.865 * Th - Jh - 2250;
         Jh - 0.71 * Jc + 7.46 * Th - 110093];

    % Jacobian matrix
    J = [5.67e-8 * 4 * Tc^3 + 17.41, -1, 0, 0;
         7.46, 1, 0, -0.71;
         0, 0, 5.67e-8 * 4 * Th^3 + 1.865, -1;
         -0.71, 0, 7.46, 1];
end
