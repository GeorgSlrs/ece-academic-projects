function GenSignal(AM)
clc;
if isnumeric(AM) == 0 || AM > 999 || AM < 0
    display('ERROR: '); 
    return;
else
    FILENAME = ['Freq' num2str(AM, '%03d') '.mat'];
end
load('Data.mat');
nm = mod(AM, 10)+1;

Fc = Fc(nm) ;
Fm = Fm(nm);

if mod(nm, 2) == 0
    if nm < 5
        Ac = Ac(2);
        Am = Am(2);
    else
        Ac = Ac(4);
        Am = Am(4);
    end
 
else
    if nm < 5
        Ac = Ac(1);
        Am = Am(1);
    else
        Ac = Ac(3);
        Am = Am(3);
    end
 

end
save(FILENAME, 'Ac', 'Am', 'Fc', 'Fm');
end