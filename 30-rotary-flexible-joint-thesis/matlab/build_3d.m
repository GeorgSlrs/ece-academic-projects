function build_3d
% BUILD_3D  Simscape Multibody 3D playback (uses theta_ts, phi_ts).
% Requires Simscape Multibody. If blocks are missing, throw a clear error.

if ~evalin('base',"exist('theta_ts','var') && exist('phi_ts','var')")
    error('theta_ts/phi_ts not in base. Run RFJ_L2 (build_all does it).');
end

% helper: pick first available block path among releases
    function src = pick(cands)
        src = '';
        for i = 1:numel(cands)
            p = cands{i};
            j = strfind(p,'/'); if ~isempty(j)
                try, load_system(p(1:j(1)-1)); catch, end
            end
            try, get_param(p,'BlockType'); src = p; return; catch, end
        end
    end

MECHCFG = pick({'sm_lib/Mechanisms/Mechanism Configuration','sm_lib/Utilities/Mechanism Configuration','sm_lib/Environment/Mechanism Configuration','sm_lib/Mechanism Configuration'});
WORLD   = pick({'sm_lib/Frames and Transforms/World Frame','sm_lib/Environment/World Frame','sm_lib/World Frame'});
SOLID   = pick({'sm_lib/Body Elements/Solid','sm_lib/Body/Solid','sm_lib/Solid'});
REVJNT  = pick({'sm_lib/Joints/Revolute Joint','sm_lib/Mechanical Joints/Revolute Joint','sm_lib/Revolute Joint'});
RIGIDTF = pick({'sm_lib/Frames and Transforms/Rigid Transform','sm_lib/Transforms/Rigid Transform','sm_lib/Rigid Transform'});
S2PS    = pick({'simscape/Utilities/Simulink-PS Converter','simscape/Foundation Library/Utilities/Simulink-PS Converter'});

if any(cellfun(@isempty,{MECHCFG,WORLD,SOLID,REVJNT,RIGIDTF,S2PS}))
    error('Simscape Multibody blocks not found on this installation.');
end

mdl = 'RFJ_3D';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);

% visual sizes
L_link = 0.30; R_hub = 0.02; T_hub = 0.02;

% core blocks
add_block(MECHCFG,[mdl '/MechConfig']);
add_block(WORLD,  [mdl '/World']);
add_block(SOLID,  [mdl '/Hub']);  set_param([mdl '/Hub'], 'GeometryShape','Cylinder','CylinderRadius',num2str(R_hub),'CylinderLength',num2str(T_hub),'Color','[0.75 0.75 0.75]');
add_block(SOLID,  [mdl '/Link']); set_param([mdl '/Link'],'GeometryShape','Brick','BrickLength',num2str(L_link),'BrickWidth','0.02','BrickHeight','0.01','Color','[0.2 0.6 0.95]');
add_block(REVJNT, [mdl '/R1']); set_param([mdl '/R1'],'SpecifyPositionTarget','on','PositionTargetSource','Input');
add_block(REVJNT, [mdl '/R2']); set_param([mdl '/R2'],'SpecifyPositionTarget','on','PositionTargetSource','Input');
add_block(RIGIDTF,[mdl '/Xform_LinkOffset']); set_param([mdl '/Xform_LinkOffset'],'TranslationMethod','StandardAxis','Axis','+X','Offset',num2str(L_link/2));

% workspace signals → PS
add_block('simulink/Sources/From Workspace',[mdl '/from_theta'],'VariableName','theta_ts','OutputAfterFinalValue','Extrapolation');
add_block('simulink/Sources/From Workspace',[mdl '/from_phi'],  'VariableName','phi_ts','OutputAfterFinalValue','Extrapolation');
add_block('simulink/Math Operations/Sum',[mdl '/alpha=phi-theta'],'Inputs','+-');
add_block(S2PS,[mdl '/SPS_theta']); add_block(S2PS,[mdl '/SPS_alpha']);

% layout
set_param([mdl '/World'],'Position',[40 100 80 140]);
set_param([mdl '/R1'],   'Position',[160 90 220 150]);
set_param([mdl '/Hub'],  'Position',[280 90 340 150]);
set_param([mdl '/R2'],   'Position',[420 90 480 150]);
set_param([mdl '/Xform_LinkOffset'],'Position',[560 90 620 150]);
set_param([mdl '/Link'], 'Position',[700 90 760 150]);

set_param([mdl '/from_theta'],'Position',[120 260 200 290]);
set_param([mdl '/from_phi'],  'Position',[120 320 200 350]);
set_param([mdl '/alpha=phi-theta'],'Position',[240 300 290 340]);
set_param([mdl '/SPS_theta'],'Position',[320 260 380 290]);
set_param([mdl '/SPS_alpha'],'Position',[320 320 380 350]);

% wire mechanism
add_line(mdl,'World/R','R1/B');
add_line(mdl,'R1/F','Hub/R');
add_line(mdl,'Hub/R','R2/B','autorouting','on');
add_line(mdl,'R2/F','Xform_LinkOffset/R');
add_line(mdl,'Xform_LinkOffset/F','Link/R');

% wire signals
add_line(mdl,'from_theta/1','SPS_theta/1'); add_line(mdl,'SPS_theta/1','R1/q');
add_line(mdl,'from_phi/1','alpha=phi-theta/1'); add_line(mdl,'from_theta/1','alpha=phi-theta/2');
add_line(mdl,'alpha=phi-theta/1','SPS_alpha/1'); add_line(mdl,'SPS_alpha/1','R2/q');

save_system(mdl); fprintf('Built %s (3D playback)\n', mdl);
end

