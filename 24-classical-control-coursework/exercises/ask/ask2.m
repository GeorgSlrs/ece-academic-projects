A = [0 1; 2 4];
B = [1; 1];
C = [1 0];
D = 0;

[num, den] = ss2tf(A, B, C, D);
G = tf(num, den)

A = [-2 0 4; 0 0 1; 6 2 10];
B = [0; 0; 1];
C = [0 1 0];
D = 0;

[num, den] = ss2tf(A, B, C, D);
G = tf(num, den)
