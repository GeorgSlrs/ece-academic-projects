%Κώδικας σε MatLab/Octave για την προσομοίωση των βασικών σημάτων ψηφιακών διαμορφώσεων:
%Amplitude Shift Keying / On-Off Keying (ASK/ΟΟΚ), Frequency Shift Keying (FSK), Phase Shift Keying (PSK).
clear all; 
close all; 
clc;
%pi=3.14159;
%π
Spcm = [1 0 1 0 1 0 1]; 
total=size(Spcm,2); % Ο πλήθος των data bits
org_bits=[]; % βοηθητικός πίνακας για την αναπαράσταση των bits
f1=5; 		% Συχνότητα φορέα f1=5 Hz
f2=10; 		% Συχνότητα φορέα f2=10 Hz
t1=0; 		% Μεταβλητή χρόνου
t2=1; 		% Μεταβλητή Χρόνου

for i=1:total                   % Για κάθε data bit i, αντιστοιχεί χρονικό διάστημα [t1, t2]
t =[t1:0.01:t2];                % Διακριτότητα χρόνου 0.01
m_ask(i,:)=zeros(1,length(t));  % Αρχικοποίηση
m_fsk(i,:)=zeros(1,length(t));  % Αρχικοποίηση
m_psk(i,:)=zeros(1,length(t));  % Αρχικοποίηση
if Spcm(i)==1                   % Αν bit = "1"
  m_ask(i,:)=sin(2*pi*f1*t);    % OOK(ASK) = φορέα συχνότητας f1.
  m_fsk(i,:)=sin(2*pi*f1*t);    % FSK = φορέα συχνότητας f1.
  m_psk(i,:)=sin(2*pi*f1*t);    % PSK = φορέα φάσης 0 rads.
  org_bits(i,:) = ones(1, length(t));
else                            % Αν bit = "0"
  m_ask(i,:)=0;                 % OOK = 0.
  m_fsk(i,:)=sin(2*pi*f2*t);    % FSK = φορέα συχνότητας f2.
  m_psk(i,:)=sin(2*pi*f1*t+pi); % PSK = φορέα φάσης π rads.
  org_bits(i,:) = zeros(1, length(t));
end
subplot(4,1,1);        % Το σχήμα θα περιλαμβάνει 4 διαγράμματα, το ένα κάτω από το άλλο.
 % plot(t,Spcm(i), 'b');     % Στην θέση 1, τα bits ως (μονο)πολική
 % παλμοσειρά. Works fine in Octave!
 plot(t, org_bits(i,:), 'b');
  xlabel('time')
  ylabel('amplitude')
  title('Data bits')
  hold on;
  grid on;
  axis([0 total 0 1]); % ’ξονας x από 0 μέχρι total. ’ξονας y από 0 μέχρι 1.
subplot(4,1,2);
  plot(t,m_ask(i,:),'b');  % Στην θέση 2, το σήμα ΟΟΚ(ASK) - χρώμα μπλε.
  xlabel('time')
  ylabel('amplitude')
  title('Σήμα ASK/OOK')
  hold on;
  grid on;
  axis([0 total -1 1]); % ’ξονας x από 0 μέχρι total. ’ξονας y από -1 μέχρι +1.
subplot(4,1,3);
  plot(t,m_fsk(i,:),'r');   % Στην θέση 3, το σήμα FSΚ - χρώμα κόκκινο.
  xlabel('time')
  ylabel('amplitude')
  title('Σήμα FSK')
  hold on;
  grid on;
  axis([0 total -1 1]); % ’ξονας x από 0 μέχρι total. ’ξονας y από -1 μέχρι +1.
subplot(4,1,4);
  plot(t,m_psk(i,:),'b');  % Στην θέση 4, το σήμα PSΚ - χρώμα μπλε.
  xlabel('time')
  ylabel('amplitude')
  title('Σήμα PSK')
  hold on;
  grid on;
  axis([0 total -1 1]); % ’ξονας x από 0 μέχρι total. ’ξονας y από -1 μέχρι +1.
t1=t1+1.0;
t2=t2+1.0;
end