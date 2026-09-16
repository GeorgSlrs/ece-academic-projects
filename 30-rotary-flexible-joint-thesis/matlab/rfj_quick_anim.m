function rfj_quick_anim(theta_ts_in, phi_ts_in, varargin)
% RFJ_QUICK_ANIM  (prettier v2) 2D animation for the rotary flexible joint.
% Drop-in replacement: same name/signature as before, nicer visuals, robust
% stop (Esc or Stop button), optional MP4 recording.
%
% Usage (unchanged):
%   rfj_quick_anim(theta_ts, phi_ts, 'L',0.30, 'speed',1.0, 'saveVideo',false)

% -------- options (compat with old) --------
p = inputParser;
p.addParameter('L', 0.30);
p.addParameter('R', 0.018);
p.addParameter('gap', 0.020);
p.addParameter('springTurns', 10);
p.addParameter('springAmp', 0.010);
p.addParameter('symOffset', 0.018);
p.addParameter('minVisualLen', 0.06);
p.addParameter('speed', 1.0);
p.addParameter('saveVideo', false);
p.addParameter('filename','RFJ_2D.mp4');
p.addParameter('trailLen', 120);   % number of tip points to keep
p.parse(varargin{:});
opt = p.Results;

% -------- fetch timeseries --------
if nargin < 2
    theta_ts_in = evalin('base','theta_ts');
    phi_ts_in   = evalin('base','phi_ts');
end
[tt, th] = to_arrays(theta_ts_in);
[tp, ph] = to_arrays(phi_ts_in);
t0 = max(min(tt), min(tp));  tf = min(max(tt), max(tp));
t  = linspace(t0, tf, max(400, max(numel(tt),numel(tp))));
theta = interp1(tt, th, t, 'linear', 'extrap');
phi   = interp1(tp, ph, t, 'linear', 'extrap');
alpha = theta - phi;

% -------- figure & theme --------
L=opt.L; R=opt.R;
fig = figure('Name','Rotary Flexible Joint (2D)','Color',[1 1 1],'Renderer','opengl');
ax  = axes(fig); hold(ax,'on'); axis(ax,'equal'); box(ax,'on'); grid(ax,'on');
ax.GridAlpha = 0.10; ax.LineWidth = 0.8;
lim = 1.25*L; axis(ax,[-lim lim -lim lim]);
xlabel(ax,'x [m]'); ylabel(ax,'y [m]');
title(ax,'Rotary Flexible Joint (2D)','FontWeight','bold');

% graceful stop
setappdata(fig,'rfj_stop',false);
set(fig,'KeyPressFcn',@(s,e) strcmp(e.Key,'escape') && setappdata(fig,'rfj_stop',true));
uicontrol('Style','pushbutton','String','Stop','Units','normalized', ...
          'Position',[0.90 0.93 0.08 0.06], 'Callback',@(s,e)setappdata(fig,'rfj_stop',true));
set(fig,'CloseRequestFcn',@(src,evt)setappdata(src,'rfj_stop',true));

% base plate + hub shadow
patch(ax,[-lim -lim lim lim],[-0.02 -0.06 -0.06 -0.02],[0.96 0.96 0.98], ...
      'EdgeColor',[0.85 0.85 0.90],'LineWidth',1);
rectangle(ax,'Position',[-R*1.25 -R*1.25 2.5*R 2.5*R],'Curvature',[1 1], ...
          'FaceColor',[0 0 0 0.06],'EdgeColor','none');

% hub + tick
rectangle(ax,'Position',[-R -R 2*R 2*R],'Curvature',[1 1], ...
          'FaceColor',[0.88 0.89 0.92],'EdgeColor',[0.15 0.15 0.2],'LineWidth',1.2);
hub_tick = plot(ax,[0 R*cos(theta(1))],[0 R*sin(theta(1))],'-','Color',[0.1 0.1 0.2],'LineWidth',2);

% link + tip + short trail
link  = plot(ax,[0 L*cos(phi(1))],[0 L*sin(phi(1))],'-','LineWidth',6,'Color',[0.22 0.54 0.93]);
tip   = plot(ax,L*cos(phi(1)),L*sin(phi(1)),'o','MarkerSize',8, ...
             'MarkerFaceColor',[0.22 0.54 0.93],'MarkerEdgeColor',[0.1 0.1 0.2]);
trail = animatedline(ax,'LineWidth',1.5,'Color',[0.25 0.25 0.25 0.35]);

% small hub labels
text(ax, 0.00, +0.03, 'x_s', 'FontAngle','italic', 'Color',[0.2 0.2 0.2]);
text(ax,-0.03,  0.00, 'C_s', 'FontAngle','italic', 'Color',[0.2 0.2 0.2]);

% spring/damper placeholders
spring_h  = plot(ax,nan,nan,'-','Color',[0.25 0.25 0.25],'LineWidth',2);
spring_lbl= text(ax,0,0,'K_s','HorizontalAlignment','center','Color',[0.25 0.25 0.25]);
[dam_p1,dam_p2,dam_rod,dam_box,dam_lbl] = damper_handles(ax);

% HUD
hud = text(ax,-lim*0.98, +lim*0.95, hudStr(t(1),theta(1),phi(1),alpha(1)), ...
           'FontName','Consolas','VerticalAlignment','top','FontSize',10);

% optional recording
if opt.saveVideo, vw = VideoWriter(opt.filename,'MPEG-4'); vw.FrameRate = 30; open(vw); end

% -------- animate --------
tic; t_start = t(1);
trailX = nan(opt.trailLen,1); trailY = nan(opt.trailLen,1); ti = 0;

for k = 1:numel(t)
    if ~ishandle(fig) || getappdata(fig,'rfj_stop'), break; end
    if ~all(isgraphics([hub_tick link tip spring_h dam_p1 dam_p2 dam_rod dam_box])), break; end

    % pacing
    elapsed = toc*opt.speed; target = t(k)-t_start;
    if elapsed < target, pause(target - elapsed); end
    if ~ishandle(fig) || getappdata(fig,'rfj_stop'), break; end

    % hub & link
    set(hub_tick,'XData',[0 R*cos(theta(k))],'YData',[0 R*sin(theta(k))]);
    set(link,    'XData',[0 L*cos(phi(k))],'YData',[0 L*sin(phi(k))]);
    set(tip,     'XData', L*cos(phi(k)),   'YData', L*sin(phi(k)));

    % trail
    ti = ti + 1; trailX(mod(ti-1,opt.trailLen)+1) = L*cos(phi(k));
    trailY(mod(ti-1,opt.trailLen)+1) = L*sin(phi(k));
    clearpoints(trail); addpoints(trail, trailX(~isnan(trailX)), trailY(~isnan(trailY)));

    % anchors (hub tick end vs link root)
    pm  = [ R*cos(theta(k))      , R*sin(theta(k))      ];
    pl0 = [(R+opt.gap)*cos(phi(k)), (R+opt.gap)*sin(phi(k))];
    v = pl0 - pm;  len = hypot(v(1),v(2));
    if len < opt.minVisualLen, u = v / max(len,1e-9); pl = pm + opt.minVisualLen*u; else, pl = pl0; end
    u = (pl - pm); u = u / max(hypot(u(1),u(2)),1e-12);
    n = [-u(2) u(1)];
    pm_off = pm + opt.symOffset*n;  pl_off = pl + opt.symOffset*n;

    % spring
    [xs,ys] = coil_points(pm_off, pl_off, opt.springTurns, opt.springAmp);
    set(spring_h,'XData',xs,'YData',ys);
    set(spring_lbl,'Position',[mean([pm_off(1) pl_off(1)]) mean([pm_off(2) pl_off(2)])+0.02 0]);

    % damper (mirrored)
    pm_d = pm - opt.symOffset*n;  pl_d = pl - opt.symOffset*n;
    damper_draw(dam_p1,dam_p2,dam_rod,dam_box, pm_d, pl_d);
    set(dam_lbl,'Position',[mean([pm_d(1) pl_d(1)]) mean([pm_d(2) pl_d(2)])-0.02 0], 'String','C_s');

    % HUD
    if isgraphics(hud), hud.String = hudStr(t(k),theta(k),phi(k),alpha(k)); end

    drawnow;
    if opt.saveVideo && ishandle(fig), writeVideo(vw, getframe(fig)); end
end

if opt.saveVideo, try, close(vw); catch, end, end
if ishandle(fig) && getappdata(fig,'rfj_stop'), delete(fig); end
end

% ===== helpers =====
function s = hudStr(t,th,ph,al)
s = sprintf('t=%5.2f s   \\theta=%+5.2f rad   \\phi=%+5.2f rad   \\alpha=%+5.2f rad', t, th, ph, al);
end
function [p1,p2,rod,box,lbl] = damper_handles(ax)
p1  = plot(ax,nan,nan,'-','Color',[0.1 0.1 0.15],'LineWidth',3);
p2  = plot(ax,nan,nan,'-','Color',[0.1 0.1 0.15],'LineWidth',3);
rod = plot(ax,nan,nan,'-','Color',[0.2 0.2 0.25],'LineWidth',2);
box = patch('XData',nan,'YData',nan,'FaceColor',[.70 .70 .72],'EdgeColor',[0.15 0.15 0.2]);
lbl = text(ax,0,0,'','HorizontalAlignment','center','Color',[0.2 0.2 0.2]);
end
function damper_draw(p1,p2,rod,box, p0,p1pt)
v = p1pt - p0; L = max(hypot(v(1),v(2)),1e-12); u = v/L; n = [-u(2) u(1)];
plateW = 0.014; plateH = 0.006;
c1 = p0 + 0.28*L*u; c2 = p0 + 0.72*L*u;
set(p1,'XData',[c1(1)-plateH*u(1) c1(1)+plateH*u(1)], 'YData',[c1(2)-plateH*u(2) c1(2)+plateH*u(2)]);
set(p2,'XData',[c2(1)-plateH*u(1) c2(1)+plateH*u(1)], 'YData',[c2(2)-plateH*u(2) c2(2)+plateH*u(2)]);
set(rod,'XData',[c1(1) c2(1)], 'YData',[c1(2) c2(2)]);
B = 0.6*(c1 + c2);  w = plateW; h = 0.5*plateH;
rect = [ -h -w;  h -w;  h  w; -h  w ]';
R = [u(:) n(:)]; rectW = R*rect + B.';  % rotate small box
set(box,'XData',rectW(1,:),'YData',rectW(2,:));
end
function [xs,ys] = coil_points(p0, p1, turns, amp)
v = p1 - p0; L = max(hypot(v(1),v(2)),1e-9);
ang = atan2(v(2), v(1));
s = linspace(0, L, max(140, 12*turns));
w = 2*pi*turns/L; y = amp * sin(w*s);
Rz = [cos(ang) -sin(ang); sin(ang) cos(ang)];
pts = (Rz * [s; y]).'; xs = pts(:,1) + p0(1); ys = pts(:,2) + p0(2);
end
function [t,x] = to_arrays(ts)
if isa(ts,'timeseries'), t=ts.Time; x=ts.Data;
elseif istimetable(ts),  t=seconds(ts.Time-ts.Time(1)); x=ts.Variables;
elseif isstruct(ts) && isfield(ts,'time') && isfield(ts,'signals')
    t=ts.time; x=ts.signals.values;
else, error('Unsupported time series type.');
end
t=t(:); x=x(:);
end



