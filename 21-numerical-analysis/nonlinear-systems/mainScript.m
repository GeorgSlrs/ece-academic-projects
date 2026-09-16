clear; clc;

% Initial conditions
X0 = [0; 0; 0; 0];

% Tolerance for convergence
tol = 1e-8;

% Maximum number of iterations
maxIter = 100;

% Solve the system using Newton's Method
[X, iterations] = newtonsMethod(X0, tol, maxIter);

% Display the solution
disp('Solution:');
disp(X);

% Plot the results
figure;
subplot(4,1,1);
plot(iterations(1,:));
title('Tc vs. Iterations');
ylabel('Tc');

subplot(4,1,2);
plot(iterations(2,:));
title('Jc vs. Iterations');
ylabel('Jc');

subplot(4,1,3);
plot(iterations(3,:));
title('Th vs. Iterations');
ylabel('Th');

subplot(4,1,4);
plot(iterations(4,:));
title('Jh vs. Iterations');
ylabel('Jh');
xlabel('Iterations');