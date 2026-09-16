
%Πρόγραμμα Προσομοίωσης Πομπού FSK 
%Remember to key in the command window: pkg load signal
%Remember to key in the command window: pkg load communications
clear all;  		%Σβήνονται από την μνήμη όλες οι μεταβλητές
close all;   		%Κλείνουν όλα τα παράθυρα πλην του «command window»
clc;                %Καθαρισμός του «command window»
%pi=3.14159;		%π
duty=50;   			%Παράμετρος duty cycle (στην συνάρτηση square)
Fs =960; 			%Παράμετρος διακριτότητας χρόνου
max_Hz=40;            %Maximum value in the Hz-axis
step_Hz=1;            %Βήμα - ticks in the Hz-axis
max_amplitude_1=2500; %Maximum Amplitude for FFT plots 
max_amplitude_2=500;  %Maximum Amplitude for FFT plots 
n=2^16;    		   	%Παράμετρος υπολογισμού τιμών FFT
SNR=5;              %Signal to Noise Ratio (αν υπάρχει θόρυβος AWGN)
A=sqrt(2);			%Το πλάτος του φορέα
f_c1 = 24; 			%Συχνότητα του 1ου φορέα σε Hz
f_c2 = 12; 			%Συχνότητα του 2ου φορέα σε Hz
f=50;     			%Συχνότητα των data bits σε bps 
Tb=1/f;    			%Περίοδος συμβόλων = Περίοδος bits (για BFSK)
Spcm = [1 0 1 0 1 0 1];  % Τα προς μετάδοση bits
org_bits=[];            % βοηθητικός πίνακας για την αναπαράσταση των bits
total=size(Spcm,2);       % Tο πλήθος τους  
%--------Αναπαράσταση των data bits (Spcm)--------
t=0:1/Fs:total*Tb;        %Mεταβλητή χρόνου (Tb*total = συνολική διάρκεια συμβόλων)
%--------Υπενθύμιση: Για OCTAVE, load the signal package: pkg load signal--------
y_sq =square(2*pi*(f/2)*t, duty);	  %Tα bits ως ένα (βοηθητικό) ορθογώνιο περιοδικό σήμα!!!
figure(1);
subplot(6,1,1);                     %Το σχήμα 1 θα περιλαμβάνει 6 διαγράμματα, το ένα κάτω από το άλλο.
  stem(Spcm);                       %Στην θέση 1, τα bits ως 0 ή 1
  xlabel('Bit number')
  ylabel('Amplitude')
  title('Data bits to be transmitted')
  axis([0 total 0 1]);    %’ξονας x από 0 μέχρι total. ’ξονας y από 0 μέχρι 1.
  set(gca,'XTick',0:1:total);
  set(gca,'YTick',0:0.5:1);
  grid on;
  hold on;
%--------Δημιουργία του σήματος m_FSK--------
t1=0;
t2=Tb;                              %Μεταβλητή Χρόνου
for index=1:total                   %Για κάθε data bit i, αντιστοιχεί χρονικό διάστημα [t1, t2]
t =[t1:1/Fs:t2];                    %Διακριτότητα χρόνου 1/Fs
 c1=A*cos(2*pi*f_c1*t);             %Φορέας c1
 c2=A*cos(2*pi*f_c2*t);             %Φορέας c2
if Spcm(index)==1                   %Αν bit = "1"
    m_FSK(index,:)=c1;              %FSK = φορέα συχνότητας f_c1
    org_bits(index,:) = ones(1, length(t)); %Βοηθητικός πίνακας για αναπαράσταση
else                                %Αν bit = "0"
    m_FSK(index,:)=c2;              %FSK = φορέα συχνότητας f_c2
    org_bits(index,:) = zeros(1, length(t));
end

subplot(6,1,2);        
  %plot(t, Spcm(index), 'b'); 				%Στην θέση 2 του σχήματος 1, τα bits ως μονοπολική παλμοσειρά.
  plot(t, org_bits(index,:), 'b');
  title('Data Βits to be transmitted (Unipolar line coding)');
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb 0 1]); 					%’ξονας x. ’ξονας y από 0 μέχρι 1.
  set(gca,'XTick',0:Tb:total*Tb);
  set(gca,'YTick',0:0.5:1);
  grid on; hold on;
subplot(6,1,3);
  plot(t, c1,'b');                  %Στην θέση 3, o 1ος φορέας - χρώμα μπλε.
  title('Σήμα Carrier 1');
  xlabel('Time (seconds)');
  ylabel('Amplitude');
  axis([0 total*Tb -1.5 1.5]);      %’ξονας x. ’ξονας y από -1.5 μέχρι +1.5
  set(gca,'XTick',0:Tb:total*Tb);
  grid on; hold on;
subplot(6,1,4);
  plot(t, c2,'b');                  %Στην θέση 4, ο 2ος φορέας - χρώμα μπλε.
  title('Σήμα Carrier 2')
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb -1.5 1.5]);      %’ξονας x από 0 μέχρι total*Tb. ’ξονας y από -1.5 μέχρι +1.5
  set(gca,'XTick',0:Tb:total*Tb);
  grid on; hold on;
subplot(6,1,5);
  plot(t,m_FSK(index,:),'r');       %Στην θέση 3, το σήμα FSΚ - χρώμα κόκκινο.
  title('Σήμα FSK')
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb -1.5 1.5]);      %’ξονας x από 0 μέχρι total*Tb. ’ξονας y από -1.5 μέχρι +1.5
  set(gca,'XTick',0:Tb:total*Tb);
  grid on; hold on;
m_FSK_noise(index, :)=awgn(m_FSK(index, :),SNR);
subplot(6,1,6);
  plot(t, m_FSK_noise(index,:));
  title(['FSK Signal + AWGN with SNR = ', num2str(SNR)]);
  xlabel('Time (seconds)')
  ylabel('Amplitude')
  axis([0 total*Tb -1.5 1.5]);      %’ξονας x από 0 μέχρι total*Tb. ’ξονας y από -1.5 μέχρι +1.5
  set(gca,'XTick',0:Tb:total*Tb);
  grid on; hold on;
t1=t1+Tb;
t2=t2+Tb;
end
figure(2);
%--------Φάσμα Συχνοτήτων (MF απολύτου τιμής) των bits--------
y = abs(fft(y_sq, n));  %Βάσει του βοηθητικού σήματος των ορθογωνίων περιοδικών παλμών
y = fftshift(y);
MF = Fs*(-n/2:n/2-1)/n;
subplot(4, 1, 1);
  plot(MF, y);			%Στην θέση 4 του σχήματος 1, το εύρος ζώνης συχνοτήτων των data bits
  title('Spectrum of symbols based on Bit Rate');
  xlabel('Frequency (Hz)');
  ylabel('|Amplitude|');
  axis([-max_Hz max_Hz 0 max_amplitude_1]);
  set(gca,'XTick',-max_Hz:step_Hz:max_Hz);
  grid on; hold on;
%--------Φάσμα Συχνοτήτων (MF απολύτου τιμής) του 1ου φορέα--------
y = abs(fft(c1, n));                %Μετασχηματισμός Fourier του c1
y = fftshift(y);
MF = Fs*(-n/2:n/2-1)/n;		        %’ξονας συχνοτήτων (αρνητικός, θετικός)
subplot(4,1,2);
  plot(MF, y, 'lineWidth',1.5);     %Στην θέση 2 του σχήματος 2, το φάσμα συχνοτήτων του φορέα 1
  xlabel('Frequency (Hz)');
  ylabel('|Amplitude|');
  title('Frequency Spectrum of Carrier 1');
  axis([-max_Hz max_Hz 0 max_amplitude_2]);
  set(gca,'XTick',-max_Hz:step_Hz:max_Hz);
  grid on; hold on;
%--------Φάσμα Συχνοτήτων (MF απολύτου τιμής) του 2ου φορέα--------
y = abs(fft(c2, n));                %Μετασχηματισμός Fourier του c2
y = fftshift(y);
MF = Fs*(-n/2:n/2-1)/n;		          %’ξονας συχνοτήτων (αρνητικός, θετικός)
subplot(4,1,3);
  plot(MF, y, 'lineWidth',1.5);     %Στην θέση 3 του σχήματος 2, το φάσμα συχνοτήτων του φορέα 2
  xlabel('Frequency (Hz)');
  ylabel('|Amplitude|');
  title('Frequency Spectrum of Carrier 2');
  axis([-max_Hz max_Hz 0 max_amplitude_2]);
  set(gca,'XTick',-max_Hz:step_Hz:max_Hz);
  grid on; hold on;
%--------Φάσμα Συχνοτήτων (MF απολύτου τιμής) του FSK--------
t1=0;
t2=Tb;                   %Μεταβλητή Χρόνου
for index=1:total        %Για κάθε data bit i, αντιστοιχεί χρονικό διάστημα [t1, t2]
t =[t1:1/Fs:t2];         %Διακριτότητα χρόνου 1/Fs
m_FSK=[];
for in=1:total
 if Spcm(in)==1
 y=A*cos(2*pi*f_c1*t);
 else
 y=A*cos(2*pi*f_c2*t);
 end
m_FSK=[m_FSK y];
end
t1=t1+Tb;
t2=t2+Tb;
end
y = abs(fft(m_FSK, n));  %Μετασχηματισμός Fourier του m_FSK
y = fftshift(y);
MF = Fs*(-n/2:n/2-1)/n;	 %’ξονας συχνοτήτων (αρνητικός, θετικός)
subplot(4,1,4);
  plot(MF, y); 		%Στην θέση 4 του σχήματος 2, το εύρος ζώνης συχνοτήτων του m_PSK
  xlabel('Frequency (Hz)');
  ylabel('|Amplitude|');
  title('Frequency Spectrum of FSK');
  axis([-max_Hz max_Hz 0 max_amplitude_1]);
  set(gca,'XTick',-max_Hz:step_Hz:max_Hz);
  grid on; hold on;