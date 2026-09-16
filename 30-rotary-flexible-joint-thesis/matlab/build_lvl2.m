function build_lvl2
% BUILD_LVL2  Build RFJ_L2: discrete controller + sensors + continuous plant.
%
% RFJ_L2 uses rfj_controller_core.m to implement:
%   - PID (CTL_MODE = 1)
%   - Robust sliding-mode (CTL_MODE = 2)
%   - Adaptive backstepping (CTL_MODE = 3)
%
% It also logs:
%   theta_ts  (true θ, for animation / analysis)
%   phi_ts    (true φ)
%   e_L2      (θ_ref - θ_hat, measured)
%   Vcmd_L2   (command voltage to motor)

% Ensure parameters exist in BASE workspace
if ~evalin('base','exist(''Ae'',''var'') && exist(''BV'',''var'') && exist(''Bd1'',''var'') && exist(''C_out_e'',''var'')')
    evalin('base','flex_joint_params');
end
if ~evalin('base','exist(''Ts_ctrl'',''var'')'), evalin('base','flex_joint_params'); end
if ~evalin('base','exist(''dth_q'',''var'') && exist(''dph_q'',''var'')')
    evalin('base','flex_joint_params');
end

Ae      = evalin('base','Ae');
BV      = evalin('base','BV');
Bd1     = evalin('base','Bd1');
C_out_e = evalin('base','C_out_e');

mdl = 'RFJ_L2';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);

% --------------- Blocks ---------------

% 1) Reference: Step + Sine + Switch
add_block('simulink/Sources/Step', [mdl '/StepRef'], ...
    'Time','0.5','Before','0','After','0.5');
add_block('simulink/Sources/Sine Wave', [mdl '/SineRef'], ...
    'Amplitude','0.5','Frequency','1','Bias','0','Phase','0');
add_block('simulink/Signal Routing/Manual Switch', [mdl '/RefSwitch']);

% 2) Ts constant (for controller core)
add_block('simulink/Sources/Constant', [mdl '/Ts_const'], 'Value','Ts_ctrl');

% 3) Controller core: Interpreted MATLAB Fcn
add_block('simulink/User-Defined Functions/Interpreted MATLAB Fcn', ...
          [mdl '/ControllerCore']);
set_param([mdl '/ControllerCore'], ...
    'MATLABFcn',  'rfj_controller_core', ...
    'SampleTime', 'Ts_ctrl');

% 4) Disturbance torque (τ_L)
add_block('simulink/Sources/Constant', [mdl '/tauL'], 'Value','0');

% 5) Plant (continuous augmented): inputs [V; tau_L]
add_block('simulink/Continuous/State-Space', [mdl '/Plant']);
set_param([mdl '/Plant'], ...
    'A','Ae', ...
    'B','[BV Bd1]', ...
    'C','C_out_e', ...
    'D','zeros(3,2)', ...
    'InitialCondition','[0;0;0;0;0]');

% 6) Input MUX for [V; tau_L]
add_block('simulink/Signal Routing/Mux', [mdl '/U_mux'], 'Inputs','2');

% 7) Demux outputs to {θ_true, φ_true, α_true}
add_block('simulink/Signal Routing/Demux', [mdl '/Ysplit'], 'Outputs','3');

% 8) Sensor chain: quantize + ZOH
add_block('simulink/Discontinuities/Quantizer', [mdl '/Q_theta'], ...
    'QuantizationInterval','dth_q');
add_block('simulink/Discrete/Zero-Order Hold', [mdl '/ZOH_theta'], ...
    'SampleTime','Ts_ctrl');

add_block('simulink/Discontinuities/Quantizer', [mdl '/Q_phi'], ...
    'QuantizationInterval','dph_q');
add_block('simulink/Discrete/Zero-Order Hold', [mdl '/ZOH_phi'], ...
    'SampleTime','Ts_ctrl');

% 9) Error calculation for logging: e = θ_ref - θ_hat
add_block('simulink/Math Operations/Sum', [mdl '/sum_e_log'], 'Inputs','+-');

% 10) To Workspace logs
add_block('simulink/Sinks/To Workspace', [mdl '/log_theta'], ...
    'VariableName','theta_ts','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace', [mdl '/log_phi'], ...
    'VariableName','phi_ts','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace', [mdl '/log_e'], ...
    'VariableName','e_L2','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace', [mdl '/log_u'], ...
    'VariableName','Vcmd_L2','SaveFormat','Timeseries');

% 11) Scope (measured θ_hat, φ_hat, α_true)
add_block('simulink/Sinks/Scope', [mdl '/Scope']);
set_param([mdl '/Scope'], 'NumInputPorts','3');

% --------------- Layout ---------------
set_param([mdl '/StepRef'],      'Position',[50 50  90 70]);
set_param([mdl '/SineRef'],      'Position',[50 100 90 120]);
set_param([mdl '/RefSwitch'],    'Position',[130 60 160 110]);
set_param([mdl '/Ts_const'],     'Position',[130 150 170 170]);
set_param([mdl '/ControllerCore'],'Position',[220 60 300 120]);

set_param([mdl '/tauL'],         'Position',[220 160 270 190]);
set_param([mdl '/U_mux'],        'Position',[310 100 340 150]);
set_param([mdl '/Plant'],        'Position',[380 60 610 170]);
set_param([mdl '/Ysplit'],       'Position',[640 90 660 150]);

set_param([mdl '/Q_theta'],      'Position',[690 60  730 90]);
set_param([mdl '/ZOH_theta'],    'Position',[770 60  810 90]);
set_param([mdl '/Q_phi'],        'Position',[690 110 730 140]);
set_param([mdl '/ZOH_phi'],      'Position',[770 110 810 140]);

set_param([mdl '/sum_e_log'],    'Position',[850 60  880 90]);
set_param([mdl '/log_theta'],    'Position',[690 180 750 205]);
set_param([mdl '/log_phi'],      'Position',[690 220 750 245]);
set_param([mdl '/log_e'],        'Position',[930 60  990 85]);
set_param([mdl '/log_u'],        'Position',[350 190 410 215]);

set_param([mdl '/Scope'],        'Position',[930 120 990 180]);

% --------------- Wiring ---------------

% Reference selection: StepRef -> RefSwitch(1), SineRef -> RefSwitch(2)
add_line(mdl,'StepRef/1','RefSwitch/1');
add_line(mdl,'SineRef/1','RefSwitch/2');

% ControllerCore inputs:
% 1: theta_ref, 2: theta_hat, 3: phi_hat, 4: Ts
add_line(mdl,'RefSwitch/1','ControllerCore/1');

% Plant outputs -> Demux
add_line(mdl,'Plant/1','Ysplit/1');

% TRUE θ, φ to sensor chain
add_line(mdl,'Ysplit/1','Q_theta/1');
add_line(mdl,'Ysplit/2','Q_phi/1');

add_line(mdl,'Q_theta/1','ZOH_theta/1');
add_line(mdl,'Q_phi/1','ZOH_phi/1');

% Sensors to controller
add_line(mdl,'ZOH_theta/1','ControllerCore/2');
add_line(mdl,'ZOH_phi/1','ControllerCore/3');

% Ts_const to controller
add_line(mdl,'Ts_const/1','ControllerCore/4');

% Controller output voltage -> U_mux input 1 and log_u
add_line(mdl,'ControllerCore/1','U_mux/1');
add_line(mdl,'ControllerCore/1','log_u/1');

% Disturbance tauL -> U_mux input 2
add_line(mdl,'tauL/1','U_mux/2');

% U_mux -> Plant input
add_line(mdl,'U_mux/1','Plant/1');

% Logs: TRUE θ, φ
add_line(mdl,'Ysplit/1','log_theta/1');
add_line(mdl,'Ysplit/2','log_phi/1');

% Error log: e = θ_ref - θ_hat
add_line(mdl,'RefSwitch/1','sum_e_log/1');
add_line(mdl,'ZOH_theta/1','sum_e_log/2');
add_line(mdl,'sum_e_log/1','log_e/1');

% Scope inputs: θ_hat, φ_hat, α_true
add_line(mdl,'ZOH_theta/1','Scope/1');
add_line(mdl,'ZOH_phi/1','Scope/2');
add_line(mdl,'Ysplit/3','Scope/3');

save_system(mdl);
fprintf('Built %s (discrete controller + logging)\n', mdl);
end






