% Data for Pn/4
If_dikt_4 = [1.55 1.86 2.17 2.48 2.79 3.1 3.41 3.72 4.03 4.34 4.65 4.96 5.27 6.0 6.4 7.1];
Is_dikt_4 = [4.72 4.1 3.6 3.2 2.87 2.8 2.7 2.87 3.17 3.6 4.1 4.6 5.2 6.8 7.4 9];
cosf_4 = 1820/(sqrt(3)*400);
cosf_4 = cosf_4./Is_dikt_4;

% Data for Pn/2
If_dikt_2 = [1.5 1.87 2.24 2.61 2.98 3.35 3.72 4.09 4.46 4.83 5.2 5.57 5.94 6.31 6.68 7.1];
Is_dikt_2 = [8.4 7.49 6.84 6.23 5.66 5.39 5.25 5.3 5.48 5.8 6.28 6.8 7.42 8 8.68 9.43];
cosf_2 = 3645/(sqrt(3)*400);
cosf_2 = cosf_2./Is_dikt_2;

figure;
plot(If_dikt_4, Is_dikt_4, '-o', 'DisplayName', 'Pn/4', 'LineWidth', 1.5, 'MarkerSize', 6, 'MarkerFaceColor', 'b');
hold on;
plot(If_dikt_2, Is_dikt_2, '-x', 'DisplayName', 'Pn/2', 'LineWidth', 1.5, 'MarkerSize', 6, 'MarkerFaceColor', 'r');
xlabel('If (A)', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('Is (A)', 'FontSize', 12, 'FontWeight', 'bold');
title('Is vs If στον παραλληλισμό', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best', 'FontSize', 12);
grid on;
set(gca, 'FontSize', 12, 'LineWidth', 1.2);
hold off;
