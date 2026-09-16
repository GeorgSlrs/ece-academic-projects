function [X, iterations] = newtonsMethod(X0, tol, maxIter)
    X = X0;
    for i = 1:maxIter
        [F,J] = systemEquations(X);
        
        
        % Update the solution
        X = X - J\F;
        
        % Store iterations for plotting
        iterations(:,i) = X;
        
        % Check for convergence
        if max(abs(F)) < tol
            fprintf('Convergence achieved after %d iterations.\n', i);
            return;
        end
    end
    fprintf('Solution did not converge within %d iterations.\n', maxIter);
end
