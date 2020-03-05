import numpy as np
import core as cfc
import matplotlib.pyplot as plt


# Class used for calculating basic properties for a beam.
class Beam:
    # Calculating the displacement along the beam using the library CALFEM.
    def __init__(self,xStart,xEnd,last=np.array([[],[]]),bc=[],bcVal=None,):
        self.xStart = xStart
        self.xEnd = xEnd
        self.last = last
        self.bc = bc
        self.bcVal = bcVal


        nel = 3
        Edof = []
        for i in range(nel):
            Edof.append([3*i+1,3*i+2,3*i+3,3*i+4,3*i+5,3*i+6])
        Edof = np.asarray(Edof)
        print(Edof)

        self.coord = []
        for i in range(nel+1):
            self.coord.append(i/nel)
        print(self.coord)
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
        Es = np.empty((nel,2,3))
        Edi = np.empty((nel,2,2))
        Eci = np.empty((nel, 2, 1))
        for i in range(nel):
            es,edi,eci = cfc.beam2s(ex,ey,ep,Ed[i,:])
            Es[i] = es
            Edi[i] = edi
            Eci[i] = eci
        self.Es = Es
        self.Edi = Edi
        self.Eci = Eci



    # Method used to plot the torque along the beam
    def TorqueDiagram(self):
        Val = []
        for i in range(len(self.Es)):
            Val.append(self.Es[i][0][2])

        Val.append(self.Es[-1][1][2])
        print(Val)
        plt.plot(self.coord,Val)
        plt.show()

    # Method used to plot the shear forces along the beam
    def ShearDiagram(self):
        Val = []
        for i in range(len(self.Es)):
            Val.append(self.Es[i][0][1])
        Val.append(self.Es[-1][1][1])


        plt.plot(self.coord,Val)
        plt.show()

    #Method used to plot the normal force along the beam
    def NormalForce(self):
        Val = []
        for i in range(len(self.Es)):
            Val.append(self.Es[i][0][0])
        Val.append(self.Es[-1][0][0])
        plt.plot(self.coord,Val)
        plt.show()

    # Method used to plot the deformation of the beam
    def DeformationFigure(self):
        pass


class truss:
    pass

balk1 = Beam(0,1,np.array([[7],[-1000]]),np.array([1,2,11]),np.array([0,0,0]))
balk1.ShearDiagram()
balk1.TorqueDiagram()