
clc;
clear;
close all;
scrsz = get(0, 'ScreenSize');

GenSignal(584)
load('res_584.mat','f1','f2')

f1x = f1;
f2x = f2;

Td = 5e-5;
Fs = 20e3;

tstep = 1 / Fs;
t = 0:tstep:Td;

ht = [-0.031 0.0586 0.0743 0.1018 0.129 0.1484 0.155 ...
0.1484 0.129 0.1018 0.0743 0.0586 -0.031];

A1 = 1.0;
phi1 = 0.0;

A2 = 1.0;
phi2 = 0.0;

sig_1 = A1 * sin(2*pi*f1x*t + phi1);
sig_2 = A2 * sin(2*pi*f2x*t + phi2);


sig_in = sig_1 + sig_2;

sig_out = conv(sig_in, ht);
t_conv = (0:(length(sig_out)-1)) * tstep; 

figure('Position', [100 100 scrsz(3)-200 scrsz(4)-200]);


ax = zeros(1, 3);


ax(1) = subplot(3, 1, 1);
plot(t, sig_in, 'b', 'LineWidth', 1.5);
title('Input Signal: sig\_in');
xlabel('Time (s)');
ylabel('Amplitude');
axis([min(t) max(t) floor(min(sig_in)) ceil(max(sig_in))]);
grid on;

ax(2) = subplot(3, 1, 2);
plot((0:length(ht)-1)*tstep, ht, 'r', 'LineWidth', 1.5); 
title('Filter Response: h(t)');
xlabel('Time (s)');
ylabel('Amplitude');
axis([0 (length(ht)-1)*tstep floor(min(ht)) ceil(max(ht))]);
grid on;


ax(3) = subplot(3, 1, 3);
plot(t_conv, sig_out, 'g', 'LineWidth', 1.5);
title('Output Signal: sig\_out');
xlabel('Time (s)');
ylabel('Amplitude');
axis([min(t_conv) max(t_conv) floor(min(sig_out)) ceil(max(sig_out))]);
grid on;


linkaxes(ax, 'x');