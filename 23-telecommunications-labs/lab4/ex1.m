clear all;
close all;
clc;
GenSignal(584);

load('Freq584.mat','Ac','Am','Fc','Fm');

Acc = Ac;              	% Πλάτος φορέα   [Volts]
Fcc = Fc;               % Συχνότητα φορέα
Amm = Am;             	% Πλάτος ημιτόνου   [Volts]
Fmm = Fm;               % Συχνότητα ημιτόνου  [Hz]


Nfft = 512;             % FFT
Nd = Nfft/2+1;
Fsamp = 16.0*Fcc;  
Freq = (Fsamp/Nfft)*(0:Nd-1);
tstep = 1/Fsamp;
mi = 0.8/Amm; 

signal_duration = 1.0*Nfft*tstep;       % Διάρκεια σήματος [secs]
              


time = (0:tstep:signal_duration);      % Χρόνος
Sm = Amm*sin(2*pi*(Fmm*time));           % Σήμα
Sc = Acc*sin(2*pi*Fcc*time);             % Φορέας

%% Διαμόρφωση
SAm = Acc*(1+mi*Sm).*sin(2*pi*Fcc*time);

YSm = fft(Sm,Nfft);                                     %  FFT σήματος εισόδου
Pyy = YSm.*conj(YSm)/(Nfft^2);
PSm = [Pyy(1) 2*Pyy(2:(Nd-1)) Pyy(Nd)]; 

YSc = fft(Sc,Nfft);                                     % FFT σήματος φορέα
Pyy = YSc.*conj(YSc)/(Nfft^2);
PSc = [Pyy(1) 2*Pyy(2:(Nd-1)) Pyy(Nd)]; 

YSAm = fft(SAm,Nfft);                                   %  FFT σήματος AM
Pyy = YSAm.*conj(YSAm)/(Nfft^2);
PSAm = [Pyy(1) 2*Pyy(2:(Nd-1)) Pyy(Nd)]; 




%%   Απεικόνιση στο πεδίο του χρόνου
%
scrsz = get(0,'ScreenSize');
figure('Position',[30 100  scrsz(3)-50  scrsz(4)-200]);
set(gcf, 'color', 'white');
FontSize = 13;
set(gcf,'DefaultLineLineWidth',2);
set(gcf,'DefaultTextFontSize', FontSize, 'DefaultAxesFontSize', FontSize, 'DefaultLineMarkerSize', FontSize);

ax(1) = subplot(2,3,1);           
plot(time*1e3, Sm);
xlabel('Time [msecs]');
ylabel('Amplitude [Volts]');
title('Input Signal');
grid on;

ax(2) = subplot(2,3,2);
plot(time*1e3, Sc);
xlabel('Time [msecs]');
ylabel('Amplitude [Volts]');
title('Carrier');
grid on;

ax(3) = subplot(2,3,3);
plot(time*1e3, SAm);
xlabel('Time [msecs]');
ylabel('Amplitude [Volts]');
title('AM Signal');
grid on


linkaxes(ax);
axis([0 signal_duration*1e3 -(Acc+2*Amm) Acc+2*Amm]);


%% Απεικόνιση στη συχνότητα
bx(1) = subplot(2,3,4); 
plot(Freq*1e-3,10*log10(PSm), '.-')
title('Input Signal');
xlabel('Frequency [kHz]')
ylabel('Power [dBW]')
grid on

bx(2) = subplot(2,3,5);
plot(Freq*1e-3,10*log10(PSc), '.-')
title('Carrier');
xlabel('Frequency [kHz]')
ylabel('Power [dBW]')
grid on

bx(3) = subplot(2,3,6);
plot(Freq*1e-3,10*log10(PSAm), '.-')
title('AM Signal');
xlabel('Frequency [kHz]')
ylabel('Power [dBW]')
grid on

linkaxes(bx);
%axis([0 2e-3*Fcc-40 max(1,1.1*max(10*log10(max([PSm PSc PSAm PSm]))))]);
