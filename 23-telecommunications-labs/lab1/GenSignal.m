function [SignIn] = GenSignal(AM)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here


x= floor(AM/100);
y= floor((AM-100*x)/10);
z= AM-100*x-10*y;
fprintf('AM = %d%d%d', x, y, z);

if x == 0
    x = 10;
end

t = linspace(1, pi/100, 100*x*pi);

F1 = x*1e3;
F2 = y*1e3;
F3 = z*1e3;
sigx = x*sin(2*pi*F1*t + x);
sigy = y*sin(2*pi*F2*t + y);
sigz = z*sin(2*pi*F3*t + z);
SignIn = sigx + sigy + sigz;

FILENAME = ['res_' num2str(AM, '%03d') '.mat'];
save(FILENAME, "SignIn");
clear;
end

