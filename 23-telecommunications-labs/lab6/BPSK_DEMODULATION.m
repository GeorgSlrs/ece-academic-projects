%Πρόγραμμα Προσομοίωσης Δέκτη (B)PSK Remember (in OCTAVE)to key in the
%command window: pkg load communications
clear all;      %Σβήνονται από την μνήμη όλες οι μεταβλητές
close all;      %Κλείνουν όλα τα παράθυρα πλην του «command window»
clc;            %Καθαρισμός του «command window»
%pi=3.14159;    %π
Fs = 960; 		%Παράμετρος διακριτότητας χρόνου
SNR=0.5;
A=sqrt(2);		%Το πλάτος του φορέα
f_c =15; 		%Συχνότητα του φορέα σε Hz
f=4;     		%Συχνότητα των data bits σε bps (σε Hz κριτήριο ο 1ος λοβός) 
Tb=1/f;    		%Περίοδος συμβόλων = Περίοδο bits (για BPSK)
Spcm = [1 0 1 0 1 0 1];  	%Τα λαμβανόμενα bits;
total=size(Spcm,2);       	%Tο πλήθος τους  
%--------Polar_NRZ (line coding των bits), ο φορέας και το σήμα
%m_PSK--------
Vp=1;
t1=0;
t2=Tb;
for index=1:total
t=[t1:1/Fs:t2];
if Spcm(index)==1
  Polar_NRZ(index,:)=ones(1,length(t))*Vp;
elseif Spcm(index)==0
  Polar_NRZ(index,:)=ones(1,length(t))*(-Vp);
end
subplot(6,1,1);		                  %6 διαγράμματα
  plot(t, Polar_NRZ(index,:),'b');    %Στην θέση 1 του σχήματος, το σήμα Polar NRZ 
  xlabel('Time (seconds)');
  ylabel('Volts');
  title('Generated symbols (Polar line coding)');
  grid on; hold on;
  axis([0 total*Tb -1.5 1.5]);        %’ξονας x (από 0 έως 8), ενώ άξονας y από -1.5 μέχρι 1.5.
  set(gca,'XTick',0:Tb:total*Tb);
c=A*cos(2*pi*f_c*t);
m_PSK=c.*Polar_NRZ(index,:);          %Το σήμα m_PSK χωρίς θόρυβο
m_PSK_noise=awgn(m_PSK,SNR);          %Το λαμβανόμενο σήμα m_PSK_noise με θόρυβο
subplot(6,1,2);
  if Spcm(index)==0  
   plot(t, m_PSK,'r'); 				%Στην θέση 2 του σχήματος, το σήμα PSK με κόκκινο χρώμα
  elseif Spcm(index)==1
   plot(t, m_PSK,'b'); 				%Στην θέση 2 του σχήματος, το σήμα PSK με μπλε χρώμα    
  end
  xlabel('Time (seconds)');
  ylabel('Volts');
  title('Binary PSK signal');
  grid on; hold on;
  axis([0 total*Tb -1.5 1.5]);        %total*Tb
  set(gca,'XTick',0:Tb:total*Tb);     %0:Tb:total*Tb
subplot(6,1,3);
  plot(t, m_PSK_noise);               %Στην θέση 3 του σχήματος, το σήμα PSΚ με θόρυβο AWGN.
  title(['ASK/OOK Signal + AWGN with SNR = ', num2str(SNR)]);
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb -2.0 2.0]);        %’ξονας x από 0 μέχρι total*Tb. ’ξονας y από -2 μέχρι +2.
  set(gca,'XTick',0:Tb:total*Tb);
  grid on; hold on;
subplot(6,1,4);
  plot(t, c, 'b'); 					%Στην θέση 4 του σχήματος, ο φορέας με μπλε χρώμα
  title('Local Carrier (cos)');
  xlabel('Time (seconds)');
  ylabel('Volts');
  axis([0 total*Tb -1.5 1.5]);        %0 μέχρι 1 s
  set(gca,'XTick',0:Tb:total*Tb);   %0:Tb:total*Tb  βήμα Tb=1/f
  grid on; hold on;
y=[ ];
x=[ ];
y=c.*m_PSK;                           %Πολλαπλασιασμός στον δέκτη με τοπικό ταλαντωτή
x=trapz(t,y);                         %ολοκλήρωση στο χρονικό διάστημα ενός bit (Tb)
if x>0 
Spcm_receiver(index)=1; 
else
Spcm_receiver(index)=0; 
end
%plot the demodulated data bits - no noise
subplot(6,1,5);
  stem(Spcm_receiver);                %Στην θέση 5 του σχήματος, τα λαμβανόμενα data bits απουσία θορύβου
  title('Demodulated data bits');
  xlabel('Bit number');
  ylabel('Amplitude');
  axis([0 total 0 1.0]);
  set(gca,'XTick',0:1:total); 	%Η αρίθμηση στον άξονα x από 0 μέχρι total(=8) με βήμα 1
  set(gca,'YTick',0:0.5:1); 	%Η αρίθμηση στον άξονα y από 0 μέχρι 1 με βήμα 0.5
  grid on; hold on;
y=[ ];
x=[ ];
y=c.*m_PSK_noise;               %Πολλαπλασιασμός στον δέκτη με τοπικό ταλαντωτή
x=trapz(t,y);                   %ολοκλήρωση στο χρονικό διάστημα ενός bit (Tb)
if x>0 
Spcm_receiver(index)=1; 
else
Spcm_receiver(index)=0; 
end
%plot the demodulated data bits in the presence of noise
  subplot(6,1,6);       %Στην θέση 6 του σχήματος, τα λαμβανόμενα data bits παρουσία θορύβου
  stem(Spcm_receiver); 
  title(['Demodulated data - ΠΑΡΟΥΣΙΑ Θορύβου with SNR = ', num2str(SNR)]);
  xlabel('Bit number');
  ylabel('Amplitude');
  axis([0 total 0 1.0]);
  set(gca,'XTick',0:1:total); 	%Η αρίθμηση στον άξονα x από 0 μέχρι total με βήμα 1
  set(gca,'YTick',0:0.5:1); 	%Η αρίθμηση στον άξονα y από 0 μέχρι 1 με βήμα 0.5
  grid on; hold on;
t1=t1+Tb; 
t2=t2+Tb;
end