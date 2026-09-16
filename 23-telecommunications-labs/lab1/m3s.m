function [means,mins,maxs] = m3s(X)

maxs = X(1);
mins = X(1);
means = 0;
k = 0; %iterator

for k = 2:1:length(X)
    means = means + X(k);
    if maxs < X(k)
        maxs = X(k);
    end
    if mins > X(k)
        mins = X(k);
    end

end

means = means / length(X);

end