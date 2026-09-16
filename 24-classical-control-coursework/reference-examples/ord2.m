wn = 5;
damping_ratio = 0.4;
[num0, den] = ord2(wn, damping_ratio);
num = 5^2*num0;
printsys(num, den, 's')