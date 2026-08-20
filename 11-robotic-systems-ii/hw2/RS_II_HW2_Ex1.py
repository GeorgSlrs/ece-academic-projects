import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Academic coursework artifact. See the folder README for authorship context.
DT=0.01; TF=8.0; YREF=1.0; XREF=0.0
KPX=1.2; KDX=0.7; KPY=10.0; KDY=6.0; KPTH=12.0; KDTH=3.0; XCTL=True

def _env_float(name,default):
    v=os.getenv(name)
    try:return float(v) if v is not None else default
    except Exception:return default

def _env_bool(name,default):
    v=os.getenv(name)
    if v is None:return default
    v=str(v).strip().lower()
    if v in ('1','true','t','yes','y','on'):return True
    if v in ('0','false','f','no','n','off'):return False
    return default

DT=_env_float('DT',DT); TF=_env_float('TF',TF); YREF=_env_float('YREF',YREF); XREF=_env_float('XREF',XREF)
KPX=_env_float('KPX',KPX); KDX=_env_float('KDX',KDX); KPY=_env_float('KPY',KPY); KDY=_env_float('KDY',KDY)
KPTH=_env_float('KPTH',KPTH); KDTH=_env_float('KDTH',KDTH); XCTL=_env_bool('XCTL',XCTL)

g=9.81; m=1.0; J=0.05; kx=0.3; ky=0.3; kth=0.02
T_min=0.5*m*g; T_max=1.5*m*g; tau_min=-0.5; tau_max=0.5

def clamp(val,vmin,vmax): return np.minimum(np.maximum(val,vmin),vmax)

def world_to_body_vel(xdot,ydot,theta):
    c,s=np.cos(theta),np.sin(theta)
    return c*xdot+s*ydot,-s*xdot+c*ydot

def dynamics(x,u):
    X,Y,th,Xd,Yd,thd=np.asarray(x).reshape(-1); T,tau=np.asarray(u).reshape(-1)
    T=clamp(T,T_min,T_max); tau=clamp(tau,tau_min,tau_max)
    vx,vy=world_to_body_vel(Xd,Yd,th)
    fx=-kx*vx*abs(vx); fy=-ky*vy*abs(vy); fth=-kth*thd
    c,s=np.cos(th),np.sin(th)
    Xdd=(-s*(T+fy)+c*fx)/m; Ydd=(c*(T+fy)+s*fx)/m-g; thdd=(tau-fth)/J
    return np.array([Xd,Yd,thd,Xdd,Ydd,thdd])

def rk4_step(x,u,dt):
    k1=dynamics(x,u); k2=dynamics(x+0.5*dt*k1,u); k3=dynamics(x+0.5*dt*k2,u); k4=dynamics(x+dt*k3,u)
    return x+(dt/6.0)*(k1+2*k2+2*k3+k4)

def simulate(x0,u_fn,tf=8.0,dt=0.01):
    N=int(np.floor(tf/dt))+1; t=np.linspace(0.0,tf,N); X=np.zeros((N,6)); U=np.zeros((N,2)); X[0]=np.asarray(x0).reshape(-1)
    for k in range(N-1):
        uk=np.asarray(u_fn(t[k],X[k])).reshape(-1); U[k]=uk; X[k+1]=rk4_step(X[k],uk,dt)
    U[-1]=U[-2]; return t,X,U

def pd_hover_controller_y(y_ref=1.0,kp_y=10.0,kd_y=6.0):
    mg=m*g
    def u_y(x):
        _,y,_,_,yd,_=x
        return mg+(-kp_y*(y-y_ref)-kd_y*yd)*m
    return u_y

def pd_theta_controller(kp_th=12.0,kd_th=3.0,theta_ref_fn=None):
    if theta_ref_fn is None:theta_ref_fn=lambda x,T:0.0
    def u_theta(x,T):
        th=x[2]; thd=x[5]; th_ref=float(theta_ref_fn(x,T)); return -kp_th*(th-th_ref)-kd_th*thd
    return u_theta

def theta_ref_from_x_pd(x_ref=0.0,kp_x=1.2,kd_x=0.7,theta_limit=0.6):
    def fn(x,T):
        xpos,_,_,xdot,_,_=x; ax_des=-kp_x*(xpos-x_ref)-kd_x*xdot; T_eff=max(float(T),1e-3)
        return np.clip(-m*ax_des/T_eff,-theta_limit,theta_limit)
    return fn

def make_controller(use_x_control=True,**kwargs):
    uy=pd_hover_controller_y(kwargs.get('y_ref',1.0),kwargs.get('kp_y',10.0),kwargs.get('kd_y',6.0))
    th_ref_fn=theta_ref_from_x_pd(kwargs.get('x_ref',0.0),kwargs.get('kp_x',1.2),kwargs.get('kd_x',0.7)) if use_x_control else (lambda x,T:0.0)
    uth=pd_theta_controller(kwargs.get('kp_th',12.0),kwargs.get('kd_th',3.0),th_ref_fn)
    def u_fn(t,x):
        T_cmd=clamp(uy(x),T_min,T_max); tau_cmd=clamp(uth(x,T_cmd),tau_min,tau_max); return np.array([T_cmd,tau_cmd])
    return u_fn

def plot_all(t,X,U,y_ref,x_ref):
    plt.figure(); plt.plot(X[:,0],X[:,1]); plt.xlabel('x [m]'); plt.ylabel('y [m]'); plt.title('XY trajectory'); plt.gca().set_aspect('equal',adjustable='box'); plt.show()
    plt.figure(); plt.plot(t,X[:,1]); plt.plot(t,np.ones_like(t)*y_ref,'--'); plt.xlabel('time [s]'); plt.ylabel('altitude [m]'); plt.show()
    plt.figure(); plt.plot(t,X[:,0]); plt.plot(t,np.ones_like(t)*x_ref,'--'); plt.xlabel('time [s]'); plt.ylabel('x position [m]'); plt.show()
    plt.figure(); plt.plot(t,X[:,2]); plt.xlabel('time [s]'); plt.ylabel('theta [rad]'); plt.show()
    plt.figure(); plt.plot(t,U[:,0]); plt.axhline(T_min,ls='--'); plt.axhline(T_max,ls='--'); plt.show()
    plt.figure(); plt.plot(t,U[:,1]); plt.axhline(tau_min,ls='--'); plt.axhline(tau_max,ls='--'); plt.show()

if __name__=='__main__':
    x0=np.array([0.0,0.0,0.25,0.0,0.0,0.0])
    u_fn=make_controller(use_x_control=XCTL,y_ref=YREF,kp_y=KPY,kd_y=KDY,kp_th=KPTH,kd_th=KDTH,x_ref=XREF,kp_x=KPX,kd_x=KDX)
    t,X,U=simulate(x0,u_fn,tf=TF,dt=DT)
    print('Final state:',X[-1]); print('Final input [T, tau]:',U[-1])
    plot_all(t,X,U,YREF,XREF)
