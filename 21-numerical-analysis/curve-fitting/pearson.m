function [r, sum_x, sum_y, sum_xy, sum_x2, sum_y2] = pearson(x, y)
    n = length(x); % Number of data points

    sum_x = sum(x);
    sum_y = sum(y);
    sum_xy = sum(x .* y);
    sum_x2 = sum(x.^2);
    sum_y2 = sum(y.^2);

    numerator = n * sum_xy - sum_x * sum_y;
    denominator = sqrt((n * sum_x2 - sum_x^2) * (n * sum_y2 - sum_y^2));

    r = numerator / denominator; % Pearson correlation coefficient
end