clc;
clear all;

Pos_Pwm=[128
138
148
158
168
178
188
198
208
218
228
238
248
255
];

Neg_Pwm=[0
10
20
30
40
50
60
70
80
90
100
110
120
128
];

Corr=[127
127
127
127
127
127
127
127
127
127
127
127
127
127
];


T_rise_p=[0.1
0.1
0.3
0.6
1.0
1.1
0.9
0.9
0.9
1.6
1.1
1.1
1.1
];

T_rise_n=[0.05
0.1
0.1
0.1
0.65
1.3
1.2
0.55
0.65
0.7
1.2
0.9
1.0];

Res_pos=[4
9
13
13.5
14
16
17.5
17.5
18
20.5
21
21
21
25
];

Res_neg=-[24
22
21
20
18
18
16
14
13
11
9
7
7
5];

%xc1=canon(Pos_Pwm,2.5,1.18);
%yc1=canon(Res_pos,1.3,27.8);%we peek the max deviration
polyfit(Pos_Pwm,Res_pos,1)
fit(Pos_Pwm,Res_pos,1,"fit1","xf","yf",1)
%K=0.1258
%t_i=0.8308
%G_p(s)=0.1258/(0.8308s+1)

%xc2=canon(Neg_Pwm+Corr,2.5,1.18);
%yc2=canon(Res_neg,5,27.5);
polyfit(Neg_Pwm,Res_neg,1)
fit(Neg_Pwm,Res_neg,1,"fit2","xf","yf",2)
%K=0.1474
%t_i=0.6538
%G_n(s)=0.1474/(0.6538s+1)


%M(s)=0.1/(0.5s+1)
function B=canon(A,dmax,dleit)
    B=ones(1,length(A));
    for n = 1:length(A)
        B(n) =(A(n)-dleit)/dmax;
    
    end
end


function f = fit(x,y,n,t,xt,yt,fff)
    figure(fff)
    
    eff = polyfit(x, y, n); 
    xfit=min(x):0.01:max(x);
    yfit=polyval(eff,xfit);
    scatter(x,y);
    
    hold on;
    plot(xfit,yfit);
    title(t);
    xlabel(xt);
    ylabel(yt);

end