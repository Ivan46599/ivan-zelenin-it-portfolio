function [CD, LWR] = evaluateCDandLWR(xGrid, yGrid, RelativeHeight, Structure, HeightThreshold)

widthArray = [];

HeightThreshold = HeightThreshold * (max(mean(RelativeHeight, 1)) - min(mean(RelativeHeight, 1)));

for nn = 1:size(xGrid, 1)

    thresholdX           = xGrid(nn, :);
    thresholdX(RelativeHeight(nn, :) < HeightThreshold) = [];

    componentNumber = 0;
    setIndex        = 1;
    for mm = 1:length(thresholdX) - setIndex
        if thresholdX(mm + setIndex) - thresholdX(mm) > setIndex * (xGrid(nn, 2) - xGrid(nn, 1))
            componentNumber = componentNumber + 1;
        end
    end

    components           = cell(componentNumber, 1);
    components{1}.StartX = xGrid(nn, 1);
    components{end}.EndX = xGrid(nn, end);
    componentNumber      = 0;
    for mm = 1:length(thresholdX) - setIndex
        if thresholdX(mm + setIndex) - thresholdX(mm) > setIndex * (xGrid(1, 2) - xGrid(1, 1))
            componentNumber = componentNumber + 1;
            components{componentNumber}.EndX       = thresholdX(mm);
            components{componentNumber + 1}.StartX = thresholdX(mm + 1);
        end
    end

    for mm = 1:componentNumber
        if (components{(mm)}.EndX - components{(mm)}.StartX) <  Structure.Trapez.Width.Value
        else
            widthArray = [widthArray; components{(mm)}.EndX - components{(mm)}.StartX];
        end
    end

end

widthArray = widthArray(widthArray < Structure.Pitch.Value);

hEdges        = linspace(0, Structure.Pitch.Value, Structure.Pitch.Value * 2 + 1);
[N, ~, bins]  = histcounts(widthArray, hEdges);
xN = hEdges([1:end-1]) + 0.5 * (hEdges(2) - hEdges(1));

xZeros     = xN(N == 0);
compNumber = 0;
for nn = 1:length(xZeros) - 1
    if xZeros(nn + 1) - xZeros(nn) >= 2.0 * (hEdges(2) - hEdges(1))
        compNumber = compNumber + 1;
    end
end
if xZeros(end) == xZeros(end - 1) + (hEdges(2) - hEdges(1))
    compNumber = compNumber + 1;
end

compHistCount = ones(compNumber, 1);
intervalEnds  = zeros(compNumber, 1);
compNumber = 0;
for nn = 1:length(xZeros) - 1
    if xZeros(nn + 1) - xZeros(nn) >= 2.0 * (hEdges(2) - hEdges(1))
        compNumber = compNumber + 1;
        intervalEnds(compNumber) = xZeros(nn);
    else
        compHistCount(compNumber + 1) = compHistCount(compNumber + 1) + 1;
    end
end
if xZeros(end) == xZeros(end - 1) + (hEdges(2) - hEdges(1))
    compHistCount(compNumber + 1) = compHistCount(compNumber + 1) + 1;
else
    compNumber = compNumber + 1;
    intervalEnds(compNumber) = xZeros(end);
end

% figure;
% plot(xN, N, '.k', 'MarkerSize', 10);
% grid on;
% hold on;
% plot(xZeros, 0, '.r', 'MarkerSize', 10);

[~, ind]       = max(compHistCount);
widthThreshold = intervalEnds(ind) - 0.5 * (compHistCount(ind) - 1) * (hEdges(2) - hEdges(1));

evalWidthArray = widthArray;
if sum(N(xN > widthThreshold)) > sum(N(xN < widthThreshold))
    evalWidthArray(widthArray < widthThreshold) = [];
else
    evalWidthArray(widthArray > widthThreshold) = [];
end

CD.Value  = mean(evalWidthArray);
CD.Unit   = 'nm';
LWR.Value = std(evalWidthArray);
LWR.Unit  = 'nm';

end