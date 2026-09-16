function build_lvl1
% BUILD_LVL1  Level-1: adds motor electrical dynamics + average H-bridge.
% INPUT to plant: u = [V; tau_L]
% Two command modes (Manual Switch):
%   • DUTY mode : duty ∈ [-1,1]  →  V = duty*Vbus
%   • VOLTS mode: PID output treated as volts (saturated to ±Vbus)
% Optional feed-forward: +Ke * (dtheta) to cancel back-EMF

% Ensure parameters
if ~evalin('base',"exist('Ae','var') && exist('BV','var') && exist('Bd1','var') && exist('Ce','var') && exist('Vbus','var') && exist('Ke','var')")
    evalin('base','flex_joint_params');
end

% Defaults
pairs = {
    'tauL1',     0.0;
    'PID_P_L1',  1.0;
    'PID_I_L1',  0.0;
    'PID_D_L1',  0.0;
};
for i=1:size(pairs,1)
    if ~evalin('base',sprintf("exist('%s','var')",pairs{i,1}))
        assignin('base',pairs{i,1},pairs{i,2});
    end
end
Vbus_s = num2str(evalin('base','Vbus'));
tauL1_s = num2str(evalin('base','tauL1'));

mdl = 'RFJ_L1';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);

%% Ref and error
add_block('simulink/Sources/Step',[mdl '/theta_ref_step'],'Time','0.5','Before','0','After','0.5');
add_block('simulink/Sources/Sine Wave',[mdl '/theta_ref_sine'],'Amplitude','0.3','Frequency','pi');
add_block('simulink/Signal Routing/Manual Switch',[mdl '/ref_source']);
add_block('simulink/Math Operations/Sum',[mdl '/sum_e'],'Inputs','+-');

%% PID(θ)
add_block('simulink/Continuous/PID Controller',[mdl '/PID'], ...
    'P','PID_P_L1','I','PID_I_L1','D','PID_D_L1');

%% Command path: DUTY branch and VOLTS branch + mode switch
add_block('simulink/Discontinuities/Saturation',[mdl '/SatDuty'],'UpperLimit','1','LowerLimit','-1');
add_block('simulink/Math Operations/Gain',[mdl '/Gain_Vbus'],'Gain','Vbus');   % V = duty*Vbus
add_block('simulink/Discontinuities/Saturation',[mdl '/SatVolt'],'UpperLimit',Vbus_s,'LowerLimit',['-' Vbus_s]);
add_block('simulink/Signal Routing/Manual Switch',[mdl '/mode_Vsel']);

%% Optional feed-forward +Ke*dtheta
add_block('simulink/Continuous/Derivative',[mdl '/dtheta']);
add_block('simulink/Math Operations/Gain',[mdl '/Ke_gain'],'Gain','Ke');
add_block('simulink/Sources/Constant',[mdl '/FF_zero'],'Value','0');
add_block('simulink/Signal Routing/Manual Switch',[mdl '/ff_enable']);  % choose 0 or Ke*dθ
add_block('simulink/Math Operations/Sum',[mdl '/sum_V'],'Inputs','++'); % V_total = V_cmd + FF

%% Disturbance
add_block('simulink/Sources/Constant',[mdl '/tauL'],'Value',tauL1_s);

%% Plant: y=[theta; phi; alpha; i]
add_block('simulink/Continuous/State-Space',[mdl '/Plant_L1']);
set_param([mdl '/Plant_L1'], 'A','Ae','B','[BV Bd1]', ...
    'C','[Ce; 0 0 0 0 1]','D','zeros(4,2)','InitialCondition','[0;0;0;0;0]');

%% I/O routing
add_block('simulink/Signal Routing/Mux',[mdl '/U_mux'],'Inputs','2');
add_block('simulink/Signal Routing/Demux',[mdl '/Ysplit4'],'Outputs','4');

%% Scope & logs
add_block('simulink/Sinks/Scope',[mdl '/Scope']); set_param([mdl '/Scope'],'NumInputPorts','4');
add_block('simulink/Sinks/To Workspace',[mdl '/log_theta'],'VariableName','theta_L1','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace',[mdl '/log_phi'],  'VariableName','phi_L1','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace',[mdl '/log_alpha'],'VariableName','alpha_L1','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace',[mdl '/log_i'],    'VariableName','i_L1','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace',[mdl '/log_duty'], 'VariableName','duty_L1','SaveFormat','Timeseries');
add_block('simulink/Sinks/To Workspace',[mdl '/log_Vcmd'], 'VariableName','Vcmd_L1','SaveFormat','Timeseries');

%% Layout
set_param([mdl '/theta_ref_step'],'Position',[40 70 120 100]);
set_param([mdl '/theta_ref_sine'],'Position',[40 130 120 160]);
set_param([mdl '/ref_source'],    'Position',[160 90 190 140]);
set_param([mdl '/sum_e'], 'Position',[230 95 260 125]);
set_param([mdl '/PID'],   'Position',[300 90 360 130]);

set_param([mdl '/SatDuty'],  'Position',[390 70 430 110]);
set_param([mdl '/Gain_Vbus'],'Position',[470 70 520 110]);
set_param([mdl '/SatVolt'],  'Position',[390 130 430 170]);
set_param([mdl '/mode_Vsel'],'Position',[560 90 590 150]);

set_param([mdl '/dtheta'],   'Position',[860 85 900 125]);
set_param([mdl '/Ke_gain'],  'Position',[930 90 980 120]);
set_param([mdl '/FF_zero'],  'Position',[920 150 950 180]);
set_param([mdl '/ff_enable'],'Position',[1000 110 1030 160]);
set_param([mdl '/sum_V'],    'Position',[1080 105 1120 155]);

set_param([mdl '/tauL'],     'Position',[1080 180 1120 205]);
set_param([mdl '/U_mux'],    'Position',[1170 120 1190 180]);
set_param([mdl '/Plant_L1'],'Position',[1240 70 1480 200]);
set_param([mdl '/Ysplit4'],  'Position',[1500 110 1520 190]);
set_param([mdl '/Scope'],    'Position',[1580 70 1660 190]);

%% Wiring
add_line(mdl,'theta_ref_step/1','ref_source/1');
add_line(mdl,'theta_ref_sine/1','ref_source/2');
add_line(mdl,'ref_source/1','sum_e/1');

add_line(mdl,'Plant_L1/1','Ysplit4/1');  % theta
add_line(mdl,'Ysplit4/1','sum_e/2');     % feedback

add_line(mdl,'sum_e/1','PID/1');

% DUTY branch → Vbus gain
add_line(mdl,'PID/1','SatDuty/1');
add_line(mdl,'SatDuty/1','Gain_Vbus/1');
add_line(mdl,'Gain_Vbus/1','mode_Vsel/1');

% VOLTS branch (direct volts with ±Vbus sat)
add_line(mdl,'PID/1','SatVolt/1');
add_line(mdl,'SatVolt/1','mode_Vsel/2');

% Feed-forward path from dtheta
add_line(mdl,'Ysplit4/1','dtheta/1');
add_line(mdl,'dtheta/1','Ke_gain/1');
add_line(mdl,'Ke_gain/1','ff_enable/1'); add_line(mdl,'FF_zero/1','ff_enable/2');

% Sum total V to plant, plus disturbance
add_line(mdl,'mode_Vsel/1','sum_V/1');
add_line(mdl,'ff_enable/1','sum_V/2');
add_line(mdl,'sum_V/1','U_mux/1');
add_line(mdl,'tauL/1','U_mux/2');
add_line(mdl,'U_mux/1','Plant_L1/1');

% Scope & logs
add_line(mdl,'Ysplit4/1','Scope/1'); add_line(mdl,'Ysplit4/2','Scope/2');
add_line(mdl,'Ysplit4/3','Scope/3'); add_line(mdl,'Ysplit4/4','Scope/4');
add_line(mdl,'Ysplit4/1','log_theta/1'); add_line(mdl,'Ysplit4/2','log_phi/1');
add_line(mdl,'Ysplit4/3','log_alpha/1'); add_line(mdl,'Ysplit4/4','log_i/1');
add_line(mdl,'SatDuty/1','log_duty/1');  add_line(mdl,'sum_V/1','log_Vcmd/1');

save_system(mdl); fprintf('Built %s\n', mdl);
end




