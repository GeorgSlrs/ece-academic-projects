function [] = GenSpcm(x)
%GenSpcm generates random bits based on last digits of AM
%   Detailed explanation goes here
x = x+3;
Spcm = randi(0:1, 1, x);
save ('Spcm.mat', 'Spcm');
end

