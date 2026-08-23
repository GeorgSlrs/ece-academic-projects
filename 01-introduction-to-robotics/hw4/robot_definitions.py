import numpy as np

class Link:
    def __init__(self, name, mass, inertia_3x3, com, home_transform):
        self.name = name
        self.mass = mass
        self.inertia_3x3_com = inertia_3x3
        self.com = com
        self.home_transform = home_transform
        self.G_link = None  # You can remove or keep, depending on your needs

class Joint:
    def __init__(
        self,
        name,
        joint_type,
        axis,
        home_transform,
        limit=None
    ):
        """
        :param name:          str, name of the joint
        :param joint_type:    str, "revolute", "prismatic", or "fixed"
        :param axis:          np.array, axis of rotation or translation
        :param home_transform dict, e.g. {'rpy':[r,p,y], 'xyz':[x,y,z]}
        :param limit:         dict or None, e.g. {
                                   'effort': float,
                                   'velocity': float,
                                   'lower': float,
                                   'upper': float
                               }
        """
        self.name = name
        self.joint_type = joint_type
        self.axis = axis
        self.home_transform = home_transform
        self.limit = limit  # store limits if provided

def get_robot_links():
    """
    Returns a list of links whose inertial parameters and
    transforms match those in the given URDF.
    """
    links = [
        # Link 0 (base) - URDF does not provide inertial, so keep it zeroed out.
        Link(
            name="arm_link_0",
            mass=0.0,
            inertia_3x3=np.zeros((3,3)),
            com=np.zeros(3),
            # The URDF has the <visual> offset at xyz=[0,0,0.02725], but
            # the link frame itself is at the origin
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0]}
        ),
        # Link 1
        Link(
            name="arm_link_1",
            mass=0.190421352,
            inertia_3x3=np.array([
                [0.000279744834534, 0,                 0],
                [0,                 0.000265717763008, 0],
                [0,                 0,                 6.53151584738e-05]
            ]),
            com=np.array([0, 0, 0.0615]),
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0.0545]}
        ),
        # Link 2
        Link(
            name="arm_link_2",
            mass=0.29302326,
            inertia_3x3=np.array([
                [0.00251484771035,  0,                0],
                [0,                 0.00248474836108, 0],
                [0,                 0,                9.19936757328e-05]
            ]),
            com=np.array([0, 0, 0.1585]),
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0.123]}
        ),
        # Link 3
        Link(
            name="arm_link_3",
            mass=0.21931466,
            inertia_3x3=np.array([
                [0.000791433503053, 0, 0],
                [0,                 0.000768905501178, 0],
                [0,                 0,                 6.88531064581e-05]
            ]),
            com=np.array([0, 0, 0.101]),
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0.317]}
        ),
        # Link 4
        Link(
            name="arm_link_4",
            mass=0.15813986,
            inertia_3x3=np.array([
                [0.00037242266488,  0,                0],
                [0,                 0.000356178538461, 0],
                [0,                 0,                4.96474819141e-05]
            ]),
            com=np.array([0, 0, 0.08025]),
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0.202]}
        ),
        # Link 5 (end-effector)
        Link(
            name="arm_link_5",
            mass=0.0,
            inertia_3x3=np.zeros((3,3)),
            com=np.zeros(3),
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0.1605]}
        ),
    ]
    return links

def get_robot_joints():
    """
    Returns a list of joints whose axes, transforms, and
    limits match those in the given URDF.
    """
    joints = [
        Joint(
            name="arm_joint_1",
            joint_type="revolute",
            axis=np.array([0,0,1]),
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0.0545]},
            limit={
                'effort': 5.0,
                'velocity': 5.0,
                'lower': -3.1415926535,
                'upper':  3.1415926535
            }
        ),
        Joint(
            name="arm_joint_2",
            joint_type="revolute",
            axis=np.array([0,1,0]),
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0.123]},
            limit={
                'effort': 5.0,
                'velocity': 5.0,
                'lower': -1.57079632679,
                'upper':  1.57079632679
            }
        ),
        Joint(
            name="arm_joint_3",
            joint_type="revolute",
            axis=np.array([0,1,0]),
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0.317]},
            limit={
                'effort': 5.0,
                'velocity': 5.0,
                'lower': -1.57079632679,
                'upper':  1.57079632679
            }
        ),
        Joint(
            name="arm_joint_4",
            joint_type="revolute",
            axis=np.array([0,1,0]),
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0.202]},
            limit={
                'effort': 5.0,
                'velocity': 5.0,
                'lower': -1.57079632679,
                'upper':  1.57079632679
            }
        ),
        Joint(
            name="arm_joint_5",
            joint_type="fixed",
            axis=np.array([0,0,0]),
            home_transform={'rpy':[0,0,0], 'xyz':[0,0,0.1605]}
            # fixed joints typically have no limits
        ),
    ]
    return joints

def get_active_joints(joints):
    """
    Filter out any joint that is 'fixed'
    """
    return [j for j in joints if j.joint_type != "fixed"]
