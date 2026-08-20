%% MRAC for P(s) = 1/(s(s+a)) using ONLY the normalized MIT rule (slide form)
% Plant:       y¨ + a y˙ = u
% Ref. model:  y_m¨ + 2ζω0 y_m˙ + ω0^2 y_m = ω0^2 r
% Controller:  u = θ1*r - θ2*y - θ3*y˙
% Normalized MIT update: θ̇_i = -γ * e * ψ_i / (α + ψᵀψ)
%
% Academic coursework artifact. See the folder README for authorship context.

clear; clc; close all;
fsT = 15; fsL = 13; fsTick = 11;
set(groot,'defaultAxesFontSize',fsTick);
a = 1.0; zeta = 0.707; w0 = 2.0;
th_star = [w0^2, w0^2, 2*zeta*w0-a];
gammas = [0.2, 0.4, 0.8]; alpha = 2.0;
A = 1.0; wr_vec = linspace(0.3,2.0,12);
cycles_settle=8; cycles_meas=2;
nG=numel(gammas); nW=numel(wr_vec);
Yp_amp=nan(nG,nW); Ym_amp=nan(1,nW); Erms=nan(nG,nW); Emse=nan(nG,nW); Th_mean=nan(nG,nW,3);

for iw=1:nW
    wr=wr_vec(iw);
    Ym_amp(1,iw)=A*(w0^2)/sqrt((w0^2-wr^2)^2+(2*zeta*w0*wr)^2);
    for ig=1:nG
        gamma=gammas(ig);
        [t,y,ym,e,TH]=simulate_normMIT_sigma(a,zeta,w0,gamma,alpha,A,wr,cycles_settle,cycles_meas);
        if numel(t)<10, continue; end
        Tper=2*pi/wr; t1=t(end)-cycles_meas*Tper; idx=t>=max(t(1),t1);
        if nnz(idx)<5, continue; end
        seg_y=y(idx); seg_e=e(idx); seg_th=TH(idx,:);
        Yp_amp(ig,iw)=0.5*(max(seg_y)-min(seg_y));
        Erms(ig,iw)=sqrt(mean(seg_e.^2)); Emse(ig,iw)=mean(seg_e.^2); Th_mean(ig,iw,:)=mean(seg_th,1);
    end
end

figure('Color','w','Name','Amplitude vs input frequency'); ax=axes; hold(ax,'on'); grid(ax,'on'); box(ax,'on');
plot(ax,wr_vec,Ym_amp,'k--','LineWidth',1.8,'DisplayName','|y_m| (model)');
for ig=1:nG
    plot(ax,wr_vec,Yp_amp(ig,:),'-','LineWidth',1.8,'DisplayName',sprintf('\\gamma=%.2g: |y_p|',gammas(ig)));
end
xlabel(ax,'\\omega_r (rad/s)'); ylabel(ax,'Amplitude'); legend(ax,'Location','best');

figure('Color','w','Name','Error vs input frequency');
ax1=subplot(2,1,1); hold(ax1,'on'); grid(ax1,'on');
for ig=1:nG, plot(ax1,wr_vec,Erms(ig,:),'LineWidth',1.8); end
xlabel(ax1,'\\omega_r (rad/s)'); ylabel(ax1,'RMS(e)');
ax2=subplot(2,1,2); hold(ax2,'on'); grid(ax2,'on');
for ig=1:nG, plot(ax2,wr_vec,Emse(ig,:),'LineWidth',1.8); end
xlabel(ax2,'\\omega_r (rad/s)'); ylabel(ax2,'MSE(e)');

function [t,y,ym,e,TH]=simulate_normMIT_sigma(a,zeta,w0,gamma,alpha,A,wr,cycles_settle,cycles_meas)
    Tper=2*pi/wr; Ttot=(cycles_settle+cycles_meas)*Tper; dt=min(2.5e-4,Tper/1600);
    N=round(Ttot/dt)+1; t=linspace(0,Ttot,N).'; x=zeros(13,1);
    y=zeros(N,1); ym=zeros(N,1); e=zeros(N,1); TH=zeros(N,3);
    for k=1:N-1
        y(k)=x(1); ym(k)=x(3); e(k)=x(1)-x(3); TH(k,:)=x(11:13).';
        x=rk4(@(tt,xx) rhs_normMIT_sigma(tt,xx,a,zeta,w0,gamma,alpha,A,wr),t(k),x,dt);
    end
    y(N)=x(1); ym(N)=x(3); e(N)=x(1)-x(3); TH(N,:)=x(11:13).';
end

function dx=rhs_normMIT_sigma(t,s,a,zeta,w0,gamma,alpha,A,wr)
    y=s(1); yd=s(2); ym=s(3); ymd=s(4);
    psi1=s(5); psi2=s(6); psi3=s(7); psid1=s(8); psid2=s(9); psid3=s(10);
    th1=s(11); th2=s(12); th3=s(13); r=A*sin(wr*t);
    u=th1*r-th2*y-th3*yd;
    ydd=-a*yd+u; ymdd=-2*zeta*w0*ymd-(w0^2)*ym+(w0^2)*r; e=y-ym;
    psi1dd=-2*zeta*w0*psid1-(w0^2)*psi1+r;
    psi2dd=-2*zeta*w0*psid2-(w0^2)*psi2-y;
    psi3dd=-2*zeta*w0*psid3-(w0^2)*psi3-yd;
    denom=alpha+(psi1^2+psi2^2+psi3^2);
    th1d=-gamma*e*(psi1/denom); th2d=-gamma*e*(psi2/denom); th3d=-gamma*e*(psi3/denom);
    dx=[yd;ydd;ymd;ymdd;psid1;psid2;psid3;psi1dd;psi2dd;psi3dd;th1d;th2d;th3d];
end

function xnew=rk4(f,t,x,h)
    k1=f(t,x); k2=f(t+0.5*h,x+0.5*h*k1); k3=f(t+0.5*h,x+0.5*h*k2); k4=f(t+h,x+h*k3);
    xnew=x+(h/6)*(k1+2*k2+2*k3+k4);
end
