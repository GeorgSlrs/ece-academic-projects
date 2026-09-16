folder_path = 'C:\Users\georg\Desktop\electrical_mes';
files = dir(fullfile(folder_path, 'tek*.csv'));

% Predefine a variable for storing all file names
files = dir(fullfile(folder_path, 'tek*.csv'));

% Initialize variables to store the combined data
all_time = [];
all_voltage = [];

% Loop through each file
for k = 1:length(files)
    % Construct the full file path
    file_path = fullfile(folder_path, files(k).name);
    
    % Read the data from the file
    data = readmatrix(file_path);
    
    % Assuming the first column is time and the second is voltage
    all_time = [all_time; data(:, 1)]; % Combine time data from all files
    all_voltage = [all_voltage; data(:, 2)]; % Combine voltage data from all files
end

% Sort the combined data by time
[sortedTime, sortIndex] = sort(all_time);
sortedVoltage = all_voltage(sortIndex);

% Define a voltage threshold below which the data is considered as noise
voltageThreshold = 20; % You need to set this value based on your observation

% Filter out the noise by excluding points below the voltage threshold
filteredIndices = sortedVoltage > voltageThreshold;
filteredTime = sortedTime(filteredIndices);
filteredVoltage = sortedVoltage(filteredIndices);

% Find the maximum voltage value and its corresponding time in the filtered data
[maxVoltage, maxIdx] = max(filteredVoltage);
maxTime = filteredTime(maxIdx);

% Find the time where voltage is 50% of the max value in the filtered data
halfMaxVoltage = maxVoltage / 2;
halfMaxIdx = find(filteredVoltage >= halfMaxVoltage, 1, 'first');
halfMaxTime = filteredTime(halfMaxIdx);

% Initialize a figure for the plot
figure;

% Plot the filtered data
plot(filteredTime, filteredVoltage, '.'); % Use dots to plot individual points

% Annotate the plot with the maximum value
hold on; % Keep the plot open for more additions
plot(maxTime, maxVoltage, 'ro', 'MarkerSize', 8, 'LineWidth', 2); % Mark with a red circle
hold off; % Release the figure

% Customize the plot
title('Filtered Voltage-Time Plot without Noise');
xlabel('Time (s)');
ylabel('Voltage (units)');

% Print the maximum voltage and its corresponding time
fprintf('Maximum Voltage in Filtered Data: %.2f V at time %.2f s\n', maxVoltage, maxTime);
fprintf('Time to reach 50%% of Maximum Voltage in Filtered Data: %.2f s\n', halfMaxTime);
