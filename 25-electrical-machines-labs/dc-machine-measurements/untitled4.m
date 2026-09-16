clear;
IF1 = [0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.76];
n = [1360 1231 1111 1015 943 880 837 796 763];
IT1 = [2.3 2.2 2 1.8 1.6 1.5 1.4 1.3 1.3];

figure(1)
plot(IF1,n, 'Marker','o');
ylim([0 inf]);
xlabel("IF1   (A)","FontWeight","bold");
ylabel("n  (rpm)","FontWeight","bold");
title("Κινητήρας εν κενώ");
