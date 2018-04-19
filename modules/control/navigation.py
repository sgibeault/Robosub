import rospy
# from auv2018.msg import Navigate
from auv2018.msg import HControl
from auv2018.msg import RControl
from auv2018.msg import MControl


class Navigation():
    """
    AUV 2017 Version
    Controls thrusters to move or point AUV to a certain direction given power and direction or rotational values
    """

    def __init__(self):
        self.is_killswitch_on = False

        # used for HControl (int state, float depth) #######################################
        self.hStates = {
            'down': 0,
            'staying': 1,
            'up': 2
        }
        self.hState = None  # state

        self.depth = None  # depth (nonstop moving: -1, moving distance: x)

        # used for RControl (int state, float rotation) ####################################
        self.rStates = {
            'left': 0,  # rotate left
            'staying': 1,
            'right': 2,  # rotate right
            'rotate_front_cam_dist': 3,  # rotate with fcd
            'keep_rotate_front_cam_dist': 4  # keeping rotating with fcd
        }
        self.rState = None  # state

        self.rotation = None  # rotation (nonstop rotating: -1, rotate degree: x)

        # used for MControl (int state, int mDirection, float power, float distance) #######
        self.mStates = {
            'off': 0,
            'power': 1,  # adjust with power
            'distance': 2,  # ajust with distance
            'front_cam_center': 3,  # centered with front camera
            'bot_cam_center': 4,  # centered with bottom camera
            'motor_time': 5  # turn on motor with specific time
        }
        self.mState = None  # state

        self.directions = {
            'none': 0,
            'forward': 1,
            'right': 2,
            'backward': 3,
            'left': 4
        }

        self.mDirection = None  # mDirection

        self.power = None  # power (none: 0, motor power: x)

        self.distance = None  # distance (distance away from the object: x)

        self.runningTime = None  # runningTime (time for the motor to turn on)

    def set_h_nav(self, hState, depth):
        """
        hState: 'down': 0, 'staying': 1, 'up': 2
        depth: nonstop moving: -1, moving distance: x
        """

        if hState.isdigit():
            self.hState = hState
        else:
            self.hState = self.hStates[hState]

        self.depth = depth

    def set_r_nav(self, rState, rotation):
        """
        rState: 'left': 0, 'staying': 1, 'right': 2, 'rotate_front_cam_dist': 3, 'keep_rotate_front_cam_dist': 4
        rotation: nonstop rotating: -1, rotate degree: x
        """

        if rState.isdigit():
            self.rState = rState
        else:
            self.rState = self.rStates[rState]

        self.rotation = rotation

    def set_m_nav(self, mState, mDirection, value):
        """
        mState: 'off': 0, 'power': 1, 'distance': 2, 'front_cam_center': 3, 'bot_cam_center': 4, 'motor_time': 5
        mDirection: 'none': 0, 'forward': 1, 'right': 2, 'backward': 3, 'left': 4
        value: based on mState
            (1)power: none: 0, motor power: x
            (2)distance: distance away from the object: x
            (5)runningTime: time for the motor to turn on
        """

        if mState.isdigit():
            self.mState = mState
        else:
            self.mState = self.mStates[mState]

        if mDirection.isdigit():
            self.mDirection = mDirection
        else:
            self.mDirection = self.directions[mDirection]

        self.power = 0.0
        self.distance = 0.0
        self.runningTime = 0.0

        if self.mState == self.mStates['power']:
            self.power = value
        elif self.mState == self.mStates['distance']:
            self.distance = value
        elif self.mState == self.mStates['motor_time']:
            self.runningTime = value

    def h_nav(self, hState=None, depth=None):
        """
        Start horizontal navigation given hState and depth when killswitch is on.
        hState: 'down': 0, 'staying': 1, 'up': 2
        depth: nonstop moving: -1, moving distance: x
        """

        if self.is_killswitch_on:

            if hState is not None or depth is not None:
                self.set_h_nav(hState, depth)

            pub_h_nav = rospy.Publisher('height_control', HControl, queue_size=100)

            h_control = HControl()
            h_control.state = self.hState
            h_control.depth = self.depth

            pub_h_nav.publish(h_control)
            rospy.sleep(.1)

            print('state: %d depth: %.2f' % (self.hState, self.depth))

    def r_nav(self, rState=None, rotation=None):
        """
        Start rotational navigation given rState and rotation when killswitch is on.
        rState: 'left': 0, 'staying': 1, 'right': 2, 'rotate_front_cam_dist': 3, 'keep_rotate_front_cam_dist': 4
        rotation: nonstop rotating: -1, rotate degree: x
        """

        if self.is_killswitch_on:

            if rState is not None or rotation is not None:
                self.set_r_nav(rState, rotation)

            pub_r_nav = rospy.Publisher('rotation_control', RControl, queue_size=100)

            r_control = RControl()
            r_control.state = self.rState
            r_control.rotation = self.rotation

            pub_r_nav.publish(r_control)
            rospy.sleep(.1)

            print('state: %d rotation: %.2f' % (self.rState, self.rotation))

    def m_nav(self, mState=None, mDirection=None, value=None):
        """
        Start movement navigation given mState, mDirection, and power/distance/runningTime when killswitch is on.
        mState: 'off': 0, 'power': 1, 'distance': 2, 'front_cam_center': 3, 'bot_cam_center': 4, 'motor_time': 5
        mDirection: 'none': 0, 'forward': 1, 'right': 2, 'backward': 3, 'left': 4
        value: based on mState
            (1)power: none: 0, motor power: x
            (2)distance: distance away from the object: x
            (5)runningTime: time for the motor to turn on
        """

        if self.is_killswitch_on:

            if mState is not None or mDirection is not None or value is not None:
                self.set_m_nav(mState, mDirection, value)

            pub_m_nav = rospy.Publisher('movement_control', MControl, queue_size=100)

            m_control = MControl()
            m_control.state = self.mState
            m_control.power = self.power
            m_control.distance = self.distance
            m_control.runningTime = self.runningTime

            pub_m_nav.publish(m_control)
            rospy.sleep(.1)

            print(
                'state: %d direction: %d power: %.2f distance: %.2f runningTime: %.2f'
                % (self.mState, self.mDirection, self.power, self.distance, self.runningTime))

    def start(self):
        """Starts navigation with set preferences when killswitch is plugged in"""

        self.is_killswitch_on = True

    def stop(self):
        """Stops navigation when killswitch is unplugged"""

        self.is_killswitch_on = False
