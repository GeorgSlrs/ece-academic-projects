function analysis_metrics
% ANALYSIS_METRICS
% Uses sysL0_tau2theta and sysL1_V2theta if available to get stepinfo.
if ~evalin('base',"exist('sysL0_tau2theta','var')"), analysis_tf_freq; end
sysL0 = evalin('base','sysL0_tau2theta');
sysL1 = evalin('base','sysL1_V2theta');

% Step info
infoL0 = stepinfo(sysL0);
infoL1 = stepinfo(sysL1);
disp('=== Step info (tau->theta, L0) ==='); disp(infoL0);
disp('=== Step info (V->theta, L1)   ==='); disp(infoL1);

% Poles
pL0 = pole(sysL0); pL1 = pole(sysL1);
disp('Poles L0:'); disp(pL0.');
disp('Poles L1:'); disp(pL1.');

end
