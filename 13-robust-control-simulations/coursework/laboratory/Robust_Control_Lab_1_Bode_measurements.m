% Data for "Control Input sinusoidal" (normalized by 2)
amplitude1 = [2, 1.6, 1.15, 1, 0.7, 0.6, 0.5, 0.4, 0.35, 0.3] /2.4;
%
angular_velocity1 = 0:9;

% Transfer function parameters for G_u
Ku = 2.4;
tau_u = 1.53;

% Compute theoretical magnitude
omega = angular_velocity1;
mag_theory_u = Ku ./ sqrt((tau_u * omega).^2 + 1)/2.4;

% Plot for Control Input
figure;
plot(angular_velocity1, amplitude1, '-o', 'DisplayName', 'Normalized Measurements');
hold on;
plot(omega, mag_theory_u, 'r-', 'DisplayName', 'G_u Theory');
hold off;
xlabel('Angular Velocity (rad/s)');
ylabel('Normalized Amplitude');
% title('Control Input: Amplitude vs. Angular Velocity');
legend('Location', 'best');
grid on;
sgtitle('Control Input sinusoidal');

% Data for "Disturbance sinusoidal" (normalized by 3.1)
amplitude2 = [3, 3.1, 1.4, 1.3, 1, 0.7, 0.6, 0.5, 0.45, 0.3] / 3.1;
angular_velocity2 = 0:9;

% Updated transfer function parameters for G_d
Kd = 1.67;
tau_d = 1.12;

% Compute theoretical magnitude
mag_theory_d = Kd ./ sqrt((tau_d * omega).^2 + 1)/3.1;

% Plot for Disturbance
figure;
plot(angular_velocity2, amplitude2, '-o', 'DisplayName', 'Normalized Measurements');
hold on;
plot(omega, mag_theory_d, 'r-', 'DisplayName', 'G_d Theory');
hold off;
xlabel('Angular Velocity (rad/s)');
ylabel('Normalized Amplitude');
%title('Disturbance: Amplitude vs. Angular Velocity');
legend('Location', 'best');
grid on;
sgtitle('Disturbance sinusoidal');