%Πρόγραμμα Προσομοίωσης Δέκτη FSK 
%In OCTAVE, remember to key in the command window: pkg load communications
clear all;  			%Σβήνονται από την μνήμη όλες οι μεταβλητές
close all;   			%Κλείνουν όλα τα παράθυρα πλην του «command window»
clc;					%Καθαρισμός του «command window»
%pi=3.14159;			%π
Fs=960; 	            %Παράμετρος διακριτότητας χρόνου (ακρίβεια υπολογισμών)
SNR=0.5;                  %Signal to Noise Ratio (σε περίπτωση παρουσίας θορύβου AWGN)
A=sqrt(2);				%Το πλάτος του φορέα
f_c1=24; 				%Συχνότητα του 1ου φορέα σε Hz (η υψηλή λέγεται mark)
f_c2=12; 				%Συχνότητα του 2ου φορέα σε Hz (η χαμηλή λέγεται space)
f=3.5;                    %Συχνότητα των data bits σε bps
Tb=1/f;    				%Περίοδος συμβόλων = Περίοδο bits (για BFSK)
Spcm = [1 0 1 0 1 0 1];  %Τα bits που μετέδωσε ο πομπός
org_bits=[];              %βοηθητικός πίνακας για την αναπαράσταση των bits
total=size(Spcm,2);       %Tο πλήθος τους  
%--------Αναπαράσταση των data bits (Spcm)--------
t=0:1/Fs:total*Tb;        %Mεταβλητή χρόνου (Tb*total = συνολική διάρκεια συμβόλων)
subplot(4,1,1);           %Το σχήμα θα περιλαμβάνει 4 διαγράμματα, το ένα κάτω από το άλλο.
  stem(Spcm);             %Στο 1ο διάγραμμα, τα bits ως 0 ή 1
  xlabel('Bit number')
  ylabel('Amplitude')
  title('Data bits sent by the Transmitter')
  axis([0 total 0 1]);    %’ξονας x από 0 μέχρι total. ’ξονας y από 0 μέχρι 1, αφού Vp=1 V.
  set(gca,'XTick',0:1:total);
  set(gca,'YTick',0:0.5:1);
  grid on; hold on;
%--------Δημιουργία του σήματος m_FSK--------
t1=0; 						        %Μεταβλητή Χρόνου
t2=Tb;           					%Μεταβλητή Χρόνου
for index=1:total  				%Για κάθε data bit, αντιστοιχεί χρονικό διάστημα [t1, t2]
t =[t1:1/Fs:t2];   				%Διακριτότητα χρόνου 1/Fs
 c1=A*cos(2*pi*f_c1*t); 	%Φορέας c1
 c2=A*cos(2*pi*f_c2*t); 	%Φορέας c2
if Spcm(index)==1         %Αν bit = "1"
    m_FSK(index,:)=c1;    %FSK = φορέα συχνότητας f_c1
    org_bits(index,:) = ones(1, length(t)); 
else                      %Αν bit = "0"
    m_FSK(index,:)=c2;    %FSK = φορέα συχνότητας f_c2
    org_bits(index,:) = zeros(1, length(t));
end
subplot(4,1,2);        
  %plot(t, Spcm(index), 'b'); 		%Στην θέση 2 του σχήματος, τα bits ως (μονο)πολική παλμοσειρά.
  plot(t, org_bits(index,:), 'b');
  title('Data Βits in Unipolar line coding');
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb 0 1]); 			%’ξονας x. ’ξονας y από 0 μέχρι 1, αφού Vp=1 V.
  set(gca,'XTick',0:Tb:total*Tb);
  set(gca,'YTick',0:0.5:1);
  grid on; hold on;
m_FSK_noise(index, :)=awgn(m_FSK(index, :),SNR);
subplot(4,1,3);
  plot(t, m_FSK_noise(index,:));%Στην θέση 3, το σήμα FSΚ + θόρυβος AWGN.
  title(['FSK Signal + AWGN with SNR = ', num2str(SNR)]);
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb -1.5 1.5]);  %’ξονας x από 0 μέχρι total. ’ξονας y από -1 μέχρι +1.
  set(gca,'XTick',0:Tb:total*Tb);
  grid on; hold on;
t1=t1+Tb;
t2=t2+Tb;
end
%DEMODULATION
t1=0;
t2=Tb; 
 for index=1:total
 t=[t1:1/Fs:t2];
%correlator = πολλαπλασιαστής + Φίλτρο(ολοκληρωτής) 
%  y1=c1.*m_FSK_noise(index,:);   %Πολλαπλασιασμός στον δέκτη με τοπικό ταλαντωτή c1
%  x1=trapz(t,y1);                %ολοκλήρωση στο χρονικό διάστημα ενός bit (Tb)
%  y2=c2.*m_FSK_noise(index,:);   %Πολλαπλασιασμός στον δέκτη με τοπικό ταλαντωτή c2
%  x2=trapz(t,y2);                %ολοκλήρωση στο χρονικό διάστημα ενός bit (Tb)
  x1=sum(c1.*m_FSK_noise(index,:)); 
  x2=sum(c2.*m_FSK_noise(index,:)); 
  x=x1-x2;
%decision device 
 if x>0 
 Spcm_receiver(index)=1; 
 else 
 Spcm_receiver(index)=0; 
 end 
 t1=t1+Tb; 
 t2=t2+Tb; 
 end 
%Plotting the demodulated data bits 
 subplot(4,1,4);
  stem(Spcm_receiver); 
  title('Demodulated data');
  xlabel('Bit number')
  ylabel('Amplitude')
  axis([0 total 0 1]);            %’ξονας x από 0 μέχρι total. ’ξονας y από 0 μέχρι 1, αφού Vp=1 V.
  set(gca,'XTick',0:1:total);
  set(gca,'YTick',0:0.5:1);
  grid on; hold on;