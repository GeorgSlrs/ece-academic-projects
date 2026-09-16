T = [50, 100, 150, 200, 400, 600, 800, 1000];
k = [28, 9.1, 4.0, 2.7, 1.1, 0.6, 0.4, 0.3];

y_lin = [log(k); log(k); log10(k); 1./k; 1./k];
x_lin = [log(T); T; T; T; 1./T];

coefficients = zeros(1, 5); % Pre-allocate for clarity and efficiency
for i = 1:5
    coefficients(i) = pearson(x_lin(i, :), y_lin(i, :));
end

% Debugging: Check the coefficients array
disp('Coefficients:');
disp(coefficients);



for i = 1:5
    pos = 1;
    max_val = abs(coefficients(1));
    if abs(coefficients(i)) > max_val
        max_val = abs(coefficients(i))
        pos = pos + 1;
    end
end

max_val
pos
    

function r = pearson(x, y)
    % Ensure inputs are vectors of the same length
    if length(x) ~= length(y)
        error('Input vectors x and y must be of the same length.');
    end

    % Calculate Pearson correlation coefficient
    n = length(x);
    sum_x = sum(x);
    sum_y = sum(y);
    sum_xy = sum(x .* y);
    sum_x2 = sum(x.^2);
    sum_y2 = sum(y.^2);

    numerator = n * sum_xy - sum_x * sum_y;
    denominator = sqrt((n * sum_x2 - sum_x^2) * (n * sum_y2 - sum_y^2));

    if denominator == 0
        r = 0;  % Avoid division by zero
    else
        r = numerator / denominator;
    end
end

