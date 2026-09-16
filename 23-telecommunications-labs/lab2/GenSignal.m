function GenSignal(AM)
clc;
if isnumeric(AM) == 0 || AM > 999 || AM < 0
    display('ERROR: '); 
    return;
else
    if AM < 100
        AM = AM + 300;
    else
        AM = AM;
    end
    f1 = AM;
    f2 = 2500;
    
    FILENAME = ['res_' num2str(AM, '%03d') '.mat'];
    save(FILENAME, 'f1', 'f2');
   
end

end