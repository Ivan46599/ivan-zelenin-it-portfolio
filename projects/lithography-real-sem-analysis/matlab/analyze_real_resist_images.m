clear; clc; close all;

% Real SEM/TIF photoresist analysis.
% Target objects in the supplied images are thin dark developed bands.
% NILS is not calculated from SEM images because SEM contrast is not the
% optical intensity profile I(x).

projectDir = fileparts(fileparts(mfilename('fullpath')));
inputDir = fullfile(projectDir, 'input_images');
resultsDir = fullfile(projectDir, 'results');
if ~exist(resultsDir, 'dir')
    mkdir(resultsDir);
end

params = struct();
params.featurePolarity = 'dark';   % Use 'bright' only for bright resist ridges.
params.scaleBarNm = 100.0;
params.scaleNmPerPx = [];          % Estimate from the green 100 nm scale bar.
params.topCropPx = 70;
params.peakDistancePx = 25;
params.edgeMarginPx = 15;
params.minWidthNm = 3.0;
params.maxWidthNm = 70.0;
params.minValidFraction = 0.30;

files = dir(fullfile(inputDir, '*.tif'));
files = [files; dir(fullfile(inputDir, '*.tiff'))]; %#ok<AGROW>

summaryRows = table();
allLineRows = table();
allSectionRows = table();

for k = 1:numel(files)
    imagePath = fullfile(files(k).folder, files(k).name);
    [summary, lineTable, sectionTable] = evaluateRealResistImage(imagePath, params);
    summaryRows = [summaryRows; struct2table(summary)]; %#ok<AGROW>
    allLineRows = [allLineRows; lineTable]; %#ok<AGROW>
    allSectionRows = [allSectionRows; sectionTable]; %#ok<AGROW>
    fprintf('%s: CD = %.3f nm, LWR_3sigma = %.3f nm, LER_3sigma = %.3f nm\n', ...
        files(k).name, summary.CD_mean_nm, summary.LWR_3sigma_nm, summary.LER_avg_3sigma_nm);
end

writetable(summaryRows, fullfile(resultsDir, 'summary_metrics_matlab.csv'));
writetable(allLineRows, fullfile(resultsDir, 'per_line_metrics_matlab.csv'));
writetable(allSectionRows, fullfile(resultsDir, 'section_edges_matlab.csv'));
