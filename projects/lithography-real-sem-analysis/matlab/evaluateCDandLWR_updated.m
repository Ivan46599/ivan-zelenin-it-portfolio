function [CD, LWR, LER, edges] = evaluateCDandLWR_updated(xGrid, yGrid, RelativeHeight, HeightThresholdFraction, MinWidth, MaxWidth)
% evaluateCDandLWR_updated  Updated height-map algorithm for CD, LWR and LER.
%
% Difference from the old evaluateCDandLWR.m:
%   1) no histogram split of widths;
%   2) left and right edges are saved for every row;
%   3) edge positions are refined by linear interpolation at threshold crossing;
%   4) LER is calculated after removing a linear trend from each edge;
%   5) min/max width limits are explicit arguments.

if nargin < 5, MinWidth = 10; end
if nargin < 6, MaxWidth = 100; end

x = xGrid(1, :);
y = yGrid(:, 1);
heightRange = max(RelativeHeight(:)) - min(RelativeHeight(:));
threshold = min(RelativeHeight(:)) + HeightThresholdFraction * heightRange;

leftEdges = [];
rightEdges = [];
yValid = [];

for row = 1:size(RelativeHeight, 1)
    profile = RelativeHeight(row, :);
    above = profile >= threshold;
    if ~any(above)
        continue;
    end

    idx = find(above);
    % Use the widest connected component in the row.
    breaks = [0, find(diff(idx) > 1), numel(idx)];
    bestWidth = -Inf;
    bestStart = NaN;
    bestEnd = NaN;
    for k = 1:numel(breaks)-1
        component = idx(breaks(k)+1:breaks(k+1));
        if isempty(component), continue; end
        widthPx = component(end) - component(1) + 1;
        if widthPx > bestWidth
            bestWidth = widthPx;
            bestStart = component(1);
            bestEnd = component(end);
        end
    end

    if isnan(bestStart) || bestEnd <= bestStart
        continue;
    end

    if bestStart > 1
        leftX = interpThreshold(x(bestStart-1), profile(bestStart-1), x(bestStart), profile(bestStart), threshold);
    else
        leftX = x(bestStart);
    end

    if bestEnd < numel(x)
        rightX = interpThreshold(x(bestEnd+1), profile(bestEnd+1), x(bestEnd), profile(bestEnd), threshold);
    else
        rightX = x(bestEnd);
    end

    width = rightX - leftX;
    if width >= MinWidth && width <= MaxWidth
        leftEdges(end+1,1) = leftX; %#ok<AGROW>
        rightEdges(end+1,1) = rightX; %#ok<AGROW>
        yValid(end+1,1) = y(row); %#ok<AGROW>
    end
end

widths = rightEdges - leftEdges;
CD.Value = mean(widths);
CD.Unit = 'nm';
LWR.Sigma = std(widths);
LWR.ThreeSigma = 3 * LWR.Sigma;
LWR.Unit = 'nm';

leftResidual = detrendEdge(yValid, leftEdges);
rightResidual = detrendEdge(yValid, rightEdges);
LER.LeftSigma = std(leftResidual);
LER.RightSigma = std(rightResidual);
LER.AvgSigma = 0.5 * (LER.LeftSigma + LER.RightSigma);
LER.AvgThreeSigma = 3 * LER.AvgSigma;
LER.Unit = 'nm';

edges.y = yValid;
edges.left = leftEdges;
edges.right = rightEdges;
edges.width = widths;
edges.threshold = threshold;
end

function x = interpThreshold(x0, y0, x1, y1, threshold)
if y1 == y0
    x = 0.5 * (x0 + x1);
else
    x = x0 + (threshold - y0) * (x1 - x0) / (y1 - y0);
end
end

function residual = detrendEdge(y, edge)
if numel(y) < 3
    residual = edge * NaN;
else
    p = polyfit(y, edge, 1);
    residual = edge - polyval(p, y);
end
end
