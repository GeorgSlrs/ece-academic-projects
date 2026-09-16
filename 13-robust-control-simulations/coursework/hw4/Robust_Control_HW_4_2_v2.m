clear; clc;

% Your plant
M = [1 0;
     10 10];

%% Full 2×2 complex block
% [2 0] ⇒ one 2×2 block, 'c' ⇒ complex‐μ
blk_full = [2 0];
[b_full, info_full] = mussv(M, blk_full, 'c');
mu_full = b_full(1);    % lower ≃ upper

[Delta_full, ~, ~] = mussvextract(info_full);

fprintf('Full‐block (complex):\n');
fprintf('  μ_lower = %.6f   μ_upper = %.6f\n', b_full(1), b_full(2));
fprintf('  ⇒ μ = %.6f\n', mu_full);
fprintf('  ‖Δ‖₂ = %.6f    det(I–MΔ) = %.2e\n\n', ...
        norm(Delta_full,2), det(eye(2)-M*Delta_full));


%% Two 1×1 complex blocks (diagonal Δ)
blk_diag = [1 0;
            1 0];
[b_diag, info_diag] = mussv(M, blk_diag, 'c');
mu_diag = b_diag(1);

[Delta_diag, ~, ~] = mussvextract(info_diag);

fprintf('Diagonal‐block (complex):\n');
fprintf('  μ_lower = %.6f   μ_upper = %.6f\n', b_diag(1), b_diag(2));
fprintf('  ⇒ μ = %.6f\n', mu_diag);
fprintf('  ‖Δ‖₂ = %.6f    det(I–MΔ) = %.2e\n', ...
        norm(Delta_diag,2), det(eye(2)-M*Delta_diag));


