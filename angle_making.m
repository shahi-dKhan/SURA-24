% Sampling time (50 Hz)
dt = 1/50;

% Manually specify input files for lower and upper armbands
lower_file = 'envelopes/4kg_lower_run03.csv';  % Change this to your file path
upper_file = 'envelopes/4kg_upper_run03.csv';  % Change this to your file path
processing_dir = 'matlab_processing_directory';
if ~exist(processing_dir, 'dir')
    mkdir(processing_dir);
end

% Copy files into the processing directory
copyfile(lower_file, processing_dir);
copyfile(upper_file, processing_dir);

% Update file paths to point to the copied files
lower_file = fullfile(processing_dir, '4kg_lower_run03.csv');
upper_file = fullfile(processing_dir, '4kg_upper_run03.csv');

% Remove the first 0.0 seconds of lower armband data
num_points_to_remove_upper = round(0.0 / dt);  % Specify the number of points to remove
num_points_to_remove_lower = round(0.14 / dt);  % Specify the number of points to remove
% Process data for lower and upper armband
[angles_lower_kalman, gyro_angles_lower, lower_data_filtered] = processArmData(lower_file, num_points_to_remove_lower);
[angles_upper_kalman, gyro_angles_upper, upper_data_filtered] = processArmData(upper_file, num_points_to_remove_upper);

N_lower = length(angles_lower_kalman);
N_upper = length(angles_upper_kalman);

if N_lower > N_upper
    % Trim the lower data to match upper data
    angles_lower_kalman = angles_lower_kalman(1:N_upper);
    gyro_angles_lower = gyro_angles_lower(1:N_upper);
    lower_data_filtered = lower_data_filtered(1:N_upper, :);
elseif N_upper > N_lower
    % Trim the upper data to match lower data
    angles_upper_kalman = angles_upper_kalman(1:N_lower);
    gyro_angles_upper = gyro_angles_upper(1:N_lower);
    upper_data_filtered = upper_data_filtered(1:N_lower, :);
end
% Baseline correction for lower arm gyroscopic angle
window_size = 100;
baseline = movmean(gyro_angles_lower, window_size);
gyro_angles_lower_corrected = gyro_angles_lower;

% Invert gyroscopic angles
gyro_angles_lower_corrected = -gyro_angles_lower_corrected;
gyro_angles_upper = -gyro_angles_upper;

% Generate time vector based on the size of the adjusted arrays
N = length(angles_lower_kalman);
time = (0:N-1) * dt;

% Calculate angle differences
kalman_angle_difference = angles_upper_kalman - angles_lower_kalman;
gyro_angle_difference = gyro_angles_upper - gyro_angles_lower_corrected;

% Set negative values to zero in gyro angle difference
gyro_angle_difference(gyro_angle_difference < 0) = 0;

% Save the output CSV file for the upper data with the new kalman_angle_difference column
upper_data = readtable(upper_file);  % Read original data from the upper file
upper_data_filtered.kalman_angle_difference = kalman_angle_difference;  % Add the new column
output_dir = 'matlab_output';
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

% Generate output file name with 'matlab_output_' prefix
[~, upper_name, ext] = fileparts(upper_file);
output_file = fullfile(output_dir, [upper_name, ext]);

% Write the modified table to a new CSV file
writetable(upper_data_filtered, output_file);

% Inform user about the saved output
disp(['Processed file saved as: ', output_file]);

% Plot the results for visual verification
figure;
subplot(2, 1, 1);
plot(time, angles_lower_kalman, 'b--', 'DisplayName', 'Lower Armband Kalman Angle');
hold on;
plot(time, angles_upper_kalman(1:N), 'r--', 'DisplayName', 'Upper Armband Kalman Angle');
plot(time, (180 + kalman_angle_difference), 'g', 'DisplayName', 'Kalman Angle Difference (Upper - Lower)');
xlabel('Time (s)');
ylabel('Angle (degrees)');
legend;
title('Kalman Filter Angle Comparison');
grid on;

subplot(2, 1, 2);
plot(time, gyro_angles_lower_corrected, 'b', 'DisplayName', 'Lower Armband Gyro Angle (Corrected)');
hold on;
plot(time, gyro_angles_upper(1:N), 'r', 'DisplayName', 'Upper Armband Gyro Angle');
plot(time, gyro_angle_difference, 'g--', 'DisplayName', 'Gyro Angle Difference');
xlabel('Time (s)');
ylabel('Angle (degrees)');
legend;
title('Gyroscopic Angle Comparison');
grid on;

function [angles_kalman, gyro_angle, data_filtered] = processArmData(file_name, num_points_to_remove)
    % Load data from CSV file
    data = readtable(file_name);
    dt = 1/50;  % Sampling time (50 Hz)
    
    % Extract accelerometer and gyroscope data
    accel_X = data.AccX;
    accel_Y = data.AccY;
    gyro_Z = data.GyZ;  % Rotation about the Z axis (XY plane rotation)

    N = length(accel_X); % Number of data points

    % Preallocate for results
    angles_kalman = zeros(N, 1);  % Angle estimates using Kalman filter
    gyro_angle = zeros(N, 1);      % Integrated angle from gyroscope

    % Kalman Filter variables
    angle = 0;  % Initial angle estimate
    bias = 0;   % Initial gyro bias estimate
    P = [0 0; 0 0];  % Error covariance matrix

    for i = 1:N
        % Compute angle from accelerometer (considering g is aligned with x-axis)
        acc_magnitude = sqrt(accel_X(i)^2 + accel_Y(i)^2);  % Total acceleration
        acc_angle = acos(accel_X(i) / acc_magnitude) * 180 / pi;  % Angle relative to x-axis

        % Gyro rate (dps to degrees per second)
        gyro_rate = gyro_Z(i) - bias;

        % RK2 Integration of the gyroscope data
        if i == 1
            gyro_angle(i) = gyro_rate * dt;  % Initial integration step
        else
            k1 = gyro_rate * dt;
            k2 = (gyro_rate + gyro_Z(i-1) - bias) * dt / 2;
            gyro_angle(i) = gyro_angle(i-1) + k2;
        end

        % Kalman Filter Prediction step
        rate = gyro_rate - bias;
        angle = angle + dt * rate;

        % Kalman Filter Update step (update angle based on accelerometer measurement)
        angle = acc_angle;

        % Store the results
        angles_kalman(i) = angle;
    end 

    % Remove the specified number of points from the beginning
    if num_points_to_remove > 0
        data_filtered = data(num_points_to_remove + 1:end, :);
        angles_kalman = angles_kalman(num_points_to_remove + 1:end);
        gyro_angle = gyro_angle(num_points_to_remove + 1:end);
    else
        data_filtered = data;  % If no points to remove, keep all data
    end
end