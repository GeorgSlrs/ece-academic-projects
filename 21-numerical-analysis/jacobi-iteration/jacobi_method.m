function [x, iterations] = jacobi_method(A, b, x0, tol, max_iter)
    
    L = tril(A,-1);
    U = triu(A,1);
    D = diag(diag(A)); % Ensure D is a diagonal matrix, not a vector
    
    x = x0;
    check_convergence = [norm(D\(L+U), 1), norm(D\(L+U),2), norm(D\(L+U),inf)]

    
    % Corrected convergence check
    if any(check_convergence < 1)
        disp('We have convergence!');
    else
        disp('Convergence criteria not met.');
    end

    for iterations = 1:max_iter
        x_old = x;
        x = -(inv(D)*(L+U)*x) + inv(D)*b;

        % Convergence check based on the specified tolerance
        if x - x_old < 1/2 *tol
            break;
        end
    end
end