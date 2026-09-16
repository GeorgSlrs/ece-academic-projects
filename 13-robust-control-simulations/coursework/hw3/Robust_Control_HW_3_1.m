% define the Laplace variable
s = tf('s');

% define each element of G(s)
G11 = (11*s^3 - 18*s^2 - 70*s - 50) / ( s*(s+10)*(s+1)*(s-5) );
G12 =       (s + 2)               / ( (s+1)*(s-5) );
G21 = 5 * (s + 2)               / ( (s+1)*(s-5) );
G22 = 5 * (s + 2)               / ( (s+1)*(s-5) );

% assemble the 2×2 transfer‐function matrix
G = [ G11, G12;
      G21, G22 ];

% choose coefficients for the input
a = 1;
b = 2;
z = -2;         % pole of the exponential

% time vector
t = linspace(0, 10, 1000);

% build the two‐channel input u(t)
u1 = a * exp(z * t);
u2 = b * exp(z * t);
U  = [u1; u2]';  % lsim expects an N×2 matrix for a 2‐input system

% simulate
Y = lsim(G, U, t);  

% plot
figure;
plot(t, Y(:,1), 'b', 'LineWidth', 1.5); hold on;
plot(t, Y(:,2), 'r', 'LineWidth', 1.5);
xlabel('Time \it{t} (s)');
ylabel('Output \ity(t)');
legend('y_1(t)','y_2(t)','Location','Best');
title('Response of G(s) to u(t) = [1;2] e^{-2t}');
grid on;

