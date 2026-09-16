function [a1,a0] = calculateCoef(sumX,sumY,sumXY,sumX2,sumXY2,n)

a1 = (n*sumXY - sumX*sumY)/ (n*sumX2 - (sumX)^2);
a0 = (sumX2*sumY  - sumXY*sumX)/(n*sumX2 - (sumX)^2);
end