A = [-1 -1; 6.5 0];
B = [1 1; 1 0];
C = [1 0; 0 1];
D = [0 0; 0 0];

step(A, B, C, D, 1);
grid
title('Step-Response Plots: Input = u1 (u2 = 0)')
text(3.4, -0.06, 'Y1')
text(3.4, 1.4, 'Y2')

step(A, B, C, D, 2);
grid
title('Step-Response Plots: Input = u2 (u1 = 0)')

text(3, 0.14, 'Y1')
text(2.8, 1.1, 'Y2')