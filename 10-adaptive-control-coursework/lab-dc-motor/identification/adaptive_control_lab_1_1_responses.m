clc;
clear all;
close all;

%% ------------------------------------------------------------------------
%  Measured data
%  - Inputs:  PWM commands (0–255)
%  - Outputs: steady-state motor response (Res_pos / Res_neg)
% -------------------------------------------------------------------------

Pos_Pwm = [128
           138
           148
           158
           168
           178
           188
           198
           208
           218
           228
           238
           248
           255];

Neg_Pwm = [0
           10
           20
           30
           40
           50
           60
           70
           80
           90
           100
           110
           120
           128];

Corr = [127
        127
        127
        127
        127
        127
        127
        127
        127
        127
        127
        127
        127
        127];

T_rise_p = [0.1
            0.1
            0.3
            0.6
            1.0
            1.1
            0.9
            0.9
            0.9
            1.6
            1.1
            1.1
            1.1];

T_rise_n = [0.05
            0.1
            0.1
            0.1
            0.65
            1.3
            1.2
            0.55
            0.65
            0.7
            1.2
            0.9
            1.0];

% Steady-state responses of the motor / plant
Res_pos = [4
           9
           13
           13.5
           14
           16
           17.5
           17.5
           18
           20.5
           21
           21
           21
           25];

Res_neg = -[24
            22
            21
            20
            18
            18
            16
            14
            13
            11
            9
            7
            7
            5];

%% ------------------------------------------------------------------------
%  Static fits: PWM -> steady-state response
%  fit1: Res_pos vs Pos_Pwm
%  fit2: Res_neg vs Neg_Pwm
% -------------------------------------------------------------------------

polyfit(Pos_Pwm, Res_pos, 1); % just prints coefficients
fit(Pos_Pwm, Res_pos, 1, ...
    "fit1: steady-state output vs positive PWM", ...
    "Positive PWM command u_{PWM} (0–255)", ...
    "Steady-state output y_{ss} (same units as Res\_pos)", ...
    1);

polyfit(Neg_Pwm, Res_neg, 1); % just prints coefficients
fit(Neg_Pwm, Res_neg, 1, ...
    "fit2: steady-state output vs negative PWM", ...
    "Negative PWM command u_{PWM} (0–255, reverse direction)", ...
    "Steady-state output y_{ss} (same units as Res\_neg)", ...
    2);

% (From your identification)
% G_p(s) = 0.1258 / (0.8308 s + 1)
% G_n(s) = 0.1474 / (0.6538 s + 1)

%% ------------------------------------------------------------------------
%  Time-domain responses of identified first-order models
%  Inputs (also written on the graphs):
%    - Step: u(t) = A_step * 1(t),       A_step = 1
%    - Slow sine: u(t) = A_sine * sin(2π f_sine t),
%                 A_sine = 1, f_sine = 0.1 Hz
%    - Ramp: u(t) = slope * t,           slope = 0.1
% -------------------------------------------------------------------------

% Identified parameters
Kp = 0.1258;   % gain of positive-direction model
Tp = 0.8308;   % time constant of positive-direction model

Kn = 0.1474;   % gain of negative-direction model
Tn = 0.6538;   % time constant of negative-direction model

s  = tf('s');

Gp = Kp / (Tp*s + 1);  % positive plant model
Gn = Kn / (Tn*s + 1);  % negative plant model

% Simulation horizon
t = 0:0.01:10;  % 0 to 10 s with 10 ms step

% Input parameters (shown in titles/legends)
A_step     = 1;        % step amplitude
A_sine     = 1;        % sine amplitude
f_sine     = 0.1;      % sine frequency [Hz]
omega_slow = 2*pi*f_sine;
ramp_slope = 0.1;      % ramp slope

% Build test inputs
u_step = A_step * ones(size(t));          % for plotting input
u_slow = A_sine * sin(omega_slow * t);    % slow sine
u_ramp = ramp_slope * t;                  % ramp

%% ---------------- Positive-direction model Gp ----------------
figure(3); clf;

% 1) Step input
[y_step_p, t_step_p] = step(A_step * Gp, t);

subplot(3,1,1);
plot(t_step_p, A_step * ones(size(t_step_p)), '--', 'LineWidth', 1.0); hold on;
plot(t_step_p, y_step_p, 'LineWidth', 1.2);
grid on;
legend( ...
    sprintf('Input u(t): step, A = %.2f', A_step), ...
    'Output y(t)', ...
    'Location','best');
title(sprintf('Positive plant G_p(s): step response, u(t) = %.2f·1(t)', A_step));
ylabel('Output y(t) (same units as Res\_pos)');
xlabel('Time t [s]');

% 2) Slow sinusoidal input
y_slow_p = lsim(Gp, u_slow, t);

subplot(3,1,2);
plot(t, u_slow, '--', 'LineWidth', 1.0); hold on;
plot(t, y_slow_p, 'LineWidth', 1.2);
grid on;
legend( ...
    sprintf('Input u(t): sine, A = %.2f, f = %.2f Hz', A_sine, f_sine), ...
    'Output y(t)', ...
    'Location','best');
title(sprintf('Positive plant G_p(s): slow sinusoidal response, u(t) = %.2f sin(2π·%.2f t)', ...
              A_sine, f_sine));
ylabel('Output y(t) (same units as Res\_pos)');
xlabel('Time t [s]');

% 3) Ramp input (input AND output)
y_ramp_p = lsim(Gp, u_ramp, t);

subplot(3,1,3);
plot(t, u_ramp, '--', 'LineWidth', 1.0); hold on;
plot(t, y_ramp_p, 'LineWidth', 1.2);
grid on;
legend( ...
    sprintf('Input u(t): ramp, slope = %.2f', ramp_slope), ...
    'Output y(t)', ...
    'Location','best');
title(sprintf('Positive plant G_p(s): ramp response, u(t) = %.2f t', ramp_slope));
ylabel('Output y(t) (same units as Res\_pos)');
xlabel('Time t [s]');

%% ---------------- Negative-direction model Gn ----------------
figure(4); clf;

% 1) Step input
[y_step_n, t_step_n] = step(A_step * Gn, t);

subplot(3,1,1);
plot(t_step_n, A_step * ones(size(t_step_n)), '--', 'LineWidth', 1.0); hold on;
plot(t_step_n, y_step_n, 'LineWidth', 1.2);
grid on;
legend( ...
    sprintf('Input u(t): step, A = %.2f', A_step), ...
    'Output y(t)', ...
    'Location','best');
title(sprintf('Negative plant G_n(s): step response, u(t) = %.2f·1(t)', A_step));
ylabel('Output y(t) (same units as Res\_neg)');
xlabel('Time t [s]');

% 2) Slow sinusoidal input
y_slow_n = lsim(Gn, u_slow, t);

subplot(3,1,2);
plot(t, u_slow, '--', 'LineWidth', 1.0); hold on;
plot(t, y_slow_n, 'LineWidth', 1.2);
grid on;
legend( ...
    sprintf('Input u(t): sine, A = %.2f, f = %.2f Hz', A_sine, f_sine), ...
    'Output y(t)', ...
    'Location','best');
title(sprintf('Negative plant G_n(s): slow sinusoidal response, u(t) = %.2f sin(2π·%.2f t)', ...
              A_sine, f_sine));
ylabel('Output y(t) (same units as Res\_neg)');
xlabel('Time t [s]');

% 3) Ramp input (input AND output)
y_ramp_n = lsim(Gn, u_ramp, t);

subplot(3,1,3);
plot(t, u_ramp, '--', 'LineWidth', 1.0); hold on;
plot(t, y_ramp_n, 'LineWidth', 1.2);
grid on;
legend( ...
    sprintf('Input u(t): ramp, slope = %.2f', ramp_slope), ...
    'Output y(t)', ...
    'Location','best');
title(sprintf('Negative plant G_n(s): ramp response, u(t) = %.2f t', ramp_slope));
ylabel('Output y(t) (same units as Res\_neg)');
xlabel('Time t [s]');

%% ------------------------------------------------------------------------
%  Local helper functions
% -------------------------------------------------------------------------
function B = canon(A, dmax, dleit)
    % Canonical scaling of a vector A:
    %   B(n) = (A(n) - dleit) / dmax
    B = ones(1, length(A));
    for n = 1:length(A)
        B(n) = (A(n) - dleit) / dmax;
    end
end

function f = fit(x, y, n, t, xt, yt, fff)
    % Simple polynomial fit + plot
    %   x, y : data
    %   n    : polynomial order
    %   t    : title string
    %   xt   : x-axis label
    %   yt   : y-axis label
    %   fff  : figure number
    figure(fff)
    
    eff  = polyfit(x, y, n); 
    xfit = min(x):0.01:max(x);
    yfit = polyval(eff, xfit);
    
    scatter(x, y, 'filled'); hold on;
    plot(xfit, yfit, 'LineWidth', 1.2);
    grid on;
    title(t);
    xlabel(xt);
    ylabel(yt);
    
    f = eff; % return coefficients if you ever want them
end

