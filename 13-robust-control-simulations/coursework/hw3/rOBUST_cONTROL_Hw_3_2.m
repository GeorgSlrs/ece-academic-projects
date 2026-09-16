%% Build plant, controller, and sensitivity
s = tf('s');
A = [1 -0.9; 7 2];  D = diag([1 0.5]);
G = (1/(10*s+1))*A;
K = ((10*s+1)/(10*s))*D;
S = inv(eye(2)+G*K);

%% 1. H∞ norm and peak frequency
[Sinfty, w_star] = hinfnorm(S);          % Sinfty = 3.8569, w_star = 0.2109

%% 2. SVD at the peak
Sw          = squeeze(freqresp(S, w_star));
[U,~,V]     = svd(Sw);
u_star      = U(:,1);
v_star      = V(:,1);

%% 3. Build worst-case r(t) and simulate e(t)
T = 0:0.05:400;
r = sqrt(2)*real( v_star*exp(1j*w_star*T) );    % reference
[e,~] = lsim(S, r.', T);                        % tracking error

%% 4. Plots
subplot(2,1,1), plot(T,r(1,:),T,r(2,:)), grid on
title('Worst-case reference r(t) (unit energy)'), legend r_1 r_2
subplot(2,1,2), plot(T,e(:,1),T,e(:,2)), grid on
title('Resulting error e(t) (energy amplified by ||S||_\infty)'), legend e_1 e_2

fprintf('\n||S||_inf = %.4f  (ω* = %.4f rad/s)\n', Sinfty, w_star);
