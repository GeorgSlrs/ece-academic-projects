clear all;
close all;
clc;
GenSignal(584);

load('Freq584.mat','Ac','Am','Fc','Fm');

%% Παράμετροι
Acc = Ac;              	% Πλάτος φορέα   [Volts]
Fcc = Fc;               % Συχνότητα φορέα
Amm = Am;             	% Πλάτος ημιτόνου   [Volts]
Fmm = Fm;               % Συχνότητα ημιτόνου  [Hz]



Fsamp = 16.0*Fcc;  
tstep = 1/Fsamp;

Nfft = 2*1024;             % FFT
Nd = Nfft/2+1;
Freq = (Fsamp/Nfft)*(0:Nd-1);       % Συχνότητες FFT

mi = 0.8/Amm; 


              

signal_duration = max(5/Fmm, 1.0*Nfft*tstep);       % Διάρκεια σήματος [secs]

%  LPF  (Fc/2)
Nlpf = 60;          %  Filter taps
LPFcoefs = fir2(Nlpf, [0 Fcc/2  1.1*Fcc/2 Fsamp/2]/(Fsamp/2), [1 1 0 0]);


%% Δημιουργία σημάτων
time = (0:tstep:signal_duration);      % Χρόνος
Sm = Amm*sin(2*pi*(Fmm*time));           % Σήμα
Sc = Acc*sin(2*pi*Fcc*time);             % Φορέας

SAm = (1+mi*Sm).*Sc;                  %  AM

%%   Αποδιαμόρφωση
Ssq = SAm.^2; %ύψωση σε τετράγωνο
Slpf = filter(LPFcoefs, 1, Ssq); %LPF
Stmp = sqrt(Slpf(Nlpf:end)); %ρίζα
Sout = Stmp - mean(Stmp); %αφαιρώ DC συνιστώσα

%%
YSm = fft(Sm,Nfft);                                     %  FFT σήματος εισόδου
Pyy = YSm.*conj(YSm)/(Nfft^2);
PSm = [Pyy(1) 2*Pyy(2:(Nd-1)) Pyy(Nd)]; 

YSAm = fft(SAm,Nfft);                                   %  FFT σήματος AM
Pyy = YSAm.*conj(YSAm)/(Nfft^2);
PSAm = [Pyy(1) 2*Pyy(2:(Nd-1)) Pyy(Nd)]; 


YSsq = fft(Ssq,Nfft);                               % 1st stage
Pyy = YSsq.*conj(YSsq)/(Nfft^2);
PSsq = [Pyy(1) 2*Pyy(2:(Nd-1)) Pyy(Nd)]; 

YSlpf = fft(Slpf,Nfft);                             % 2nd stage   
Pyy = YSlpf.*conj(YSlpf)/(Nfft^2);
PSlpf = [Pyy(1) 2*Pyy(2:(Nd-1)) Pyy(Nd)]; 

YSout = fft(Sout,Nfft);                                 %  FFT σήματος εξόδου
Pyy = YSout.*conj(YSout)/(Nfft^2);
PSout = [Pyy(1) 2*Pyy(2:(Nd-1)) Pyy(Nd)]; 




%%   Απεικόνιση επιμέρους σημάτων του αποδιαμορφωτή
%
scrsz = get(0,'ScreenSize');
figure('Position',[100 100  scrsz(3)-150  scrsz(4)-200]);
set(gcf, 'color', 'white');
FontSize = 13;
set(gcf,'DefaultLineLineWidth',2);
set(gcf,'DefaultTextFontSize', FontSize, 'DefaultAxesFontSize', FontSize, 'DefaultLineMarkerSize', FontSize);


cx(1) = subplot(2,4,1);
plot(time*1e3, SAm);
xlabel('Time [msecs]');
ylabel('Amplitude [Volts]');
title('Σήμα AM');
grid on;


cx(2) = subplot(2,4,2);           
plot(time*1e3, Ssq);
xlabel('Time [msecs]');
ylabel('Amplitude [Volts]');
title('1η βαθμίδα επεξεργασίας');
grid on;


cx(3) = subplot(2,4,3);           
plot(time*1e3, Slpf);
xlabel('Time [msecs]');
ylabel('Amplitude [Volts]');
title('2η βαθμίδα επεξεργασίας');
grid on;


cx(4) = subplot(2,4,4);           
plot(time(Nlpf:end)*1e3, Sout);
xlabel('Time [msecs]');
ylabel('Amplitude [Volts]');
title('Εξοδος αποδιαμορφωτή');
grid on;


linkaxes(cx, 'x');
axis([Nlpf/Fsamp signal_duration*1e3 -1.1*max(abs(Sout(Nlpf:end))) 1.1*max(abs(Sout(Nlpf:end)))]);


dx(1) = subplot(2,4,5);
plot(Freq*1e-3,10*log10(PSAm), '.-')
xlabel('Frequency [kHz]')
ylabel('Power [dBW]')
grid on

dx(2) = subplot(2,4,6);
plot(Freq*1e-3,10*log10(PSsq), '.-')
xlabel('Frequency [kHz]')
ylabel('Power [dBW]')
grid on

dx(3) = subplot(2,4,7);
plot(Freq*1e-3,10*log10(PSlpf), '.-')
xlabel('Frequency [kHz]')
ylabel('Power [dBW]')
grid on

dx(4) = subplot(2,4,8);
plot(Freq*1e-3,10*log10(PSout), '.-')
xlabel('Frequency [kHz]')
ylabel('Power [dBW]')
grid on

linkaxes(dx);
axis([0 3e-3*Fcc -40 max(1,1.1*max(10*log10(max([PSAm PSsq PSlpf PSout]))))]);

%%     
disp('Done! ....');
disp(' ');