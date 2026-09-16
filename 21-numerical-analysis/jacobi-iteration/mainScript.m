% Define the coefficient matrix A and the vector b
    A = [9.5, -2.5, 0, -2, 0;
         -2.5, 11, -3.5, 0, -5;
         0, -3.5, 15.5, 0, -4;
         -2, 0, 0, 7, -3;
         0, -5, -4, -3, 12];

    
    b = [12; -16; 14; 10; -30];
    
    % Initial guess for the solution
    x0 = zeros(length(b), 1);
    
    % Tolerance for convergence
    tol = 1e-5;
    
    % Maximum number of iterations
    max_iter = 100;
    
    % Call the jacobi function
    [x, iterations] = jacobi_method(A, b, x0, tol, max_iter);
    
    if iterations < max_iter
        fprintf('The solution converged to:\n');
        disp(x);
        fprintf('in %d iterations.\n', iterations);
    else
        fprintf('The solution did not converge within the maximum number of iterations.\n');
    end
