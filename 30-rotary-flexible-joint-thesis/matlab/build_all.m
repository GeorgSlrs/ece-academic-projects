function build_all(varargin)
% BUILD_ALL  Build & simulate L0/L1/L2; then 3D (if Simscape Multibody) or 2D.
%
% Options:
%   build_all('rebuild',true,'open',false,'stop',[3 3 5])

p = inputParser;
p.addParameter('rebuild', true);
p.addParameter('open',    false);
p.addParameter('stop',    [3 3 5]);
p.parse(varargin{:}); opt = p.Results;

% Ensure params loaded
evalin('base','flex_joint_params');

% Build models
if opt.rebuild
    fprintf('>> Rebuilding L0/L1/L2 ...\n');
    try, build_lvl0; fprintf('Built RFJ_L0\n'); catch ME, error('Failed to build L0: %s', ME.message); end
    try, build_lvl1; fprintf('Built RFJ_L1\n'); catch ME, error('Failed to build L1: %s', ME.message); end
    try, build_lvl2; fprintf('Built RFJ_L2 (with logging)\n'); catch ME, error('Failed to build L2: %s', ME.message); end
else
    fprintf('>> Rebuild skipped.\n');
end

% Simulate L0 and L1
for k = 1:2
    mdl = sprintf('RFJ_L%d',k-1);
    T   = opt.stop(min(k,numel(opt.stop)));
    if ~bdIsLoaded(mdl), load_system(mdl); end
    fprintf('>> Simulating %s for %.3g s ...\n', mdl, T);
    sim(mdl,'StopTime',num2str(T),'FastRestart','off');
end

% Simulate L2 and export logs to base
mdl = 'RFJ_L2'; T = opt.stop(min(3,numel(opt.stop)));
if ~bdIsLoaded(mdl), load_system(mdl); end
fprintf('>> Simulating %s for %.3g s ...\n', mdl, T);
simOut = sim(mdl,'StopTime',num2str(T),'FastRestart','off','ReturnWorkspaceOutputs','on');
try, assignin('base','theta_ts', simOut.get('theta_ts')); catch, end
try, assignin('base','phi_ts',   simOut.get('phi_ts'));   catch, end
base_has = evalin('base',"exist('theta_ts','var') && exist('phi_ts','var')");
if ~base_has, error('RFJ_L2 did not produce theta_ts/phi_ts.'); end
fprintf('   L2 exported theta_ts, phi_ts for animation.\n');

% Attempt 3D; fall back to 2D
has_sm = exist(fullfile(matlabroot,'toolbox','physmod','sm','sm','sm_lib.slx'),'file')==2;
if has_sm
    try
        build_3d; fprintf('>> Simulating RFJ_3D for %.3g s\n', T);
        sim('RFJ_3D','StopTime',num2str(T));
    catch ME
        warning('3D failed (%s). Falling back to 2D.', ME.message);
        th = evalin('base','theta_ts'); ph = evalin('base','phi_ts');
        rfj_quick_anim(th, ph, 'L', 0.30, 'speed', 1.0, 'saveVideo', false);
    end
else
    warning('Simscape Multibody not detected. Showing 2D animation.');
    th = evalin('base','theta_ts'); ph = evalin('base','phi_ts');
    rfj_quick_anim(th, ph, 'L', 0.30, 'speed', 1.0, 'saveVideo', false);
end

% Optionally open models
if opt.open
    open_system('RFJ_L0'); open_system('RFJ_L1'); open_system('RFJ_L2');
    if has_sm, open_system('RFJ_3D'); end
end
fprintf('>> Done.\n');
end



