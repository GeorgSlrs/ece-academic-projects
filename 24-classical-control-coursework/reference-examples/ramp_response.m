num = [2 1];
den = [1 1 1];
t = 0:0.1:10;
r = t;
y = lsim(num, den, r, t);
plot(t,r,'-', t, y,'o')
grid
title('Unit_ramp response obtained by the use of "lsim" command')
xlabel('t sec')
ylabel('Unit-ramp input and system output')
text(6.3, 4.6, 'Unit-ramp input')
text(4.75, 9.0, 'output')