clc;
clear; 
close all;


% initial steps
ht = [-0.031 0.0586 0.0743 0.1018 0.129 0.1484 0.155 ...
0.1484 0.129 0.1018 0.0743 0.0586 -0.031];

GenSignal(584);

load('res_584.mat', 'f1', 'f2')
scrsz = get(0,'ScreenSize');
%Parameters

Fs = 20000;    %  Δειγματοληψία   [Hz]
tstep = 1/Fs;
Nfft = 1024; % 1024 samples
Td = (Nfft-1)*tstep;     %  Διάρκεια [secs]   
t = 0:tstep:Td;     % in secs
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
F1 = f1;               %  Συχνότητα 1ου ημιτόνου    [Hz]
A1 = 1;                %  Πλάτος 1ου ημιτόνου  [Volts]
ph1 = 0;               %  Aρχική φάση 1ου ημιτόνου  [rand]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
F2 = f2;               %  Συχνότητα 2ου ημιτόνου    [Hz]
A2 = 1.0;              %  Πλάτος 2ου ημιτόνου  [Volts]
ph2 = 0;               %  Aρχική φάση 2ου ημιτόνου  [rand]

fprintf('Signal duration: %d msec \nSampling Rate: %6.4f kHz\n', Td*1000, Fs/1000)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%Creating the signals

sig_1 = A1*sin(2*pi*F1*t+ph1);
sig_2 = A2*sin(2*pi*F2*t+ph2);
sig_in = sig_1 + sig_2;
sig_out = conv(sig_in,ht);

%FFT

Y = fft(sig_in,Nfft); %in
Z = fft(sig_out,Nfft); %out
Nd = Nfft/2+1;
f = (Fs/Nfft)*(0:Nd-1);

%%figure;

figure('Position',[100 100 2*scrsz(3)/3 3*scrsz(4)/4])
set(gcf, 'color', 'white');
FontSize = 12;
set(gcf,'DefaultLineLineWidth',1);
set(gcf,'DefaultTextFontSize', FontSize, 'DefaultAxesFontSize', FontSize, 'DefaultLineMarkerSize', FontSize);

subplot(2,2,1)
n1 = 1;
n2 = 1024; %Θέλουμε και τα 1024 δείγματα
plot(t(n1:n2), sig_in(n1:n2), '.-b');
grid on
xlabel('Time [secs]');
ylabel('Amplitude [Volts]');
axis([t(n1) t(n2) floor(min(sig_in)) ceil(max(sig_in)) ]);
title('sigIn time domain');

subplot(2,2,2)
Ayy = sqrt(Y.*conj(Y))/Nfft;
Ayy = [Ayy(1) sqrt(2)*Ayy(2:(Nd-1)) Ayy(Nd)];
plot(f,Ayy, '.-')
title('Amplitude Spectrum')
xlabel('Frequency (Hz)')
ylabel('Amplitude of FFT(sigIn) (Vrms)')
axis([0 Fs/2 0 1.1*max(Ayy)]);
grid on

subplot(2,2,3)
n1 = 1;
n2 = 1024;
plot(t(n1:n2), sig_out(n1:n2), '.-b'); %%και τα 1024 δείγματα
grid on
xlabel('Time [secs]');
ylabel('Amplitude [Volts]');
axis([t(n1) t(n2) floor(min(sig_in)) ceil(max(sig_in)) ]);
title('sigOut time domain');

subplot(2,2,4)
Azz = sqrt(Z.*conj(Z))/Nfft;
Azz = [Azz(1) sqrt(2)*Azz(2:(Nd-1)) Azz(Nd)];
plot(f,Azz, '.-')
title('Amplitude Spectrum')
xlabel('Frequency (Hz)')
ylabel('Amplitude of FFT(sigOut) (Vrms)')
axis([0 Fs/2 0 1.1*max(Azz)]);
grid on