% Define the folder where the CSV files are stored
folder_path = 'electrical_mes';

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
voltageThreshold = 20; % Adjust this threshold as needed

% Filter out the noise by excluding points below the voltage threshold
filteredIndices = sortedVoltage > voltageThreshold;
filteredTime = sortedTime(filteredIndices);
filteredVoltage = sortedVoltage(filteredIndices);

% Check if filtered data is empty
if isempty(filteredTime) || isempty(filteredVoltage)
    error('Filtered data is empty. Adjust the voltageThreshold or check the input data.');
end

% Find the maximum voltage value and its corresponding time in the filtered data
[maxVoltage, maxIdx] = max(filteredVoltage);
maxTime = filteredTime(maxIdx);

% Find the time where voltage is 50% of the max value in the filtered data
halfMaxVoltage = maxVoltage / 2;
halfMaxIdx = find(filteredVoltage >= halfMaxVoltage, 1, 'first');
halfMaxTime = filteredTime(halfMaxIdx);

% Check if we found the half max time
if isempty(halfMaxTime)
    error('Could not find the time for 50%% of max voltage. Check the voltageThreshold or input data.');
end

% Initialize a figure for the plot
figure;

% Plot the filtered data
plot(filteredTime, filteredVoltage, '.', 'Color', [0.5, 0.5, 0.5]); % Use grey dots to plot individual points

% Annotate the plot with the maximum value and 50% of maximum value
hold on; % Keep the plot open for more additions
plot(maxTime, maxVoltage, 'ro', 'MarkerSize', 10, 'MarkerFaceColor', 'red'); % Mark max with a red circle
plot(halfMaxTime, halfMaxVoltage, 'mo', 'MarkerSize', 10, 'MarkerFaceColor', 'magenta'); % Mark half max with a magenta circle
hold off; % Release the plot hold

% Annotations for maximum and half-maximum values
% Ensure the text annotations appear within the figure bounds
if maxVoltage < max(filteredVoltage)
    text(maxTime, maxVoltage, sprintf(' 100%% Max (%.2f V at %.2f s)', maxVoltage, maxTime), 'Color', 'red', 'VerticalAlignment', 'bottom');
end

if halfMaxVoltage < max(filteredVoltage)
    text(halfMaxTime, halfMaxVoltage, sprintf(' 50%% Max (%.2f V at %.2f s)', halfMaxVoltage, halfMaxTime), 'Color', 'magenta', 'VerticalAlignment', 'bottom');
end

% Customize the plot
title('Filtered Voltage-Time Plot with Annotations');
xlabel('Time (s)');
ylabel('Voltage (units)');

% Print the maximum voltage, 50% of the maximum voltage, and their corresponding times
fprintf('Maximum Voltage in Filtered Data: %.2f V at time %.2f s\n', maxVoltage, maxTime);
fprintf('Time to reach 50%% of Maximum Voltage in Filtered Data: %.2f s, Voltage: %.2f V\n', halfMaxTime, halfMaxVoltage);

