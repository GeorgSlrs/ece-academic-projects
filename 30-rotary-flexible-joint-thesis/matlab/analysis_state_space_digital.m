function analysis_state_space_digital
% ANALYSIS_STATE_SPACE_DIGITAL
% - Builds controllability/observability (L1)
% - Discretizes (Ae,BV,Ce) with Ts_ctrl
% - Example pole placement & LQR design (continuous and discrete)
% - Prints key metrics

% ensure
if ~evalin('base',"exist('Ae','var') && exist('BV','var') && exist('Ce','var') && exist('Ts_ctrl','var')")
    evalin('base','flex_joint_params');
end
Ae = evalin('base','Ae'); BV=evalin('base','BV'); Ce=evalin('base','Ce'); Ts=evalin('base','Ts_ctrl');

% Continuous SS
sysc = ss(Ae,BV,Ce,zeros(3,1));

% Controllability & observability (using theta output row)
Co = ctrb(Ae, BV);  Ob = obsv(Ae, Ce);
rankCo = rank(Co); rankOb = rank(Ob);
fprintf('Controllability rank = %d (n=%d)\n', rankCo, size(Ae,1));
fprintf('Observability   rank = %d (p=%d)\n', rankOb, size(Ce,1));

% Discretize (zero-order hold)
sysd = c2d(sysc, Ts, 'zoh');
[Ad,Bd,Cd,Dd] = ssdata(sysd);
assignin('base','Ad',Ad); assignin('base','Bd',Bd);
assignin('base','Cd',Cd); assignin('base','Dd',Dd);

fprintf('Discretized (ZOH) at Ts = %.4f s\n', Ts);
disp('Ad = '); disp(Ad);
disp('Bd = '); disp(Bd);

% Example pole placement (continuous) for the theta channel only
% Choose desired poles (lightly damped, faster than natural)
des_poles = 5*[-1.2 -1.25 -1.3 -1.35 -1.4];   % rough example
try
    Kpp = place(Ae,BV,des_poles);   % state feedback gain
    fprintf('place(): got Kpp (continuous state feedback)\n');
    assignin('base','Kpp',Kpp);
catch
    warning('place() failed; system may be poorly conditioned for chosen poles.');
end

% Example discrete LQR (Q,R are rough examples)
Q = diag([10 10 1 1 0.1]); R = 0.1;
try
    Kdlqr = dlqr(Ad,Bd,Q,R);
    fprintf('dlqr(): got Kdlqr (discrete LQR gain)\n');
    assignin('base','Kdlqr',Kdlqr);
catch
    warning('dlqr() failed; adjust Q,R.');
end

end
