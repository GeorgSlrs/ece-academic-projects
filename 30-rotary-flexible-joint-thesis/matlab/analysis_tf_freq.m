function analysis_tf_freq
% ANALYSIS_TF_FREQ
% Builds continuous-time SS/TF for:
%   • L0: G_tau_theta(s) from tau → theta
%   • L1: G_V_theta(s)   from V   → theta
% Plots root locus, Bode (mag/phase), Nyquist, and reports margins.

% Ensure params exist
if ~evalin('base',"exist('A_L0','var') && exist('Btau_L0','var') && exist('C_out','var')")
    evalin('base','flex_joint_params');
end
A_L0  = evalin('base','A_L0');  Btau_L0 = evalin('base','Btau_L0');  C_out = evalin('base','C_out');
Ae    = evalin('base','Ae');    BV      = evalin('base','BV');       Ce    = evalin('base','Ce');

% Output indices: theta is row 1
Cth_L0 = [1 0 0 0]; Dth_L0 = 0;
sysL0  = ss(A_L0, Btau_L0, Cth_L0, Dth_L0);      % tau -> theta

Cth_L1 = [1 0 0 0 0]; Dth_L1 = 0;
sysL1  = ss(Ae, BV, Cth_L1, Dth_L1);             % V -> theta

% Root locus (L0)
figure('Name','Root Locus (tau->theta, L0)'); rlocus(sysL0); grid on;

% Bode + margins (L0)
figure('Name','Bode L0 (tau->theta)'); margin(sysL0);

% Nyquist (L0)
figure('Name','Nyquist L0 (tau->theta)'); nyquist(sysL0); grid on;

% Bode + margins (L1)
figure('Name','Bode L1 (V->theta)'); margin(sysL1);

disp('=== DC gains ===');
disp(['L0: theta/tau DC gain = ' num2str(dcgain(sysL0)) ' [rad/(N·m)]']);
disp(['L1: theta/V   DC gain = ' num2str(dcgain(sysL1)) ' [rad/V]']);

% Save handles in base for later use
assignin('base','sysL0_tau2theta',sysL0);
assignin('base','sysL1_V2theta',sysL1);
end
