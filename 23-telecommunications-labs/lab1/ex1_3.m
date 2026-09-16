%ex1_3


clc;
clear;
close all;

GenSignal(1092584);
load res_1092584.mat;
plot(SignIn)
xlabel('x');
ylabel('SignIn')
%axis tight

[means, mins, maxs] = m3s(SignIn)
%mea = mean(SignIn)
%mi = min(SignIn)
%ma = max(SignIn)
save('out_1092584.mat','means','mins', 'maxs')