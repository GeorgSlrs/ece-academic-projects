
clc;
clear;
close all;


figure;
%% a)
G = tf([1 1], [1 0 0]) % open loop
subplot(1, 2, 1)
sgrid(0.7)
rlocus(G)

% K ~= 2.1 

%% b)
subplot(1, 2, 2)
rlocus(G)
sgrid(0.64, 1.5)