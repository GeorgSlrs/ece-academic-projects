clear; 
clc;
n_0_55 = [297 407 498 626 739 897 972 1106 1252 1396];
VT2_0_55 = [40 53 63 80 92 105 119 133 150 170];

n_1_1 = [213 401 499 600 739 854 972 1082 1255 1380];
VT2_1_1 = [58 72 89 105 128 148 168 188 218 239];

figure(1)
plot(n_0_55, VT2_0_55, 'Marker','o','DisplayName',"IF2 = 0.55 A");
hold on;
plot(n_1_1, VT2_1_1, 'Marker','o','DisplayName',"IF2 = 1.1 A");
xlabel("n (rpm)","FontWeight","bold");
ylabel("VT2   (V)","FontWeight","bold");
title("Γεννήτρια εν κενώ με παράμετρο το ρεύμα διέγερσης");
legend;


P1 = polyfit(n_0_55, VT2_0_55,1);
y1fit = P1(1)*n_0_55+P1(2);
hold on;
plot(n_0_55,y1fit,'g','DisplayName',"fit, IF2 = 0.55 A");

P2 = polyfit(n_1_1, VT2_1_1,1);
y2fit = P2(1)*n_1_1+P2(2);
hold on;
plot(n_1_1,y2fit,'m','DisplayName',"fit, IF2 = 1.1 A");
legend;