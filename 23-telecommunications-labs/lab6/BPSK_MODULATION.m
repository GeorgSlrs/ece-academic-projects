%Πρόγραμμα Προσομοίωσης Πομπού (B)PSK 
%--------Υπενθύμιση: Για OCTAVE, load the signal package: pkg load signal--------
%--------Υπενθύμιση: Για OCTAVE, load the signal package: pkg load communications--------
clear all;              %Σβήνονται από την μνήμη όλες οι μεταβλητές
close all;              %Κλείνουν όλα τα παράθυρα πλην του «command window»
clc;                    %Καθαρισμός του «command window»
pi=3.14159;			
duty=50;   				%Παράμετρος duty cycle (στην συνάρτηση square)
Fs = 960; 				%Παράμετρος διακριτότητας χρόνου
SNR=2.5;                %απoυσία θορύβου το κάνω comment out, για το i γίνεται 5
max_Hz=30;       		%Maximum value in the Hz-axis
step_Hz=1;        		%Βήμα - ticks in the Hz-axis
max_amplitude_1=2500;   %Maximum Amplitude for FFT plots 
max_amplitude_2=500;    %Maximum Amplitude for FFT plots 
n=2^16;    				%Παράμετρος υπολογισμού τιμών FFT
A=sqrt(2);				%Το πλάτος του φορέα
f_c = 15; 				%Συχνότητα του φορέα σε Hz
f=4;     				%για το ΑΠ1 ΕΊΝΑΙ 2
Tb=1/f;    				%Περίοδος συμβόλων = Περίοδο bits (για BPSK)
Spcm = [1 0 1 0 1 0 1];  	%Τα προς μετάδοση bits;
total=size(Spcm,2);       	%Tο πλήθος τους  
org_bits=[];            % βοηθητικός πίνακας για την αναπαράσταση των bits
%--------Αναπαράσταση των data bits (Spcm)--------
t=0:1/Fs:total*Tb;              %Mεταβλητή χρόνου (Tb*total = συνολική διάρκεια συμβόλων)
y_sq =square(2*pi*(f/2)*t, duty);	%Tα bits ως ένα (βοηθητικό) ορθογώνιο περιοδικό σήμα!!!
%--------Πρώτο σχήμα--------
figure(1);
subplot(5,1,1);					%Το σχήμα 1 θα περιλαμβάνει 5 διαγράμματα, το ένα κάτω από το άλλο
  stem(Spcm);
  title('Data Βits to be transmitted');
  xlabel('Bit number');
  ylabel('Amplitude');
  grid on; hold on;
  axis([0 total 0 1.0]);
  set(gca,'XTick',0:1:total); 		%Η αρίθμηση στον άξονα x από 0 μέχρι total(=8) με βήμα 1
%--------Κωδικοποιούμε τα προς μετάδοση bits με Polar_NRZ line coding --------
Vp=1; 							    %Vp είναι το πλάτος απολύτου τιμής (Volts) των διπολικών παλμών NRZ.
t1=0;      							%Mεταβλητή χρόνου
t2=Tb;     							%Mεταβλητή χρόνου
for index=1:total
t=[t1:1/Fs:t2];						%Διακριτότητα χρόνου ώστε να δημιουργήσουμε ορθογώνιο διπολικό παλμό.
if Spcm(index)==1
    org_bits(index,:) = ones(1, length(t));
elseif Spcm(index)==0
    org_bits(index,:) = zeros(1, length(t));
end
subplot(5,1,2);        
  plot(t, Spcm(index)); 				%Στην θέση 2 του σχήματος 1, τα bits ως (μονο)πολική παλμοσειρά.
  plot(t, org_bits(index,:), 'b');
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  title('Data Βits to be transmitted (Unipolar line coding)');
  grid on; hold on;
  axis([0 total*Tb 0 1]); 				%’ξονας x (από 0 μέχρι 8). ’ξονας y από 0 μέχρι 1.
  set(gca,'XTick',0:Tb:total*Tb);
%--------Δημιουργία του σήματος Polar NRZ (line coding των data bits)--------
if Spcm(index)==1
  Polar_NRZ(index,:)=ones(1,length(t))*Vp;
elseif Spcm(index)==0
  Polar_NRZ(index,:)=ones(1,length(t))*(-Vp);
end
subplot(5,1,3);						%Στην θέση 3 του σχήματος 1, το σήμα Polar NRZ
  plot(t, Polar_NRZ(index,:),'b'); 
  xlabel('Time (seconds)');
  ylabel('Volts');
  title('Generated symbols (Polar line coding)');
  grid on; hold on;
  axis([0 total*Tb -1.5 1.5]);   	%’ξονας x (από 0 έως 8), ενώ άξονας y από -1.5 μέχρι 1.5.
  set(gca,'XTick',0:Tb:total*Tb);
t1=t1+Tb; 
t2=t2+Tb;
end
%--------Φάσμα Συχνοτήτων (MF απολύτου τιμής) των bits--------
y = abs(fft(y_sq, n));				%Βάσει του βοηθητικού σήματος των ορθογωνίων περιοδικών παλμών
y = fftshift(y);
MF = Fs*(-n/2:n/2-1)/n;
subplot(5, 1, 4);
plot(MF, y);						%Στην θέση 4 του σχήματος 1, το εύρος ζώνης συχνοτήτων των data bits
title('Spectrum of symbols based on Bit Rate');
xlabel('Frequency (Hz)');
ylabel('|Amplitude|');
axis([-max_Hz max_Hz 0 max_amplitude_1]);
set(gca,'XTick',-max_Hz:step_Hz:max_Hz);
grid on; hold on;
%--------Ας δούμε και το βοηθητικό σήμα των ορθογωνίων περιοδικών παλμών--------
t=[0:1/Fs:total*Tb];						
subplot(5,1,5);        
  plot(t, y_sq,'b'); 				%Στην θέση 5 του σχήματος 1, το βοηθητικό σήμα των ορθογωνίων περιοδικών παλμών
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  title('Orthogonal periodic pulses');
  axis([0 total*Tb -2 2]); 			%’ξονας x (από 0 μέχρι 8). ’ξονας y από -2 μέχρι 2
  set(gca,'XTick',0:Tb:total*Tb); 
  grid on; hold on;
%--------Δεύτερο σχήμα--------
figure(2);
%--------Ο φορέας και το σήμα m_PSK--------
t1=0;
t2=Tb;
for index=1:total
t=[t1:1/Fs:t2];
c=A*cos(2*pi*f_c*t);
m_PSK(index,:)=c.*Polar_NRZ(index,:);
m_PSK_noise(index, :)=awgn(m_PSK(index, :),SNR); %όχι θόρυβος -> comment out this
subplot(5,1,1);					%Το σχήμα 2 περιλαμβάνει 5 διαγράμματα, το ένα κάτω από το άλλο
  plot(t, c, 'b'); 				%Στην θέση 1 του σχήματος 2, ο φορέας με μπλε χρώμα
  title('Carrier (cos)');
  xlabel('Time (seconds)');
  ylabel('Volts');
  axis([0 total*Tb -1.5 1.5]);    %0 μέχρι 1 s
  set(gca,'XTick',0:Tb:total*Tb); %0:Tb:total*Tb  βήμα Tb=1/f
  grid on; hold on;
subplot(5,1,2);
  plot(t, m_PSK(index,:),'r'); 	%Στην θέση 2 του σχήματος 2, το σήμα PSK με κόκκινο χρώμα
  xlabel('Time (seconds)');
  ylabel('Volts');
  title('Binary PSK signal');
  grid on; hold on;
  axis([0 total*Tb -1.5 1.5]);      %total*Tb
  set(gca,'XTick',0:Tb:total*Tb);   %0:Tb:total*Tb
subplot(5,1,3);
  plot(t, m_PSK_noise(index,:));    %Στην θέση 3 του σχήματος 2, το σήμα 
  
  xlabel('Time (seconds)');
  ylabel('Volts');
  title(['Binary PSK signal + AWGN with SNR=',num2str(SNR)]);
  grid on; hold on;
  axis([0 total*Tb -2 2]);          %total*Tb
  set(gca,'XTick',0:Tb:total*Tb);   %0:Tb:total*Tb
t1=t1+Tb; 
t2=t2+Tb;
end
%--------Φάσμα Συχνοτήτων (MF απολύτου τιμής) του φορέα --------
y = abs(fft(c, n));
y = fftshift(y);
MF = Fs*(-n/2:n/2-1)/n;     %’ξονας συχνοτήτων (αρνητικός, θετικός)
subplot(5,1,4);
  plot(MF, y);              %Στην θέση 4 του σχήματος 2, το εύρος ζώνης συχνοτήτων του φορέα
  xlabel('Frequency (Hz)');
  ylabel('|Amplitude|');
  title('Frequency Spectrum of Carrier');
  axis([-max_Hz max_Hz 0 max_amplitude_2]);
  set(gca,'XTick',-max_Hz:step_Hz:max_Hz);
  grid on; hold on;
%--------Φάσμα Συχνοτήτων (MF απολύτου τιμής) του (B)PSK --------
t=[0:1/Fs:total*Tb];     
c=A*cos(2*pi*f_c*t);
m_PSK=c.*y_sq;				%Το εύρος ζώνης συχνοτήτων του m_PSK βάσει του βοηθητικού σήματος
y = abs(fft(m_PSK, n));
y = fftshift(y);
MF = Fs*(-n/2:n/2-1)/n;		%’ξονας συχνοτήτων (αρνητικός, θετικός)
subplot(5,1,5);
  plot(MF, y); 				%Στην θέση 5 του σχήματος 2, το εύρος ζώνης συχνοτήτων του m_PSK
  xlabel('Frequency (Hz)');
  ylabel('|Amplitude|');
  title('Frequency Spectrum of (B)PSK');
  axis([-max_Hz max_Hz 0 max_amplitude_1]);
  set(gca,'XTick',-max_Hz:step_Hz:max_Hz);
  grid on; hold on;