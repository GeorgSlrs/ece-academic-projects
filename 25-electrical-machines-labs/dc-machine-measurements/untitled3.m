clear;
IT2 = [0 1 2 3 4 5 6 7];
VT2 = [172 172 171 170 170 170 169 168];

plot(IT2,VT2, 'Marker','o','DisplayName',"IF2 = 0.55 A");
ylim([0 inf]);
xlabel("IT2   (A)","FontWeight","bold");
ylabel("VT2   (V)","FontWeight","bold");
title("Γεννήτρια υπό φορτίο");

P1 = polyfit(IT2,VT2,1);
y1fit = P1(1)*IT2+P1(2);
hold on;
plot(IT2,y1fit,'g','DisplayName',"fit, IF2 = 0.55 A");
legend;