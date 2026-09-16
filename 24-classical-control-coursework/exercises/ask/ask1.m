% Define the transfer function G1(s) and convert to state-space
num_G1 = [1 10];
den_G1 = [1 0];
G1 = tf(num_G1, den_G1);
G1_ss = ss(G1);

% Define the transfer function G2(s) and convert to state-space
num_G2 = [3 2 1];
den_G2 = [1 8 5];
G2 = tf(num_G2, den_G2);
G2_ss = ss(G2);

% Display state-space models
disp('State-space model for G1(s):');
disp(G1_ss);

disp('State-space model for G2(s):');
disp(G2_ss);
