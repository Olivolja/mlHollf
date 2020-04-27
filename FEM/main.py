import numpy as np
import core as cfc
import matplotlib.pyplot as plt

# Class used for calculating basic properties for a beam.
class Beam:
    def __init__(self,forces=[],supports=[],loads=[],
                 E=2.1e11,A=45.3e-4,I=2510e-8):
        self.forces = [[3*f[1]+2 for f in forces],[f[2] for f in forces]]
        self.loads = loads
        self.bc = self.get_boundary_conditions(supports)
        self.ep = np.array([E, A, I])
        self.ey = np.array([0., 0.])
        self.beam_parts,self.load_coords = split_beam(forces,supports,loads)
        self.nel = 11 + sum([l[1][1]-l[1][0] for l in loads])*7 # Turning all the loaded elements into 8 elements
        self.nparts = len(self.beam_parts)

        self.load_index=[i for i,part in enumerate(self.beam_parts) if part[0] in self.load_coords[0] or part[1] in self.load_coords[1]]


    def split_beam(self,forces,supports,loads):
        # We want a piece to either be under a load or from one object until the next

        # First find coordinates for all the objects
        force_coords = [f[1] for f in forces]
        support_coords = [s[1] for s in supports]
        load = [l[1] for l in loads]
        load_coords = [[start for start, stop in load],
                       [stop for start, stop in load],
                       [l[2] for l in loads]]
        split_coords = force_coords
        split_coords.extend(support_coords)
        split_coords.extend(0,11,load_coords[0],load_coords[1])
        split_coords = list(set(split_coords))
        beam_parts = [[split_coords[i],split_coords[i+1]] for i in range(len(split_coords)-1)]
        return (beam_parts, load_coords)

    def get_part_len(self,part):
        return part[1]-part[0]

    def get_edof(self):
        Edof = []
        for i in range(self.nel):
            Edof.append([3*i+1,3*i+2,3*i+3,3*i+4,3*i+5,3*i+6])
        Edof = np.asarray(Edof)
        return Edof

    def get_boundary_conditions(self,supports):
        bc = []
        for s in supports:
            if s[0] == 'RollerSupport':
                bc.extend(3*s[1]+1)

            if s[0] == 'PinSupport':
                bc.extend([3*s[1]+1, 3*s[1]+2])

            if s[0] == 'Surface'
                bc.extend([3*s[1]+1, 3*s[1]+2, 3*s[1]+3])
        return bc

    def get_coordinates(self):
        coord = []
        for i in range(self.nel+1):
            coord.append(i/self.nel)
        return coord

    def get_stiffnes_matrix(self):
        # Check if load or not

        Edof = self.get_edof()
        K = np.mat(np.zeros((Edof[-1][-1], Edof[-1][-1])))
        f = np.mat(np.zeros((Edof[-1][-1], 1)))
        for i in range(self.load.shape[1]):
            f[self.loads[1][i]] = self.loads[2][i]

        for i,p in enumerate(self.beam_parts):
            if i in self.load_index:
                ex = np.array([0, 1/8])
                eq = [0, self.load_coords[i][2]]
                Ke,fe = cfc.beam2e(ex,self.ey,self.ep,eq);
                K,f = cfc.assem(Edof,K,Ke,f,fe)
            else:
                ex = np.array([0, 1])
                Ke = cfc.beam2e(ex,self.ey,self.ep)

                K,f = cfc.assem(Edof, K, Ke, f)
        return K,f

    def get_solutions(self):
        K,f = self.get_stiffnes_matrix()
        (a, r) = cfc.solveq(K, f, self.bc)
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
    def __init__(self,Edof,coordinates,nno,elements,bc=[],bcVal=None,A=25e-4,E=2.1e11):
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

input1 = {'Beam0': [('Force', 7, 1), ('Force', 4, -1),
                    ('PinSupport', 11), ('Moment', 6, -1),
                    ('Moment', 3, 1), ('Moment', 11, 1),
                    ('Surface', 0)]}

input2 = {'Beam0': [('Force', 7, 1.0), ('Force', 4, -1.0), ('Load', (1, 3), 3.0),
                    ('PinSupport', 11), ('Moment', 6, -1.0), ('Moment', 3, 1.0),
                    ('Moment', 11, 1.0), ('Surface', 0)]}

input3 = {'Beam0': [('Force', 7, -1.0), ('Load', (3,5), -1.0), ('Load', (9,11), -1.0),
                    ('PinSupport',0),('RollerSupport', 11)]}

balkar = list(input3.keys())
balk3 = input3[balkar[0]]

def get_forces(balk):
    return [b for b in balk if b[0] in ['Force','Moment']]

def get_supports(balk):
    return [b for b in balk if b[0] in ['PinSupport','RollerSupport','Surface']]

def get_loads(balk):
    return [b for b in balk if b[0] in ['Load']]


print(get_forces(balk3))
print(get_supports(balk3))
print(get_load(balk3))
# balken = Beam(get_forces(balk1),get_supports(balk1),get_loads(balk1))
