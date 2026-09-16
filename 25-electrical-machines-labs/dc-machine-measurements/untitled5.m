clear;
n_130 = [746 746 744 739 732 724 720 715 710 708];
IT1_130 = [1 2.5 3 3.5 4.2 4.8 5.5 6 6.5 7];

IT1_260 = [2.5 3.7 4.5 5.7 6.7 8 9.3 10.5 12 13.5];
n_260 = [1526 1516 1507 1500 1490 1478 1466 1454 1442 1432];
figure(1)
plot(IT1_130, n_130,'Marker','o','DisplayName',"VT1 = 130 V");
xlabel("IT1 (A)","FontWeight","bold");
ylabel("n (rpm)","FontWeight","bold");
title("Κινητήρας υπό φορτίο με τροφοδοσία 130 V","FontWeight","bold");
ylim([0 inf]);
P1 = polyfit(IT1_130, n_130,1);
y1fit = P1(1)*IT1_130+P1(2);
hold on;
plot(IT1_130,y1fit,'g','DisplayName',"fit, VT1 = 130 V");
legend;

figure(2)
plot(IT1_260, n_260,'Marker','o','DisplayName',"VT1 = 260 V");
xlabel("IT1 (A)","FontWeight","bold");
ylabel("n (rpm)","FontWeight","bold");
title("Κινητήρας υπό φορτίο με τροφοδοσία 260 V","FontWeight","bold");
ylim([0 inf]);

P2 = polyfit(IT1_260, n_260,1);
y2fit = P2(1)*IT1_260+P2(2);
hold on;
plot(IT1_260,y2fit,'g','DisplayName',"fit, VT1 = 260 V");
legend;

