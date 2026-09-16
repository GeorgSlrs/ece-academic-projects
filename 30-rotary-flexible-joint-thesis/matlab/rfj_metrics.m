function rfj_metrics
% RFJ_METRICS  Compute and print RFJ performance metrics from RFJ_L2 logs.
%
% After running build_all (which simulates RFJ_L2), run:
%   rfj_metrics
%
% Assumes BASE workspace has:
%   e_L2      - timeseries, tracking error e = θ_ref - θ_hat
%   theta_ts  - timeseries, TRUE θ
%   phi_ts    - timeseries, TRUE φ
%   Vcmd_L2   - timeseries, command voltage [V] (if logged)
%
% Works for ANY controller mode (PID, robust, adaptive).

e_ts     = evalin('base','e_L2');
theta_ts = evalin('base','theta_ts');
phi_ts   = evalin('base','phi_ts');

t = e_ts.Time;
e = e_ts.Data;

% deflection α = θ - φ
alpha = interp1(theta_ts.Time, theta_ts.Data, t, 'linear', 'extrap') - ...
        interp1(phi_ts.Time,   phi_ts.Data,   t, 'linear', 'extrap');

% command voltage (if available)
if evalin('base','exist(''Vcmd_L2'',''var'')')
    V_ts = evalin('base','Vcmd_L2');
    V    = interp1(V_ts.Time, V_ts.Data, t, 'linear', 'extrap');
else
    V = zeros(size(t));
end

T = t(end) - t(1);

IAE  = trapz(t, abs(e));
ITAE = trapz(t, (t - t(1)).*abs(e));
ERMS = sqrt(trapz(t, e.^2) / max(T,1e-9));

ARMS = sqrt(trapz(t, alpha.^2) / max(T,1e-9));
Amax = max(abs(alpha));

URMS = sqrt(trapz(t, V.^2) / max(T,1e-9));
if evalin('base','exist(''Vbus'',''var'')')
    Vbus = evalin('base','Vbus');
    sat_ratio = mean(abs(V) >= 0.99*Vbus);
else
    sat_ratio = NaN;
end

fprintf('\n=== RFJ metrics ===\n');
fprintf('  IAE(e_theta)        = %8.4f rad*s\n',   IAE);
fprintf('  ITAE(e_theta)       = %8.4f rad*s^2\n', ITAE);
fprintf('  RMS(e_theta)        = %8.4f rad\n',     ERMS);
fprintf('  RMS(alpha)          = %8.4f rad\n',     ARMS);
fprintf('  max|alpha|          = %8.4f rad\n',     Amax);
fprintf('  RMS(V_cmd)          = %8.4f V\n',       URMS);
if ~isnan(sat_ratio)
    fprintf('  saturation ratio    = %5.1f %% of time\n', 100*sat_ratio);
end
try
    mode = evalin('base','CTL_MODE');
    switch mode
        case 1, mstr = 'PID';
        case 2, mstr = 'Robust SMC';
        case 3, mstr = 'Adaptive BS';
        otherwise, mstr = '(unknown)';
    end
    fprintf('  Controller mode     = %d  (%s)\n', mode, mstr);
catch
end
fprintf('====================\n\n');
end
