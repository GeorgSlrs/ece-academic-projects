function flex_joint_params
% FLEX_JOINT_PARAMS
% Central place for all parameters + state-space matrices.
% Exports variables to BASE so Simulink/analysis scripts can see them.
%
% STATES (L0): x = [theta; phi; dtheta; dphi]
% INPUTS      : tau (actuator torque on hub), tau_L (disturbance on link)
% OUTPUTS     : y = [theta; phi; alpha] with alpha = theta - phi
%
% STATES (L1/L2): x = [theta; phi; dtheta; dphi; i]
% INPUTS        : V (motor voltage), tau_L
% OUTPUTS       : y = [theta; phi; alpha]
%
% ─────────────────────────────────────────────────────────────────────────

%% ---------- Mechanical parameters (SI) ----------
Jm  = 1.20e-4;   % motor/hub inertia [kg·m^2]
Jl  = 2.50e-3;   % link inertia [kg·m^2]
Ks  = 0.40;      % torsional spring stiffness [N·m/rad]
Cs  = 0.020;     % torsional damping [N·m·s/rad]
Bm  = 0.001;     % viscous friction at hub [N·m·s/rad]
Bl  = 0.001;     % viscous friction at link [N·m·s/rad]

%% ---------- Electrical parameters ----------
R   = 4.0;       % winding resistance [ohm]
L   = 0.50e-3;   % winding inductance [H]
Kt  = 0.050;     % torque constant [N·m/A]
Ke  = 0.050;     % back-emf constant [V/(rad/s)]
Vbus= 12.0;      % H-bridge bus [V]

%% ---------- Control / encoder / sampling ----------
Ts_ctrl = 0.005;     % (default) sample time for discrete control [s]
Ncounts = 4096;      % encoder counts/rev for quantization model
dtheta_q = 2*pi/Ncounts;   % quantization step [rad]
dphi_q   = dtheta_q;

%% ====================================================================
% L0: MECHANICS ONLY (x=[th; ph; dth; dph], inputs u=[tau; tau_L])
%   th_dot = dth
%   ph_dot = dph
%   Jm*dth_dot = tau - Ks*(th-ph) - Cs*(dth-dph) - Bm*dth
%   Jl*dph_dot =       Ks*(th-ph) + Cs*(dth-dph) - Bl*dph + tau_L
% =====================================================================
A_L0 = [ 0    0     1     0;
         0    0     0     1;
       -Ks/Jm Ks/Jm -(Cs+Bm)/Jm  Cs/Jm;
        Ks/Jl -Ks/Jl  Cs/Jl   -(Cs+Bl)/Jl ];

Btau_L0 = [0;0; 1/Jm; 0];   % hub torque input
Bd_L0   = [0;0; 0; 1/Jl];   % link disturbance torque

C_out    = [1 0 0 0;    % theta
            0 1 0 0;    % phi
            1 -1 0 0];  % alpha = theta - phi
D_out_L0 = zeros(3,2);

%% ====================================================================
% L1/L2: ADD ELECTRICAL STATE i (x=[th; ph; dth; dph; i], u=[V; tau_L])
% Electrical: L*di/dt = V - R*i - Ke*dtheta
% Hub torque τ = Kt * i enters hub dynamics just like tau.
% =====================================================================
Ae = [ 0     0      1      0      0;
       0     0      0      1      0;
      -Ks/Jm Ks/Jm -(Cs+Bm)/Jm  Cs/Jm   Kt/Jm;    % +Kt*i/Jm
       Ks/Jl -Ks/Jl  Cs/Jl   -(Cs+Bl)/Jl  0;
       0     0    -Ke/L     0     -R/L  ];

BV  = [0;0; 0; 0; 1/L];      % input V affects i̇
Bd1 = [0;0; 0; 1/Jl; 0];     % disturbance tau_L affects link

Ce = [1 0 0 0 0;
      0 1 0 0 0;
      1 -1 0 0 0];
D_out_e = zeros(3,2);

%% ---------- Export to BASE workspace ----------
vars = who; for k=1:numel(vars), assignin('base',vars{k},eval(vars{k})); end

fprintf('[flex_joint_params] L0 and L1/L2 params loaded.\n');
fprintf('  Ks=%.3f  Cs=%.3f  Jm=%.2e  Jl=%.2e  Vbus=%.1fV\n',Ks,Cs,Jm,Jl,Vbus);
fprintf('  Ts_ctrl=%.4fs  dtheta_q=%.5f rad (counts/rev=%d)\n',Ts_ctrl,dtheta_q,Ncounts);
end

