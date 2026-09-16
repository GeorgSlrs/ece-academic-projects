% Given data points
T = [20, 100, 180, 260, 340];  % Temperature in degrees Celsius
R = [500, 676, 870, 1060, 1205];  % Resistance in ohms



% Estimate the resistance at 150 degrees Celsius
R_150 = lagrange(T, R, 150);
disp(['The estimated resistance at 150°C is ', num2str(R_150), ' ohms.']);

% Lagrange interpolation function
function L = lagrange(x, y, value)
    n = length(x);
    L = 0;
    for i = 1:n
        p = 1;
        for j = 1:n
            if i ~= j
                p = p * (value - x(j)) / (x(i) - x(j));
            end
        end
        L = L + y(i) * p;
    end
end