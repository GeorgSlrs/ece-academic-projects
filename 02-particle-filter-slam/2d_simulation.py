# Exported from 2d-simulation.ipynb for GitHub browsing.

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import random as r
from mpl_toolkits.mplot3d import Axes3D

# The full exported notebook source is preserved in the project archive. This browseable file
# contains the original coursework export used for differential-drive simulation, collision
# checking, lidar-style sensing, particle filtering, resampling, and map reconstruction.


def diffkin(par,u):
    th_d=(par[0]/(2*par[1]))*(u[0]-u[1])
    x_d=(par[0]/2)*(u[0]+u[1])*np.cos(par[2])
    y_d=(par[0]/2)*(u[0]+u[1])*np.sin(par[2])
    return [th_d,x_d,y_d]


def rk4(par,xk,uk,dt):
    xk1=(xk.T)[0]
    par1=[par[0],par[1],xk1[0]]
    f1=np.array(diffkin(par1,uk))
    f2=np.array(diffkin(par1+f1*dt/2,uk))
    f3=np.array(diffkin(par1+f2*dt/2,uk))
    f4=np.array(diffkin(par1+f3*dt,uk))
    return np.array([xk1+(dt/6)*(f1+2*f2+2*f3+f4)]).T

# See project-files.zip for the complete exported notebook source and remaining functions.
