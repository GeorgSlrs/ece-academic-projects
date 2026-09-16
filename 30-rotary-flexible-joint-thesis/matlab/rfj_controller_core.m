function u_cmd = rfj_controller_core(theta_ref, theta_hat, phi_hat, Ts)
% RFJ_CONTROLLER_CORE  Discrete RFJ controller core (PID / Robust SMC / Adaptive BS).
%
%   u_cmd = rfj_controller_core(theta_ref, theta_hat, phi_hat, Ts)
%
% Inputs:
%   theta_ref  - reference hub angle [rad]
%   theta_hat  - measured hub angle [rad] (quantized + ZOH)
%   phi_hat    - measured link angle [rad]  (quantized + ZOH); if not available, pass 0
%   Ts         - controller sample time [s]
%
% Output:
%   u_cmd      - command *voltage* [V], saturated to [-Vbus, Vbus]
%
% Controller mode is selected via BASE workspace variable CTL_MODE:
%   CTL_MODE = 1  -> PID
%             = 2  -> Robust sliding-mode
%             = 3  -> Adaptive backstepping
%
% Gains and params are also taken from BASE workspace:
%   Vbus, Jm, Ks, Cs, Bm
%   PID_P_L2, PID_I_L2, PID_D_L2
%   SM_lambda, SM_k, SM_phi
%   AB_k1, AB_k2, AB_GKs, AB_GCs, AB_GBm, AB_Ks0, AB_Cs0, AB_Bm0

% -------- read basic params from base workspace (with defaults) --------
mode   = getBaseOr('CTL_MODE', 1);      % 1=PID, 2=SMC, 3=Adaptive BS
Vbus   = getBaseOr('Vbus',    12.0);
Jm     = getBaseOr('Jm',      1.2e-4);

Ks_nom = getBaseOr('Ks',      0.4);
Cs_nom = getBaseOr('Cs',      0.02);
Bm_nom = getBaseOr('Bm',      2e-4);

% PID gains (for mode 1)
Kp = getBaseOr('PID_P_L2', 1.0);
Ki = getBaseOr('PID_I_L2', 5.0);
Kd = getBaseOr('PID_D_L2', 0.0);

% Sliding-mode gains (for mode 2)
SM_lambda = getBaseOr('SM_lambda', 5.0);
SM_k      = getBaseOr('SM_k',      0.2);
SM_phi    = getBaseOr('SM_phi',    0.05);

% Adaptive backstepping gains (for mode 3)
AB_k1   = getBaseOr('AB_k1',  8.0);
AB_k2   = getBaseOr('AB_k2', 12.0);
AB_GKs  = getBaseOr('AB_GKs', 1.0);
AB_GCs  = getBaseOr('AB_GCs', 1.0);
AB_GBm  = getBaseOr('AB_GBm', 0.5);
AB_Ks0  = getBaseOr('AB_Ks0', Ks_nom);
AB_Cs0  = getBaseOr('AB_Cs0', Cs_nom);
AB_Bm0  = getBaseOr('AB_Bm0', Bm_nom);

% -------- persistent memory across calls --------
persistent ei      ...   % integral of error (for PID)
           th_prev ph_prev thref_prev ...
           Ks_hat Cs_hat Bm_hat      % adaptive parameter estimates

if isempty(ei)
    ei         = 0;
    th_prev    = theta_hat;
    ph_prev    = phi_hat;
    thref_prev = theta_ref;
    Ks_hat     = AB_Ks0;
    Cs_hat     = AB_Cs0;
    Bm_hat     = AB_Bm0;
end

% -------- basic signals (errors & derivatives) --------
e          = theta_ref - theta_hat;                       % tracking error
alpha_hat  = theta_hat - phi_hat;                         % deflection estimate
dtheta_hat = (theta_hat - th_prev)  / max(Ts,1e-9);       % hub velocity
dphi_hat   = (phi_hat   - ph_prev)  / max(Ts,1e-9);       % link velocity
dalpha_hat = dtheta_hat - dphi_hat;                       % deflection rate

dtheta_ref = (theta_ref - thref_prev) / max(Ts,1e-9);     % approx ref velocity

th_prev    = theta_hat;
ph_prev    = phi_hat;
thref_prev = theta_ref;

% Default control voltage (will be overwritten)
u = 0;

% ===================== MODE 1: PID =====================
if mode == 1
    % Discrete PI + D on measurement:
    % e[k]   = theta_ref - theta_hat
    % ei[k]  = ei[k-1] + Ts*e[k]
    % dθ[k]  ≈ (θ[k]-θ[k-1])/Ts
    % u[k]   = Kp*e + Ki*ei - Kd*dθ
    ei = ei + Ts*e;
    u  = Kp*e + Ki*ei - Kd*dtheta_hat;

% ===================== MODE 2: ROBUST SMC =====================
elseif mode == 2
    % Sliding-mode on θ, treating flexible torque as disturbance.
    % States:
    %   x1 = θ - θ_ref, x2 = θdot - θdot_ref
    x1 = theta_hat - theta_ref;
    x2 = dtheta_hat - dtheta_ref;

    % Sliding surface:
    %   s = x2 + λ x1
    s = x2 + SM_lambda*x1;

    % Nominal flexible + friction torque (for equivalent control)
    tau_nom = - Ks_nom*alpha_hat - Cs_nom*dalpha_hat - Bm_nom*dtheta_hat;

    % Equivalent term (approx):
    %   u_eq = Jm*(dθ_ref - λ x2) - tau_nom
    u_eq = Jm*(dtheta_ref - SM_lambda*x2) - tau_nom;

    % Robust term:
    %   u_sw = -k * sat(s/φ)
    sigma = s / max(SM_phi,1e-6);
    sat_s = max(-1, min(1, sigma));
    u_sw  = - SM_k * sat_s;

    % Total control:
    u = u_eq + u_sw;

% ===================== MODE 3: ADAPTIVE BACKSTEPPING =====================
else
    % Error coords:
    %   x1 = θ - θ_ref, x2 = θdot - θdot_ref
    x1 = theta_hat - theta_ref;
    x2 = dtheta_hat - dtheta_ref;

    % Step 1: virtual velocity target
    %   x2_des = dθ_ref - k1*x1
    x2_des = dtheta_ref - AB_k1*x1;

    % Step 2: velocity error
    %   z2 = x2 - x2_des
    z2 = x2 - x2_des;

    % Regressor for torque model:
    %   Jm*ddθ = -Ks α - Cs αdot - Bm θdot + τ
    %   => Y = [-α, -αdot, -θdot]^T
    Y = [-alpha_hat; -dalpha_hat; -dtheta_hat];

    % Control law (continuous-time backstepping form):
    %   τ = -Y^T p_hat + Jm*( dθ_ref - k1(z2+x1) - k2*z2 )
    u = - (Y(1)*Ks_hat + Y(2)*Cs_hat + Y(3)*Bm_hat) ...
        + Jm*( dtheta_ref - AB_k1*(z2 + x1) - AB_k2*z2 );

    % Parameter update (discrete Euler):
    %   p_hat[k+1] = p_hat[k] + Ts * Γ Y z2
    Ks_hat = Ks_hat + Ts * AB_GKs * Y(1) * z2;
    Cs_hat = Cs_hat + Ts * AB_GCs * Y(2) * z2;
    Bm_hat = Bm_hat + Ts * AB_GBm * Y(3) * z2;

    % Simple projection to keep estimates physical
    Ks_hat = max(0.01, min(50.0, Ks_hat));
    Cs_hat = max(0.0,  min(5.0 , Cs_hat));
    Bm_hat = max(0.0,  min(0.05, Bm_hat));
end

% -------- final saturation to available DC bus --------
u_cmd = max(-Vbus, min(Vbus, u));

end

% ===== helper to safely read from base workspace =====
function val = getBaseOr(name, defaultVal)
    try
        if evalin('base', sprintf('exist(''%s'',''var'')',name))
            val = evalin('base', name);
        else
            val = defaultVal;
        end
    catch
        val = defaultVal;
    end
end
