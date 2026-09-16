%% find_equilibria_SystemB_correct.m
% System B:
%   x2 = 0.5 * tan(pi*x1/2)
%   x1 = 0.5 * tan(pi*x2/2)
% Diagonal:     x1 = x2 = r  ->  h(r) := tan(pi*r/2) - 2*r = 0
% Off-diagonal: (a,b) with a ~= b  ->  G(a) := F(F(a)) - a = 0,  b = F(a),  F(x)=0.5*tan(pi*x/2)

clear; clc;

% ---------------- user settings ----------------
N_STRIPS = 6;          % search strips n = -N_STRIPS : +N_STRIPS (infinite in theory)
EPS      = 1e-9;       % avoid tan() poles at odd integers
TOL      = 1e-12;      % numerical tolerance
SEEDS    = [-0.85 -0.55 -0.25 0.25 0.55 0.85];  % seeds inside each noncentral strip for off-diagonals

% ---------------- helpers ----------------
F  = @(x) 0.5 * tan(pi*x/2);
h  = @(r) tan(pi*r/2) - 2*r;                   % diagonal scalar equation
G  = @(a) F(F(a)) - a;                         % period-2 equation
is_finite = @(x) all(isfinite(x(:)));

% ========== A) DIAGONAL EQUILIBRIA ==========
diag_roots = [-0.5, 0, 0.5];                   % exact roots in the central strip (-1,1)

for n = -N_STRIPS:N_STRIPS
    if n==0, continue; end                     % central handled above
    a = (2*n - 1) + EPS;                       % left boundary (inside strip)
    b = (2*n + 1) - EPS;                       % right boundary (inside strip)
    % fzero with a bracket finds the unique root in this strip
    r = fzero(h, [a, b]);
    diag_roots(end+1) = r; %#ok<AGROW>
end
diag_roots = sort(diag_roots);

% ========== B) OFF-DIAGONAL EQUILIBRIA (period-2) ==========
% We solve G(a)=0 and keep only those with |F(a) - a| > tol (exclude diagonals).
pairs = [];                                    % rows: [a b]
found_a = [];                                   % keep 'a' values to deduplicate

for n = -N_STRIPS:N_STRIPS
    if n==0, continue; end
    % Build a few starting guesses inside strip I_n = (2n-1, 2n+1)
    seeds = 2*n + SEEDS;                       % shift template seeds to this strip
    for s = seeds
        try
            a_candidate = fzero(G, s);         % solve G(a)=0 from this seed
            if ~is_finite(a_candidate), continue; end
            % Normalize a_candidate to the strip where it lies (optional check)
            % Reject if it's near a tan pole:
            if any(abs(a_candidate - (2*(round((a_candidate-1)/2))+1)) < 1e-8)
                continue
            end
            b_candidate = F(a_candidate);
            % Exclude diagonals
            if abs(b_candidate - a_candidate) <= 1e-8
                continue
            end
            % Deduplicate by 'a' (mod ~ 2-periodicity): accept if not near existing
            if isempty(found_a) || all(abs(a_candidate - found_a) > 1e-6)
                pairs(end+1, :) = [a_candidate, b_candidate]; %#ok<AGROW>
                found_a(end+1) = a_candidate; %#ok<AGROW>
            end
        catch
            % fzero may fail for some seeds; that's fine—try the next one
        end
    end
end

% ========== PRINT RESULTS ==========
fprintf('System B — Diagonal equilibria (x1 = x2 = r):\n');
for k = 1:numel(diag_roots)
    fprintf('  r = % .12f\n', diag_roots(k));
end

fprintf('\nSystem B — Off-diagonal equilibria (a,b) with a ~= b:\n');
if isempty(pairs)
    fprintf('  (none found in the scanned strips; increase N_STRIPS or adjust SEEDS)\n');
else
    for k = 1:size(pairs,1)
        a = pairs(k,1); b = pairs(k,2);
        res1 = b - 0.5*tan(pi*a/2);
        res2 = a - 0.5*tan(pi*b/2);
        fprintf('  (a,b) = (% .12f, % .12f)   [res ~ %.1e, %.1e]\n', a, b, res1, res2);
    end
end
