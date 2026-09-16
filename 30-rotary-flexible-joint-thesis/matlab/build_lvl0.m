function build_lvl0
% BUILD_LVL0  Level-0 Simulink model: mechanics-only plant with PID on theta.
%
%   u_path: e -> PID -> (uPID) -> subtract Kalpha*alpha -> tau command
%   actuator shaping: saturation |tau|<=U_MAX and rate limiting
%   plant: xdot = A_L0 x + [Btau_L0 Bd_L0][tau; tau_L], y = C_out x
%
% NOTES:
% - FallingSlewLimit MUST be <= 0 by Simulink convention.
% - All numeric literals are passed as strings to avoid workspace lookup issues.

% Ensure required matrices exist
if ~evalin('base',"exist('A_L0','var') && exist('Btau_L0','var') && exist('Bd_L0','var') && exist('C_out','var')")
    evalin('base','flex_joint_params');
end

% Safe defaults (created if missing)
defs = {
    'U_MAX',        0.15;     % |tau| limit [N·m] (>=0)
    'SLEW_UP',      1.50;     % max positive d(tau)/dt [N·m/s] (>=0)
    'SLEW_DN',      1.50;     % magnitude for negative d(tau)/dt (we use -abs)
    'Kalpha_gain',  0.20;     % cross-feedback gain on alpha
    'X0_L0',        [0;0;0;0];
    'tauL0',        0.0;
};
for i=1:size(defs,1)
    name = defs{i,1}; val = defs{i,2};
    if ~evalin('base',sprintf("exist('%s','var')",name)), assignin('base',name,val); end
end

% Pull numbers from BASE and convert to safe strings
U_MAX      = max(0, evalin('base','U_MAX'));        U_MAX_s    = num2str(U_MAX);
SLEW_UP    = max(0, evalin('base','SLEW_UP'));      SLEW_UP_s  = num2str(SLEW_UP);
SLEW_DN    = evalin('base','SLEW_DN');              SLEW_DN_s  = num2str(-abs(SLEW_DN));  % <= 0
KalphaGain = evalin('base','Kalpha_gain');          Kalpha_s   = num2str(KalphaGain);
X0         = evalin('base','X0_L0');                X0_s       = mat2str(X0);
tauL0      = evalin('base','tauL0');                tauL0_s    = num2str(tauL0);

mdl = 'RFJ_L0';                     % (rename if path shadowing annoys you)
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);

%% Blocks: sources & selector
add_block('simulink/Sources/Step',      [mdl '/theta_ref'],      'Time','0.5','Before','0','After','0.5');
add_block('simulink/Sources/Sine Wave', [mdl '/theta_ref_sine'], 'Amplitude','0.3','Frequency','pi');
add_block('simulink/Signal Routing/Manual Switch',[mdl '/ref_source']); % switch ref

%% e = ref - theta, then PID
add_block('simulink/Math Operations/Sum',[mdl '/sum_e'],'Inputs','+-');
add_block('simulink/Continuous/PID Controller',[mdl '/PID'],'P','2.0','I','0.0','D','0.0');

%% Cross-feedback: u = uPID - Kalpha*alpha
add_block('simulink/Math Operations/Gain',[mdl '/Kalpha'],'Gain',Kalpha_s);
add_block('simulink/Math Operations/Sum',[mdl '/sum_u'],'Inputs','+-');

%% Actuator shaping: sat + rate limit
add_block('simulink/Discontinuities/Saturation',[mdl '/TauSat'], ...
    'UpperLimit',U_MAX_s,'LowerLimit',['-' U_MAX_s]);
add_block('simulink/Discontinuities/Rate Limiter',[mdl '/TauRate'], ...
    'RisingSlewLimit',SLEW_UP_s,'FallingSlewLimit',SLEW_DN_s);   % <= 0

%% Disturbance tau_L
add_block('simulink/Sources/Constant',[mdl '/tauL'],'Value',tauL0_s);

%% Plant y=[theta;phi;alpha]
add_block('simulink/Continuous/State-Space',[mdl '/Plant']);
set_param([mdl '/Plant'], ...
  'A','A_L0','B','[Btau_L0 Bd_L0]','C','C_out','D','zeros(3,2)','InitialCondition',X0_s);

%% I/O split/merge + scopes
add_block('simulink/Signal Routing/Mux',[mdl '/U_mux'],'Inputs','2');
add_block('simulink/Signal Routing/Demux',[mdl '/Ysplit'],'Outputs','3');
add_block('simulink/Sinks/Scope',[mdl '/Scope']); set_param([mdl '/Scope'],'NumInputPorts','3');

%% Logs (for debugging/analysis)
add_block('simulink/Sinks/To Workspace',[mdl '/log_theta'],'VariableName','theta_L0','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace',[mdl '/log_phi'],  'VariableName','phi_L0','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace',[mdl '/log_alpha'],'VariableName','alpha_L0','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace',[mdl '/log_tau'],  'VariableName','tau_cmd_L0','SaveFormat','Timeseries');

%% Layout (just for readability)
set_param([mdl '/theta_ref'],'Position',[40 70 120 100]);
set_param([mdl '/theta_ref_sine'],'Position',[40 130 120 160]);
set_param([mdl '/ref_source'],'Position',[160 90 190 140]);
set_param([mdl '/sum_e'],'Position',[230 95 260 125]);
set_param([mdl '/PID'],  'Position',[300 90 360 130]);
set_param([mdl '/Kalpha'],'Position',[300 170 360 200]);
set_param([mdl '/sum_u'], 'Position',[390 100 420 140]);
set_param([mdl '/TauSat'], 'Position',[450 95 490 135]);
set_param([mdl '/TauRate'],'Position',[520 95 560 135]);
set_param([mdl '/tauL'],  'Position',[520 160 560 185]);
set_param([mdl '/U_mux'], 'Position',[590 110 610 160]);
set_param([mdl '/Plant'],'Position',[640 70 820 180]);
set_param([mdl '/Ysplit'],'Position',[840 100 860 160]);
set_param([mdl '/Scope'], 'Position',[900 80 960 160]);
set_param([mdl '/log_theta'],'Position',[900 180 980 200]);
set_param([mdl '/log_phi'],  'Position',[900 210 980 230]);
set_param([mdl '/log_alpha'],'Position',[900 240 980 260]);
set_param([mdl '/log_tau'],  'Position',[600 200 670 220]);

%% Wiring
add_line(mdl,'theta_ref/1','ref_source/1');
add_line(mdl,'theta_ref_sine/1','ref_source/2');
add_line(mdl,'ref_source/1','sum_e/1');

add_line(mdl,'Plant/1','Ysplit/1');      % y → Demux
add_line(mdl,'Ysplit/1','sum_e/2');      % theta feedback

add_line(mdl,'sum_e/1','PID/1');
add_line(mdl,'PID/1','sum_u/1');
add_line(mdl,'Ysplit/3','Kalpha/1');     % alpha
add_line(mdl,'Kalpha/1','sum_u/2');      % subtract Kalpha*alpha

add_line(mdl,'sum_u/1','TauSat/1');
add_line(mdl,'TauSat/1','TauRate/1');

add_line(mdl,'TauRate/1','U_mux/1');     % tau
add_line(mdl,'tauL/1','U_mux/2');        % tau_L
add_line(mdl,'U_mux/1','Plant/1');

add_line(mdl,'Ysplit/1','Scope/1'); add_line(mdl,'Ysplit/2','Scope/2'); add_line(mdl,'Ysplit/3','Scope/3');
add_line(mdl,'Ysplit/1','log_theta/1'); add_line(mdl,'Ysplit/2','log_phi/1'); add_line(mdl,'Ysplit/3','log_alpha/1');
add_line(mdl,'TauRate/1','log_tau/1');

save_system(mdl); fprintf('Built %s\n', mdl);
end

