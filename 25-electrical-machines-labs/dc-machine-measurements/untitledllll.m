clear;
IF1 = [0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.76];
n = [1360 1231 1111 1015 943 880 837 796 763];
IT1 = [2.3 2.2 2 1.8 1.6 1.5 1.4 1.3 1.3];

% Define the hyperbolic model function
hyperbolic_model = @(a, x) a ./ x;

% Fit the data using the hyperbolic model
[fitresult, gof] = fit(IF1(:), n(:), hyperbolic_model, 'StartPoint', 2000);

% Plot the data and the fit
figure(1);
plot(IF1, n, 'o', 'DisplayName', 'Data');
ylim([0 inf]);
hold on;
plot(fitresult, 'r', IF1, n);
xlabel('IF1 (A)', 'FontWeight', 'bold');
ylabel('n (rpm)', 'FontWeight', 'bold');
title('Hyperbolic Fit to Data');
%legend('Data', 'Hyperbolic Fit');
