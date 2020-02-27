import numpy as np
import core as cfc


# Class used for calculating basic properties for a beam.
class Beam:
    # Calculating the displacement along the beam using the library CALFEM.
    def __init__(self,xStart,xEnd,last=np.array([[],[]]),bc=[],bcVal=None,):
        self.xStart = xStart
        self.xEnd = xEnd
        self.last = last
        self.bc = bc
        self.bcVal = bcVal
        nel = 4
        # Element degrees of freedom, based on the coordinates from the yolo-file.
        Edof = np.array([[1, 2, 3, 4, 5, 6],
                         [4, 5, 6, 7, 8, 9],
                         [7, 8, 9, 10, 11, 12],
                         [10,11,12,13,14,15]])

        # Stiffnes matrix and load vector based on the total degrees of freedom
        K = np.mat(np.zeros((Edof[-1][-1], Edof[-1][-1])))
        f = np.mat(np.zeros((Edof[-1][-1], 1)))
        for i in range(last.shape[1]):
            f[last[0][i]] = last[1][i]

        E = 2.1e11
        A = 45.3e-4
        I = 2510e-8
        ep = np.array([E, A, I])
        ex = np.array([xStart, xEnd/nel])
        ey = np.array([0., 0.])

        Ke = cfc.beam2e(ex, ey, ep)
        K = cfc.assem(Edof, K, Ke)

        # Finding the variables:
        # a - solution of the system of equations
        # r - support forces
        (a, r) = cfc.solveq(K, f, bc, bcVal);

        self.a = a
        self.r = r

        # Solution of the equation for each element.
        Ed = cfc.extractEldisp(Edof, a);

        es1, ed1, ec1 = cfc.beam2s(ex,ey,ep,Ed[1,:])

    # Method used to plot the torque along the beam
    def TorqueDiagram(self):
        pass

    # Method used to plot the shear forces along the beam
    def ShearDiagram(self):
        pass

    #Method used to plot the normal force along the beam
    def NormalForce(self):
        pass

    # Method used to plot the deformation of the beam
    def DeformationFigure:
        pass

class truss:
    pass

balk1 = Beam(0,1,np.array([[7],[-1000]]),np.array([1,2,14]),np.array([0,0,0]))
