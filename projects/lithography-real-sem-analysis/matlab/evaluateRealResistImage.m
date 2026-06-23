function [summary, lineTable, sectionTable] = evaluateRealResistImage(imagePath, params)
% evaluateRealResistImage  Calculates CD, LWR and LER from a real SEM/TIF image.
%
% This function is the MATLAB analogue of python/resist_image_metrics.py.
% It is intended for the uploaded SEM images of developed photoresist lines.
% The original evaluateCDandLWR.m expected a synthetic height map; this function
% adds image reading, SEM crop, scale calibration and feature extraction.
%
% Required params fields, with defaults if omitted:
%   featurePolarity  - 'dark' for supplied developed bands, 'bright' for bright ridges
%   scaleBarNm       - 100, because the uploaded images show a 100 nm scale bar
%   scaleNmPerPx     - [] to estimate from the scale bar; or a known calibration
%   topCropPx        - 70, to remove top marker/overlay area
%   peakDistancePx   - 25, minimum feature spacing in pixels
%   edgeMarginPx     - 15, rejects partial features near image borders
%   minWidthNm       - 3
%   maxWidthNm       - 70
%   minValidFraction - 0.30

if nargin < 2
    params = struct();
end
params = fillDefaults(params);

rgb = imread(imagePath);
if size(rgb, 3) == 1
    gray = double(rgb);
else
    gray = double(rgb2gray(rgb));
end

[scaleBarPx, ~] = estimateScaleBarPx(rgb);
if ~isempty(params.scaleNmPerPx)
    scaleNmPerPx = params.scaleNmPerPx;
elseif ~isnan(scaleBarPx)
    scaleNmPerPx = params.scaleBarNm / scaleBarPx;
else
    scaleNmPerPx = params.scaleBarNm / 138.0;
end

[crop, bbox] = cropSemArea(gray, params.topCropPx); %#ok<ASGLU>
score = preprocessCrop(crop, params);
featureSpecs = detectFeatureSpecs(score, params, scaleNmPerPx);

imageHeight = size(score, 1);
minWidthPx = params.minWidthNm / scaleNmPerPx;
maxWidthPx = params.maxWidthNm / scaleNmPerPx;

lineRows = [];
sectionRows = [];
lineId = 0;

for k = 1:numel(featureSpecs)
    spec = featureSpecs(k);
    initialWidthPx = max(spec.initialWidthPx, minWidthPx);
    halfWindowPx = round(max(8, min(maxWidthPx * 1.2, initialWidthPx * 2.5)));
    minRowWidthPx = max(1.5, 0.7 * minWidthPx);
    maxRowWidthPx = maxWidthPx;

    leftNm = [];
    rightNm = [];
    yNm = [];
    currentCenterPx = spec.centerPx;

    for row = 1:imageHeight
        edge = edgesNearPeak(score(row, :), currentCenterPx, spec.thresholdScore, halfWindowPx, minRowWidthPx, maxRowWidthPx);
        if isempty(edge)
            continue;
        end
        leftPx = edge(1);
        rightPx = edge(2);
        centerPx = edge(3);
        currentCenterPx = 0.98 * currentCenterPx + 0.02 * centerPx;
        leftNm(end + 1, 1) = leftPx * scaleNmPerPx; %#ok<AGROW>
        rightNm(end + 1, 1) = rightPx * scaleNmPerPx; %#ok<AGROW>
        yNm(end + 1, 1) = (row - 1) * scaleNmPerPx; %#ok<AGROW>
    end

    if numel(yNm) < params.minValidFraction * imageHeight
        continue;
    end

    widths = rightNm - leftNm;
    medWidth = median(widths);
    madWidth = median(abs(widths - medWidth)) + eps;
    keep = abs(widths - medWidth) <= 4.0 * 1.4826 * madWidth;
    leftNm = leftNm(keep);
    rightNm = rightNm(keep);
    yNm = yNm(keep);
    widths = widths(keep);

    if numel(yNm) < params.minValidFraction * imageHeight
        continue;
    end

    lineId = lineId + 1;
    lwrSigma = std(widths);
    lerLeftSigma = detrendedStd(yNm, leftNm);
    lerRightSigma = detrendedStd(yNm, rightNm);
    lerAvgSigma = 0.5 * (lerLeftSigma + lerRightSigma);
    centerNm = 0.5 * (median(leftNm) + median(rightNm));

    lineRows = [lineRows; {string(getFileName(imagePath)), string(params.featurePolarity), lineId, numel(widths), numel(widths) / imageHeight, centerNm, mean(widths), median(widths), lwrSigma, 3*lwrSigma, lerLeftSigma, lerRightSigma, lerAvgSigma, 3*lerAvgSigma, spec.thresholdScore, spec.initialWidthPx * scaleNmPerPx}]; %#ok<AGROW>

    for n = 1:numel(widths)
        sectionRows = [sectionRows; {string(getFileName(imagePath)), string(params.featurePolarity), lineId, yNm(n), leftNm(n), rightNm(n), widths(n)}]; %#ok<AGROW>
    end
end

lineTable = cell2table(lineRows, 'VariableNames', {'image_name','feature_polarity','line_id','n_sections','valid_fraction','center_nm','CD_mean_nm','CD_median_nm','LWR_sigma_nm','LWR_3sigma_nm','LER_left_sigma_nm','LER_right_sigma_nm','LER_avg_sigma_nm','LER_avg_3sigma_nm','threshold_score','initial_width_nm'});
sectionTable = cell2table(sectionRows, 'VariableNames', {'image_name','feature_polarity','line_id','y_nm','left_nm','right_nm','width_nm'});

summary = struct();
summary.image_name = string(getFileName(imagePath));
summary.feature_polarity = string(params.featurePolarity);
summary.scale_nm_per_px = scaleNmPerPx;
summary.scale_bar_px = scaleBarPx;
summary.n_lines = height(lineTable);
summary.n_sections_total = sum(lineTable.n_sections);

if height(lineTable) > 0
    summary.CD_mean_nm = mean(lineTable.CD_mean_nm, 'omitnan');
    summary.CD_median_nm = mean(lineTable.CD_median_nm, 'omitnan');
    summary.LWR_sigma_nm = mean(lineTable.LWR_sigma_nm, 'omitnan');
    summary.LWR_3sigma_nm = mean(lineTable.LWR_3sigma_nm, 'omitnan');
    summary.LER_avg_sigma_nm = mean(lineTable.LER_avg_sigma_nm, 'omitnan');
    summary.LER_avg_3sigma_nm = mean(lineTable.LER_avg_3sigma_nm, 'omitnan');
    if height(lineTable) > 1
        summary.pitch_mean_nm = mean(diff(sort(lineTable.center_nm)));
    else
        summary.pitch_mean_nm = NaN;
    end
else
    summary.CD_mean_nm = NaN;
    summary.CD_median_nm = NaN;
    summary.LWR_sigma_nm = NaN;
    summary.LWR_3sigma_nm = NaN;
    summary.LER_avg_sigma_nm = NaN;
    summary.LER_avg_3sigma_nm = NaN;
    summary.pitch_mean_nm = NaN;
end

end

function params = fillDefaults(params)
if ~isfield(params, 'featurePolarity'), params.featurePolarity = 'dark'; end
if ~isfield(params, 'scaleBarNm'), params.scaleBarNm = 100.0; end
if ~isfield(params, 'scaleNmPerPx'), params.scaleNmPerPx = []; end
if ~isfield(params, 'topCropPx'), params.topCropPx = 70; end
if ~isfield(params, 'peakDistancePx'), params.peakDistancePx = 25; end
if ~isfield(params, 'edgeMarginPx'), params.edgeMarginPx = 15; end
if ~isfield(params, 'minWidthNm'), params.minWidthNm = 3.0; end
if ~isfield(params, 'maxWidthNm'), params.maxWidthNm = 70.0; end
if ~isfield(params, 'minValidFraction'), params.minValidFraction = 0.30; end
if ~isfield(params, 'backgroundSigmaPx'), params.backgroundSigmaPx = 30.0; end
if ~isfield(params, 'smoothSigmaYPx'), params.smoothSigmaYPx = 1.0; end
if ~isfield(params, 'smoothSigmaXPx'), params.smoothSigmaXPx = 1.2; end
end

function [scaleBarPx, components] = estimateScaleBarPx(rgb)
if size(rgb, 3) == 1
    scaleBarPx = NaN;
    components = [];
    return;
end
r = rgb(:,:,1); g = rgb(:,:,2); b = rgb(:,:,3);
mask = g > 120 & r < 100 & b < 100;
mask(1:floor(0.8 * size(mask,1)), :) = false;
cc = bwconncomp(mask);
components = [];
for k = 1:cc.NumObjects
    [yy, xx] = ind2sub(size(mask), cc.PixelIdxList{k});
    width = max(xx) - min(xx) + 1;
    heightPx = max(yy) - min(yy) + 1;
    area = numel(xx);
    if area > 30 && width > 80 && heightPx < 25
        components = [components; width, area, min(xx), max(xx), min(yy), max(yy)]; %#ok<AGROW>
    end
end
if isempty(components)
    scaleBarPx = NaN;
else
    [~, idx] = max(components(:,1));
    scaleBarPx = components(idx,1);
end
end

function [crop, bbox] = cropSemArea(gray, topCropPx)
rowMean = mean(gray, 2);
imageHeight = size(gray, 1);
lowerRows = floor(0.65 * imageHeight):imageHeight;
footerCandidates = lowerRows(rowMean(lowerRows) < 30);
if isempty(footerCandidates)
    bottom = floor(0.95 * imageHeight);
else
    bottom = footerCandidates(1);
end
top = min(topCropPx, bottom - 100);
top = max(top, 1);
crop = gray(top:bottom, :);
bbox = [top, 1, bottom, size(gray, 2)];
end

function score = preprocessCrop(crop, params)
background = gaussianBlur(crop, params.backgroundSigmaPx, params.backgroundSigmaPx);
corrected = crop - background + median(background(:));
smoothed = gaussianBlur(corrected, params.smoothSigmaYPx, params.smoothSigmaXPx);
v = sort(smoothed(:));
n = numel(v);

lo = v(max(1, round(0.01 * n)));
hi = v(min(n, round(0.99 * n)));
normalized = min(max((smoothed - lo) ./ (hi - lo + eps), 0), 1);
if strcmpi(params.featurePolarity, 'bright')
    score = normalized;
else
    score = 1 - normalized;
end
end

function out = gaussianBlur(in, sigmaY, sigmaX)
radiusY = max(1, ceil(4 * sigmaY));
radiusX = max(1, ceil(4 * sigmaX));
y = -radiusY:radiusY;
x = -radiusX:radiusX;
gy = exp(-0.5 * (y ./ sigmaY).^2); gy = gy ./ sum(gy);
gx = exp(-0.5 * (x ./ sigmaX).^2); gx = gx ./ sum(gx);
out = conv2(conv2(in, gy(:), 'same'), gx(:)', 'same');
end

function specs = detectFeatureSpecs(score, params, scaleNmPerPx)
profile = mean(score, 1);
profile = smooth1d(profile, 3.0);
minWidthPx = params.minWidthNm / scaleNmPerPx;
maxWidthPx = params.maxWidthNm / scaleNmPerPx;
peaks = localPeaks(profile, params.peakDistancePx);
specs = struct('centerPx', {}, 'initialWidthPx', {}, 'thresholdScore', {});
for k = 1:numel(peaks)
    p = peaks(k);
    if p < params.edgeMarginPx || p > numel(profile) - params.edgeMarginPx
        continue;
    end
    leftMin = min(profile(max(1, p - params.peakDistancePx):p));
    rightMin = min(profile(p:min(numel(profile), p + params.peakDistancePx)));
    base = max(leftMin, rightMin);
    threshold = base + 0.5 * (profile(p) - base);
    left = p;
    while left > 1 && profile(left) >= threshold
        left = left - 1;
    end
    right = p;
    while right < numel(profile) && profile(right) >= threshold
        right = right + 1;
    end
    widthPx = right - left;
    if left < params.edgeMarginPx || right > numel(profile) - params.edgeMarginPx
        continue;
    end
    if widthPx >= minWidthPx && widthPx <= maxWidthPx
        specs(end + 1).centerPx = p; %#ok<AGROW>
        specs(end).initialWidthPx = widthPx;
        specs(end).thresholdScore = threshold;
    end
end
end

function smoothed = smooth1d(signal, sigma)
radius = max(1, ceil(4 * sigma));
x = -radius:radius;
g = exp(-0.5 * (x ./ sigma).^2); g = g ./ sum(g);
smoothed = conv(signal, g, 'same');
end

function peaks = localPeaks(profile, minDistance)
candidate = find(profile(2:end-1) > profile(1:end-2) & profile(2:end-1) >= profile(3:end)) + 1;
[~, order] = sort(profile(candidate), 'descend');
selected = [];
for idx = order
    p = candidate(idx);
    if isempty(selected) || all(abs(selected - p) >= minDistance)
        selected(end + 1) = p; %#ok<AGROW>
    end
end
peaks = sort(selected);
end

function edge = edgesNearPeak(row, centerPx, threshold, halfWindowPx, minWidthPx, maxWidthPx)
n = numel(row);
centerIndex = round(centerPx);
leftLimit = max(1, centerIndex - halfWindowPx);
rightLimit = min(n, centerIndex + halfWindowPx);
above = row(leftLimit:rightLimit) >= threshold;
runs = [];
idx = 1;
while idx <= numel(above)
    if ~above(idx)
        idx = idx + 1;
        continue;
    end
    startLocal = idx;
    while idx <= numel(above) && above(idx)
        idx = idx + 1;
    end
    endLocal = idx - 1;
    startGlobal = leftLimit + startLocal - 1;
    endGlobal = leftLimit + endLocal - 1;
    centerGlobal = 0.5 * (startGlobal + endGlobal);
    widthGlobal = endGlobal - startGlobal + 1;
    runs = [runs; startGlobal, endGlobal, centerGlobal, widthGlobal]; %#ok<AGROW>
end
if isempty(runs)
    edge = [];
    return;
end
[~, best] = min(abs(runs(:,3) - centerPx));
start = runs(best, 1);
endIdx = runs(best, 2);
width = runs(best, 4);
if width < minWidthPx || width > maxWidthPx
    edge = [];
    return;
end
leftEdge = start;
rightEdge = endIdx;
if start > 1
    leftEdge = linearCrossing(start - 1, row(start - 1), start, row(start), threshold);
end
if endIdx < n
    rightEdge = linearCrossing(endIdx + 1, row(endIdx + 1), endIdx, row(endIdx), threshold);
end
if rightEdge - leftEdge < minWidthPx || rightEdge - leftEdge > maxWidthPx
    edge = [];
else
    edge = [leftEdge, rightEdge, 0.5 * (leftEdge + rightEdge)];
end
end

function x = linearCrossing(x0, y0, x1, y1, threshold)
if y1 == y0
    x = 0.5 * (x0 + x1);
else
    x = x0 + (threshold - y0) * (x1 - x0) / (y1 - y0);
end
end

function sigma = detrendedStd(y, edge)
if numel(y) < 3
    sigma = NaN;
    return;
end
p = polyfit(y, edge, 1);
residual = edge - polyval(p, y);
sigma = std(residual);
end

function name = getFileName(path)
[~, name, ext] = fileparts(path);
name = [name, ext];
end
