%ex1_1
clc;
clear;
close all;

load Lab1_1.mat;


f = x2.^3 - 3 * x1.^2 + x3;
plot(f)
save('Lab1_1_Out.mat','f')