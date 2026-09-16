clear all;
clc;
close all;
T = 50:1:1000;

sum_x_i = [0, 0, 0, 0, 0];
sum_y_i = [0, 0, 0, 0, 0];
sum_xy_i = [0, 0, 0, 0, 0];
sum_x2_i =[0, 0, 0, 0, 0];
sum_y2_i =[0, 0, 0, 0, 0];

T = [50, 100, 150, 200, 400, 600, 800, 1000];
k = [28, 9.1, 4.0, 2.7, 1.1, 0.6, 0.4, 0.3];
n = length(k);
y_lin = [log(k); log(k); log10(k); 1./k; 1./k];
x_lin = [log(T); T; T; T; 1./T];

coefficients = zeros(1, 5); % Pre-allocate for clarity and efficiency
for i = 1:5
    [coefficients(i),sum_x_i(i), sum_y_i(i), sum_xy_i(i), sum_x2_i(i), sum_y2_i(i)] = pearson(x_lin(i, :), y_lin(i, :));
    
end

% Debugging: Check the coefficients array
disp('Coefficients:');
disp(coefficients);



for i = 2:5
    pos = 1;
    max_val = abs(coefficients(1));
    if abs(coefficients(i)) > max_val
        max_val = abs(coefficients(i))
        pos = pos + 1;
    end
end

if pos == 1
    [a1, a0] = calculateCoef(sum_x_i(1), sum_y_i(1), sum_xy_i(1), sum_x2_i(1), sum_y2_i(1), n);
    m = a1;
    b = exp(a0);
    kk = b * T.^m;
end

if pos == 2
    [a1, a0] = calculateCoef(sum_x_i(2), sum_y_i(2), sum_xy_i(2), sum_x2_i(2), sum_y2_i(2), n);
    m = a1;
    b = exp(a0);
    kk = b*exp(m*T);
end

if pos == 3
    [a1, a0] = calculateCoef(sum_x_i(3), sum_y_i(3), sum_xy_i(3), sum_x2_i(3), sum_y2_i(3), n);
    m = a1;
    b = 10^a0;
    kk = b*10.^(m*T);
end

if pos == 4
    [a1, a0] = calculateCoef(sum_x_i(4), sum_y_i(4), sum_xy_i(4), sum_x2_i(4), sum_y2_i(4), n);
    m = a1;
    b = a0;
    kk = 1/(m*T + b);
end

if pos == 5
    [a1, a0] = calculateCoef(sum_x_i(5), sum_y_i(5), sum_xy_i(5), sum_x2_i(5), sum_y2_i(5), n);
    m  = 1/a0;
    b = a1/a0;
    kk = m*T / (b + T);
end

%max_val
%pos

plot(T, kk, 'b-', T, k, 'ro'); % Plot kk with a blue line and k with red circles
grid on; % Add a grid for better visualization
xlabel('T'); % Label for x-axis
ylabel('k and kk'); % Label for y-axis
legend('Fitted Curve (kk)', 'Original Data (k)'); % Adding a legend
title('Graph of Fitted Curve vs. Original Data'); % Title of the graph

    


