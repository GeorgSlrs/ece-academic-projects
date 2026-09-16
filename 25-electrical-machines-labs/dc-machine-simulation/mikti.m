clc;
clear;
close all;
j=0;

A = 0:-1:-50;




s = length(A);
for i= 1:s
    l=A(i);
    j = j+1;
    sim("mikti_sim.slx",2);
    
    TorqueTable(j) = -TORQUE.signals.values;
    SpeedTable(j) = -SPEED.signals.values;
    
end

figure;
plot(TorqueTable,SpeedTable, '-o', 'MarkerSize', 5, 'LineWidth', 2, 'MarkerEdgeColor', 'red', 'MarkerFaceColor', 'yellow');
xlabel('Me (Nm)');
ylabel('RPM');
ylim([0 inf]);
title('RPM vs Torque (Me) Plot');
grid on;
legend('RPM vs Electromagnetic Torque', 'Location', 'best');
set(gca, 'FontSize', 12); 
set(gca, 'LineWidth', 1.5); 
box on; 
