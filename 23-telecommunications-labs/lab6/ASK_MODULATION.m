%Πρόγραμμα Προσομοίωσης Πομπού (B)ΑSK/ΟΟΚ
%Remember (in OCTAVE) to key in the command window: pkg load signal
%Remember (in OCTAVE) to key in the command window: pkg load communications
clear all;          %Σβήνονται από την μνήμη όλες οι μεταβλητές
close all;     		%Κλείνουν όλα τα παράθυρα πλην του «command window»
clc;            	%Καθαρισμός του «command window»
%pi=3.14159;		%π
duty=50;   			%Παράμετρος duty cycle (στην συνάρτηση square)
Fs =960; 			%Παράμετρος διακριτότητας χρόνου
max_Hz=30;       	%Maximum value in the Hz-axis
step_Hz=1;          %Βήμα - ticks in the Hz-axis
n=2^16;    		   	%Παράμετρος υπολογισμού τιμών FFT%
SNR=2.5;             %Signal to Noise Ratio (σε περίπτωση παρουσίας θορύβου AWGN)
A=1;				%Το πλάτος του φορέα
f_c = 12; 			%Συχνότητα του φορέα σε Hz
f=7;   				%Συχνότητα των data bits σε bps 
Tb=1/f;    			%Περίοδος συμβόλων = Περίοδο bits (για B-ASK)
Vp = 1;             %Πλάτος των bits σε Volts αν bit = "1"
Spcm = [1 0 1 0 1 0 1];  	%Τα bits που μετέδωσε ο πομπός
total=size(Spcm,2);       	%Tο πλήθος τους  
org_bits=[];            % βοηθητικός πίνακας για την αναπαράσταση των bits
%--------Αναπαράσταση των data bits (Spcm)--------
t=0:1/Fs:total*Tb;        		  %Mεταβλητή χρόνου (Tb*total = συνολική διάρκεια συμβόλων)
y_sq =(Vp/2)*square(2*pi*(f/2)*t, duty)+(Vp/2);	 %Tα bits ως ένα (βοηθητικό) ορθογώνιο περιοδικό σήμα!!!
figure(1);
subplot(5,1,1);          %Το σχήμα 1 θα περιλαμβάνει 5 διαγράμματα, το ένα κάτω από το άλλο.
  stem(Spcm);            %Στην θέση 1 (1ο διάγραμμα) του σχήματος 1, τα bits ως 0 ή 1
  xlabel('Bit number')
  ylabel('Amplitude')
  title('Data bits to be transmitted')
  axis([0 total 0 1]);    			%’ξονας x από 0 μέχρι total. ’ξονας y από 0 μέχρι 1, αφού Vp=1 V.
  set(gca,'XTick',0:1:total);
  set(gca,'YTick',0:0.5:1);
  grid on; hold on;
%--------Δημιουργία του σήματος m_ASK/OOK--------
t1=0; 					%Μεταβλητή Χρόνου
t2=Tb;           		%Μεταβλητή Χρόνου
for index=1:total  		%Για κάθε data bit, αντιστοιχεί χρονικό διάστημα [t1, t2]
t =[t1:1/Fs:t2];   		%Διακριτότητα χρόνου 1/Fs
 c=A*cos(2*pi*f_c*t); 	%Φορέας
if Spcm(index)==1       %Αν bit = "1"
    m_ASK(index,:)=c; 	%ASK/OOK = φορέα συχνότητας f_c
    org_bits(index,:) = ones(1, length(t)); %Βοηθητικός πίνακας για αναπαράσταση
else                    %Αν bit = "0"
    m_ASK(index,:)=zeros(1, length(c));   %ASK/OOK = 0
    %m_ASK(index,:) = 0;
   org_bits(index,:) = zeros(1, length(t));
end
subplot(5,1,2);        
  %plot(t, Spcm(index), 'b'); 	%Στην θέση 2 του σχήματος 1, τα bits ως μονοπολική παλμοσειρά.
  plot(t, org_bits(index,:), 'b');
  title('Data Βits to be transmitted (Unipolar line coding)');
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb 0 1]);      %’ξονας x (από 0 μέχρι Total*Tb). ’ξονας y από 0 μέχρι 1, αφού Vp=1 V.
  set(gca,'XTick',0:Tb:total*Tb);
  set(gca,'YTick',0:0.5:1);
  grid on; hold on;
subplot(5,1,3);
  plot(t, c,'b'); 			%Στην θέση 3 (3ο διάγραμμα) του σχήματος 1, o φορέας - χρώμα μπλε.
  title('Σήμα Carrier');
  xlabel('Time (seconds)');
  ylabel('Amplitude');
  axis([0 total*Tb -1.5 1.5]);  %’ξονας x (από 0 μέχρι Total*Tb). ’ξονας y από -1.5 μέχρι 1.5.
  set(gca,'XTick',0:Tb:total*Tb);
  grid on; hold on;
subplot(5,1,4);
  plot(t,m_ASK(index,:),'r');   %Στην θέση 4 του σχήματος 1, το σήμα ASΚ/OOK - χρώμα κόκκινο.
  title('Σήμα ASK')
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb -1.5 1.5]);  %’ξονας x από 0 μέχρι total. ’ξονας y από -1.5 μέχρι +1.5.
  set(gca,'XTick',0:Tb:total*Tb);
  grid on; hold on;
   m_ASK_noise(index, :)=awgn(m_ASK(index, :),SNR);
subplot(5,1,5);
  plot(t, m_ASK_noise(index,:));%Στην θέση 5 του σχήματος 1, το σήμα ASΚ/OOK με θόρυβο AWGN.
  title(['ASK/OOK Signal + AWGN with SNR = ', num2str(SNR)]);
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb -1.5 1.5]);  %’ξονας x από 0 μέχρι total. ’ξονας y από -1.5 μέχρι +1.5
  set(gca,'XTick',0:Tb:total*Tb);
  grid on; hold on;
t1=t1+Tb;
t2=t2+Tb;
end
figure(2);
%--------Ας δούμε το βοηθητικό σήμα των ορθογωνίων περιοδικών παλμών--------
t=[0:1/Fs:total*Tb];
subplot(4,1,1);
  plot(t, y_sq,'b');      %Στην θέση 1 του σχήματος 2, το βοηθητικό σήμα των ορθογωνίων περιοδικών παλμών
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  title('Orthogonal periodic pulses');
  axis([0 total*Tb -1 1]); 	    %’ξονας x (από 0 μέχρι Total*Tb). ’ξονας y από -1 μέχρι 1
  set(gca,'XTick',0:Tb:total*Tb); 
  grid on; hold on;
%--------Φάσμα Συχνοτήτων (MF απολύτου τιμής) των bits--------
y = abs(fft(y_sq, n));          %Βάσει του βοηθητικού σήματος των ορθογωνίων περιοδικών παλμών
y = fftshift(y);
MF = Fs*(-n/2:n/2-1)/n;
subplot(4, 1, 2);
  plot(MF, y);				          %Στην θέση 2 του σχήματος 2, το εύρος ζώνης συχνοτήτων των data bits
  title('Spectrum of symbols based on Bit Rate');
  xlabel('Frequency (Hz)');
  ylabel('|Amplitude|');
  axis([-max_Hz, max_Hz, min(y), max(y)]);
  set(gca,'XTick',-max_Hz:step_Hz:max_Hz);
  grid on; hold on;
%--------Φάσμα Συχνοτήτων (MF απολύτου τιμής) του φορέα--------
y = abs(fft(c, n));             %Μετασχηματισμός Fourier του φορέα
y = fftshift(y);
MF = Fs*(-n/2:n/2-1)/n;		      %’ξονας συχνοτήτων (αρνητικός, θετικός)
subplot(4,1,3);
  plot(MF, y, 'lineWidth',1.5); %Στην θέση 3 του σχήματος 2, το εύρος ζώνης συχνοτήτων του φορέα
  xlabel('Frequency (Hz)');
  ylabel('|Amplitude|');
  title('Frequency Spectrum of Carrier');
  axis([-max_Hz, max_Hz, min(y), max(y)]);
  set(gca,'XTick',-max_Hz:step_Hz:max_Hz);
  grid on; hold on;
%--------Φάσμα Συχνοτήτων (MF απολύτου τιμής) του ΑSK--------
t1=0;
t2=Tb;                          %Μεταβλητή Χρόνου
for index=1:total               %Για κάθε data bit i, αντιστοιχεί χρονικό διάστημα [t1, t2]
t =[t1:1/Fs:t2];                %Διακριτότητα χρόνου 1/Fs
m_ASK=[];
for in=1:total
 if Spcm(in)==1
 y=A*cos(2*pi*f_c*t);
 else
 y=0;
 end
m_ASK=[m_ASK y];
end
t1=t1+Tb;
t2=t2+Tb;
end
y = abs(fft(m_ASK, n));         %Μετασχηματισμός Fourier του m_ΑSK
y = fftshift(y);
MF = Fs*(-n/2:n/2-1)/n;	        %’ξονας συχνοτήτων (αρνητικός, θετικός)
subplot(4,1,4);
  plot(MF, y); 		              %Στην θέση 4 του σχήματος 2, το εύρος ζώνης συχνοτήτων του m_ΑSK
  xlabel('Frequency (Hz)');
  ylabel('|Amplitude|');
  title('Frequency Spectrum of ASK');
  axis([-max_Hz, max_Hz, min(y), max(y)]);
  set(gca,'XTick',-max_Hz:step_Hz:max_Hz);
  grid on; hold on;