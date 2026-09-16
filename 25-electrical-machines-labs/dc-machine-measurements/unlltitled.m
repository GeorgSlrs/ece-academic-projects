%% 4.1.1
% IF1 = 0.76A
% n = 700
clear;
IF2_700 = [0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1];
VT2_700 = [0 22 35 48 62 78 88 96 105 110 115 120];
CF2_700 = VT2_700./73.27 ; 

% n = 1400
IF2_1400 = [0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1];
VT2_1400 = [0 38 68 95 122 150 172 190 208 220 230 242];
CF2_1400 = VT2_1400./146.5 ;

figure(1)
plot(IF2_700, VT2_700, 'Marker','o','DisplayName',"n = 700 rpm");
hold on;
plot(IF2_1400, VT2_1400, 'Marker','o','DisplayName',"n = 1400 rpm");
xlabel("IF2   (A)","FontWeight","bold");
ylabel("VT2   (V)","FontWeight","bold");
title("Γεννήτρια εν κενώ στις 700 και 1400 rpm");
legend;


figure(2)
plot(IF2_700, CF2_700, 'Marker','o','DisplayName',"n = 700 rpm");
hold on;
plot(IF2_1400, CF2_1400, 'Marker','o','DisplayName',"n = 1400 rpm");
xlabel("IF2   (A)","FontWeight","bold");
ylabel("CΦ2   (Vs/rad)","FontWeight","bold");
title("Γεννήτρια εν κενώ στις 700 και 1400 rpm");

% Linear fit with constraint to pass through the origin
f = fittype('a*x', 'independent', 'x', 'coefficients', {'a'});

% Fit for n = 700 rpm
[fitresult1, ~] = fit(IF2_700', CF2_700', f);

% Plot the fit for n = 700 rpm
plot(IF2_700, fitresult1(IF2_700), 'g', 'DisplayName', "fit, n = 700 rpm");

% Fit for n = 1400 rpm
[fitresult2, ~] = fit(IF2_1400', CF2_1400', f);

% Plot the fit for n = 1400 rpm
plot(IF2_1400, fitresult2(IF2_1400), 'm', 'DisplayName', "fit, n = 1400 rpm");

legend;
