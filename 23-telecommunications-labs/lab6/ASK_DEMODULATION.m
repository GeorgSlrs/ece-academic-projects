%Πρόγραμμα Προσομοίωσης Δέκτη (B)ΑSK/ΟΟΚ
%Remember (in OCTAVE) to key in the command window: pkg load communications
clear all;      %Σβήνονται από την μνήμη όλες οι μεταβλητές
close all;   	%Κλείνουν όλα τα παράθυρα πλην του «command window»
clc;			%Καθαρισμός του «command window»
%pi=3.14159;	%π
Fs =960; 		%Παράμετρος διακριτότητας χρόνου
max_Hz=30;      %Maximum value in the Hz-axis
step_Hz=1;      %Βήμα - ticks in the Hz-axis
n=2^16;    		%Παράμετρος υπολογισμού τιμών FFT
SNR=50;          %Signal to Noise Ratio (σε περίπτωση παρουσίας θορύβου AWGN)
A=1;			%Το πλάτος του φορέα
f_c = 12; 		%Συχνότητα του φορέα σε Hz
f=3.5;   			%Συχνότητα των data bits σε bps
Tb=1/f;    		%Περίοδος συμβόλων = Περίοδο bits (για B-ASK)
Vp = 1;         %Πλάτος των bits σε Volts αν bit = "1"
threshold=Vp/100;     %Κατώφλι σύγκρισης στον Δέκτη για το "1" ή το "0".
Spcm = [1 0 1 0 1 0 1]; 	%Τα bits που μετέδωσε ως πομπός;
total=size(Spcm,2);       	%Tο πλήθος τους  
org_bits=[];            % βοηθητικός πίνακας για την αναπαράσταση των bits
%--------Αναπαράσταση των data bits (Spcm)--------
t=0:1/Fs:total*Tb;      %Mεταβλητή χρόνου (Tb*total = συνολική διάρκεια συμβόλων)
subplot(6,1,1);         %Το σχήμα θα περιλαμβάνει 6 διαγράμματα, το ένα κάτω από το άλλο.
  stem(Spcm);           %Στην θέση 1 (1ο διάγραμμα) του σχήματος 1, τα bits ως 0 ή 1
  xlabel('Bit number')
  ylabel('Amplitude')
  title('Data bits to be transmitted')
  axis([0 total 0 1]);      %’ξονας x από 0 μέχρι total. ’ξονας y από 0 μέχρι 1, αφού Vp=1 V.
  set(gca,'XTick',0:1:total);
  set(gca,'YTick',0:0.5:1);
  grid on;
  hold on;
%--------Δημιουργία του σήματος m_ASK/OOK--------
t1=0; 				%Μεταβλητή Χρόνου
t2=Tb;           	%Μεταβλητή Χρόνου
for index=1:total  	%Για κάθε data bit, αντιστοιχεί χρονικό διάστημα [t1, t2]
t =[t1:1/Fs:t2];   	 %Διακριτότητα χρόνου 1/Fs
m_ASK(index,:)=zeros(1,length(t));
c=A*cos(2*pi*f_c*t);   %Φορέας
if Spcm(index)==1      %Αν bit = "1"
    m_ASK(index,:)=c;  %ASK/OOK = φορέα συχνότητας f_c
    org_bits(index,:) = ones(1, length(t)); %Βοηθητικός πίνακας για αναπαράσταση
else                   %Αν bit = "0"
    %m_ASK(index,:)=0;  %ASK/OOK = 0
    m_ASK(index,:)=zeros(1, length(c));   %ASK/OOK = 0
    org_bits(index,:) = zeros(1, length(t)); %Βοηθητικός πίνακας για αναπαράσταση
end
subplot(6,1,2);        
  %plot(t,Spcm(index),'b');  %Στην θέση 2 του σχήματος, τα bits ως μονοπολική παλμοσειρά.
  plot(t, org_bits(index,:), 'b');
  title('Data Βits to be transmitted (Unipolar line coding)');
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb 0 1]); 	      %’ξονας x (από 0 μέχρι total*Tb). ’ξονας y από 0 μέχρι 1, αφού Vp=1 V.
  set(gca,'XTick',0:Tb:total*Tb);
  set(gca,'YTick',0:0.5:1);
  grid on; hold on;
subplot(6,1,3);
  plot(t, c,'b'); 				 %Στην θέση 3 (3ο διάγραμμα) του σχήματος, o φορέας - χρώμα μπλε.
  title('Σήμα Carrier');
  xlabel('Time (seconds)');
  ylabel('Amplitude');
  axis([0 total*Tb -1.5 1.5]);    %’ξονας x (από 0 μέχρι Total*Tb). ’ξονας y από -1.5 μέχρι 1.5.
  set(gca,'XTick',0:Tb:total*Tb);
  grid on; hold on;
m_ASK_noise(index, :)=awgn(m_ASK(index, :),SNR);
subplot(6,1,4);
  plot(t, m_ASK_noise(index,:));  %Στην θέση 4 του σχήματος, το σήμα ASΚ/OOK με θόρυβο AWGN.
  title(['ASK/OOK Signal + AWGN with SNR = ', num2str(SNR)]);
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb -2.0 2.0]);    %’ξονας x από 0 μέχρι total*Tb. ’ξονας y από -2 μέχρι +2.
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
y1=[];
x1=[];
y2=[];
x2=[];
  y1=c.*m_ASK(index,:);           %Πολλαπλασιασμός στον δέκτη με τον τοπικό ταλαντωτή c
  y2=c.*m_ASK_noise(index,:);     %Πολλαπλασιασμός στον δέκτη με τον τοπικό ταλαντωτή c
  x1=trapz(t,y1);                 %Ολοκλήρωση στο χρονικό διάστημα ενός bit-συμβόλου (Tb)
  x2=trapz(t,y2);                 %Ολοκλήρωση στο χρονικό διάστημα ενός bit-συμβόλου (Tb)
%decision device 
 if x1>threshold
 Spcm_receiver(index)=1; 
 else 
 Spcm_receiver(index)=0; 
end 
 if x2>threshold
 Spcm_receiver_noise(index)=1; 
 else 
 Spcm_receiver_noise(index)=0; 
 end 
t1=t1+Tb; 
t2=t2+Tb; 
end 
%Plotting the demodulated data bits 
subplot(6,1,5);
  stem(Spcm_receiver); 
  title('Demodulated data - ΑΠΟΥΣΙΑ Θορύβου');
  xlabel('Bit number')
  ylabel('Amplitude')
  axis([0 total 0 1]);            %’ξονας x από 0 μέχρι total. ’ξονας y από 0 μέχρι 1, αφού Vp=1 V.
  set(gca,'XTick',0:1:total);
  set(gca,'YTick',0:0.5:1);
  grid on; hold on;
subplot(6,1,6);
  stem(Spcm_receiver_noise); 
  title(['Demodulated data - ΠΑΡΟΥΣΙΑ Θορύβου with SNR = ', num2str(SNR)]);
  xlabel('Bit number')
  ylabel('Amplitude')
  axis([0 total 0 1]);            %’ξονας x από 0 μέχρι total. ’ξονας y από 0 μέχρι 1, αφού Vp=1 V.
  set(gca,'XTick',0:1:total);
  set(gca,'YTick',0:0.5:1);
  grid on; hold on;