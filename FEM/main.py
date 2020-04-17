import numpy as np
import core as cfc
import matplotlib.pyplot as plt


# Class used for calculating basic properties for a beam.
class Beam:
    def __init__(self,xStart,xEnd,load=np.array([[],[]]),
                 bc=[],bcVal=None,E=2.1e11,
                 A=45.3e-4,I=2510e-8):

        self.xStart = xStart
        self.xEnd = xEnd
        self.load = load
        self.bc = bc
        self.bcVal = bcVal
        self.E = E
        self.A = A
        self.I = I
        self.nel = 3
        self.ep = np.array([self.E, self.A, self.I])
        self.ex = np.array([self.xStart, self.xEnd/self.nel])
        self.ey = np.array([0., 0.])

    def get_edof(self):
        Edof = []
        for i in range(self.nel):
            Edof.append([3*i+1,3*i+2,3*i+3,3*i+4,3*i+5,3*i+6])
        Edof = np.asarray(Edof)
        return Edof

    def get_coordinates(self):
        coord = []
        for i in range(self.nel+1):
            coord.append(i/self.nel)
        return coord

    def get_stiffnes_matrix(self):
        Edof = self.get_edof()
        K = np.mat(np.zeros((Edof[-1][-1], Edof[-1][-1])))
        f = np.mat(np.zeros((Edof[-1][-1], 1)))
        for i in range(self.load.shape[1]):
            f[self.load[0][i]] = self.load[1][i]
        Ke = cfc.beam2e(self.ex, self.ey, self.ep)
        K = cfc.assem(Edof, K, Ke)
        return K,f

    def get_solutions(self):
        K,f = self.get_stiffnes_matrix()
        (a, r) = cfc.solveq(K, f, self.bc, self.bcVal)
        return a,r

    def get_section_forces(self):
        Edof = self.get_edof()
        a,r = self.get_solutions()
        Ed = cfc.extractEldisp(Edof, a)
        Es = np.empty((self.nel,2,3))
        Edi = np.empty((self.nel,2,2))
        Eci = np.empty((self.nel, 2, 1))
        for i in range(self.nel):
            es,edi,eci = cfc.beam2s(self.ex,self.ey,self.ep,Ed[i,:])
            Es[i] = es
            Edi[i] = edi
            Eci[i] = eci
        return Es

    def get_torque_diagram(self):
        Es = self.get_section_forces()
        coord = self.get_coordinates()
        Val = []
        for i in range(len(Es)):
            Val.append(Es[i][0][2])
        Val.append(Es[-1][1][2])
        plt.plot(coord,Val)

    def get_shear_diagram(self):
        Es = self.get_section_forces()
        coord = self.get_coordinates()
        Val = []
        for i in range(len(Es)):
            Val.append(Es[i][0][1])
        Val.append(Es[-1][1][1])
        plt.plot(coord,Val)

    def get_normal_force_diagram(self):
        Es = self.get_section_forces()
        coord = self.get_coordinates()
        Val = []
        for i in range(len(Es)):
            Val.append(Es[i][0][0])
        Val.append(Es[-1][0][0])
        plt.plot(coord,Val)

    def get_deformation_figure(self):
        pass


class Truss:
    def __init__(self,Edof,coordinates,bc=[],bcVal=None,A=25e-4,E=2.1e11,elements,nno):
        self.Edof = Edof
        self.coordinates = coordinates
        self.bc = bc
        self.bcVal = bcVal
        self.A = A
        self.E = E
        self.nno = nno
        self.elements = elements
        self.nel = len(elements)

    def get_edof(self):
        nodes = []
        for i in range(1,self.nno+1):
            nodes.append([2*i-1,2*i])
        nodes = np.asarray(Edof)
        Edof = []
        for e in elements:
            Edof.append([nodes[e[0]][0],nodes[e[0]][1],nodes[e[1]][0],nodes[e[1]][1]])

    def get_stiffnes_matrix(self):
        K = np.mat(np.zeros((self.Edof[-1][-1], self.Edof[-1][-1])))
        f = np.mat(np.zeros((self.Edof[-1][-1], 1)))
        for i in range(self.load.shape[1]):
            f[self.load[0][i]] = self.load[1][i]
        Ke = cfc.bar2e(self.ex, self.ey, self.ep)
        K = cfc.assem(Edof, K, Ke)
        return K,f

    def get_solutions(self):
        K,f = self.get_stiffnes_matrix()
        (a, r) = cfc.solveq(K, f, self.bc, self.bcVal)
        return a,r

    def get_normal_forces(self):
        pass


    def get_displacement(self):
        pass
