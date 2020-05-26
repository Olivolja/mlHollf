#if __name__ == "__main__":
import numpy as np
import core as cfc
import matplotlib.pyplot as plt

# Class used for calculating basic properties for a beam.
class Beam:
    def __init__(self,forces=[],supports=[],loads=[],
                    E=2e11,A=50e-4,I=833333/2e11):
        #self.forces = [[3*f[1]+2 for f in forces],[f[2] for f in forces]]
        self.LOADSPLITTER = 5
        self.NORMALSPLITTER = 1

        self.L = 1
        self.forces = forces
        self.loads = loads
        self.bc = self.get_boundary_conditions(supports)
        self.ep = np.array([E, A, I])
        self.ey = np.array([0., 0.])
        self.ex = np.array([0., 1/12])
        self.beam_parts,self.load_coords = self.split_beam(forces,supports,loads)
        self.nel = 12 + sum([l[1][1]-l[1][0] for l in loads])*(self.LOADSPLITTER-1) 
        self.nparts = len(self.beam_parts)
        self.load_index=[i for i,part in enumerate(self.beam_parts) if part[0] in self.load_coords[0] or part[1] in self.load_coords[1]]
        print(self.beam_parts)
        print(self.load_coords)
        K,f = self.get_stiffnes_matrix()
        print(K)
        #print(self.load_index)


    def split_beam(self,forces,supports,loads):
        force_coords = [f[1] for f in forces]
        support_coords = [s[1] for s in supports]
        load = [l[1] for l in loads]
        load_coords = [[start for start, stop in load],
                        [stop for start, stop in load],
                        [l[2] for l in loads]]
        split_coords = force_coords
        split_coords.extend(support_coords)
        split_coords.extend([0,12])
        split_coords.extend(load_coords[0])
        split_coords.extend(load_coords[1])
        split_coords = list(set(split_coords))
        split_coords.sort()
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

    def get_stiffnes_matrix(self):
        # Check if load or not
        Edof = self.get_edof()
        K = np.mat(np.zeros((Edof[-1][-1], Edof[-1][-1])))
        f = np.mat(np.zeros((Edof[-1][-1],1)))
        #print(Edof.shape)
        loads = [l[1] for l in self.loads]
        for fo in self.forces:
            c=0
            for l in loads:
                if fo[1] > l[1]:
                    c+= l[1]-l[0]

            if fo[0] == 'Force':
                #print(c)
                f[3*(self.LOADSPLITTER-1)*c+3*fo[1]+1]=fo[2]

            elif fo[0] == 'Moment':
                f[3*(self.LOADSPLITTER-1)*c+3*fo[1]+2]=fo[2]
        j=0
        load_len=0
        for i,p in enumerate(self.beam_parts):
            if i in self.load_index:
                load_len += self.load_coords[1][j]-self.load_coords[0][j]
                ex = self.ex/self.LOADSPLITTER
                eq = [0, self.load_coords[2][j]]
                Ke,fe = cfc.beam2e(ex,self.ey,self.ep,eq)
                K,f = cfc.assem(Edof[p[0]+(load_len-self.load_coords[1][j]+self.load_coords[0][j])*(self.LOADSPLITTER-1):p[1]+load_len*(self.LOADSPLITTER-1)],K,Ke,f,fe)
                #print(p[0]+(load_len-self.load_coords[1][j]+self.load_coords[0][j])*(self.LOADSPLITTER-1),p[1]+load_len*(self.LOADSPLITTER-1))

                j+=1
            else:
                ex = self.ex
                Ke = cfc.beam2e(ex,self.ey,self.ep)
                K = cfc.assem(Edof[p[0]+load_len*(self.LOADSPLITTER-1):p[1]+load_len*(self.LOADSPLITTER-1)], K, Ke)
                #print(p[0]+load_len*(self.LOADSPLITTER-1),p[1]+load_len*(self.LOADSPLITTER-1))

        return K,f

    def get_boundary_conditions(self,supports):
        loads =[l[1] for l in self.loads]
        bc = []
        for s in supports:
            c = 0
            for l in loads:
                if s[1] >= l[1]:
                    c+= l[1]-l[0]
                elif s[1] >= l[0]:
                    c+= s[1]-l[0]

            if s[0] == 'RollerSupport':
                bc.extend([3*(self.LOADSPLITTER-1)*c+3*s[1]+2])

            if s[0] == 'PinSupport':
                bc.extend([3*(self.LOADSPLITTER-1)*c+3*s[1]+1, 3*(self.LOADSPLITTER-1)*c+3*s[1]+2])

            if s[0] == 'Surface':
                bc.extend([3*(self.LOADSPLITTER-1)*c+3*s[1]+1, 3*(self.LOADSPLITTER-1)*c+3*s[1]+2, 3*(self.LOADSPLITTER-1)*c+3*s[1]+3])
        return bc


    def get_solutions(self):
        K,f = self.get_stiffnes_matrix()
        (a, r) = cfc.solveq(K, f, np.array(self.bc))
        return a,r

    def get_coordinates(self):
        coord = []
        for i,p in enumerate(self.beam_parts):
            if i in self.load_index:
                for c in range(p[0],p[1]):
                    for j in range(self.LOADSPLITTER):
                        coord.extend([self.L*(c+j/self.LOADSPLITTER)/12])

            else:
                for c in range(p[0],p[1]):
                    coord.append(self.L*c/12)

        coord.append(self.L)
        return coord

    def get_section_forces(self,p,i,eq=None):
        Edof = self.get_edof()
        a,r = self.get_solutions()
        ed = cfc.extractEldisp(Edof, a)
        if not eq is None:
            start = np.asarray(cfc.beam2s(self.ex/self.LOADSPLITTER,self.ey,self.ep,ed[i-1,:],eq=eq)[0][0])[0]
            end = np.asarray(cfc.beam2s(self.ex/self.LOADSPLITTER,self.ey,self.ep,ed[i-1,:],eq=eq)[0][1])[0]
        else:
            start = np.asarray(cfc.beam2s(self.ex,self.ey,self.ep,ed[i-1,:])[0][0])[0]
            end = np.asarray(cfc.beam2s(self.ex,self.ey,self.ep,ed[i-1,:])[0][1])[0]

        #start = np.asarray(cfc.beam2s(self.ex,self.ey,self.ep,ed[i+c])[0])[0]
        #end = np.asarray(cfc.beam2s(self.ex,self.ey,self.ep,ed[i+c])[0])[1]
        #print(start)
        #print(end)

        return start,end

    def get_torque_diagram(self):
        coord = self.get_coordinates()
        Val = []
        c=0
        j=0
        for i,p in enumerate(self.beam_parts):
            if i in self.load_index:
                eq=[0,self.load_coords[2][j]]
                j+=1
                for _ in range((p[1]-p[0])*self.LOADSPLITTER):
                    c+=1
                    #print(c)
                    Val.append(-self.get_section_forces(p,c,eq=eq)[0][2])
                    #print(self.get_section_forces(p,c,eq=eq)[0][2])
            else:
                for _ in range(p[1]-p[0]):
                    c+=1
                    Val.append(-self.get_section_forces(p,c,eq=None)[0][2])
        Val.append(-self.get_section_forces(p,c,eq=None)[1][2])
        print(coord)
        plt.plot(coord,Val)
        #plt.show()

    def get_shear_diagram(self):
        coord = self.get_coordinates()
        Val = []
        c=0
        j=0
        for i,p in enumerate(self.beam_parts):
            if i in self.load_index:
                eq=[0,self.load_coords[2][j]]
                j+=1
                for _ in range((p[1]-p[0])*self.LOADSPLITTER):
                    c+=1
                    #print(c)
                    Val.append(self.get_section_forces(p,c,eq=eq)[0][1])
                    #print(self.get_section_forces(p,c,eq=eq)[0][1])
            else:
                for _ in range(p[1]-p[0]):
                    c+=1
                    #print(c)
                    Val.append(self.get_section_forces(p,c,eq=None)[0][1])
        Val.append(self.get_section_forces(p,c,eq=None)[1][1])
        #print(Val)
        #print(coord)
        plt.plot(coord,Val)
        #plt.show()

    def get_normal_force_diagram(self):
        coord = self.get_coordinates()
        Val = []
        c=0
        j=0
        for i,p in enumerate(self.beam_parts):
            if i in self.load_index:
                eq=[0,self.load_coords[2][j]]
                j+=1
                for _ in range((p[1]-p[0])*self.LOADSPLITTER):
                    c+=1
                    #print(c)
                    Val.append(self.get_section_forces(p,c,eq=eq)[0][0])
                    #print(self.get_section_forces(p,c,eq=eq)[0][0])
            else:
                for _ in range(p[1]-p[0]):
                    c+=1
                    #print(c)
                    Val.append(self.get_section_forces(p,c,eq=None)[0][0])
        Val.append(self.get_section_forces(p,c,eq=None)[1][0])
        #print(Val)
        #print(coord)
        plt.plot(coord,Val)
        plt.show()

    def get_mesh(self):
        coo = np.asarray(self.get_coordinates()).reshape(self.nel+1,1)
        edof = np.asarray(self.get_edof())
        dof=[]
        for i in range(self.nel+1):
            dof.append([3*i+1,3*i+2,3*i+3])
        dof = np.asarray(dof)
        ex = cfc.coordxtr(edof,coo,dof)
        for i in ex:
            plt.plot(i,[0,0],'k.')
            plt.plot(i,[0,0],'k')

    def get_deflection(self):
        a, r = self.get_solutions()
        coord = self.get_coordinates()
        y=[]
        for i in range(self.nel+1):
            y.append(a[3*i+1])
        plt.plot(coord, np.asarray(y).reshape((self.nel+1,)),linewidth=8)
        plt.plot([0, self.L], [0, 0],'--',linewidth=4)
        minvalue = np.min(y)
        maxvalue = np.max(y)
        absmax = max([abs(minvalue),maxvalue])
        plt.ylim(top=absmax*2,bottom=-absmax*2)
        plt.title("Balkens utböjning",size=20)
        plt.legend(['Balkens utböjning','Normallinje'])
        plt.ylabel('Balkens utböjning [m]', size = 10)
        plt.xlabel('Balkens längd [m]', size = 10)

'''

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

'''

input1 = {'Beam0': [('Force', 7, 1), ('Force', 4, -1),
                    ('PinSupport', 11), ('Moment', 6, -1),
                    ('Moment', 3, 1), ('Moment', 11, 1),
                    ('Surface', 0)]}

input2 = {'Beam0': [('Force', 7, 1.0), ('Force', 4, -1.0), ('Load', (1, 3), 0.5),
                    ('PinSupport', 11), ('Moment', 6, -1.0), ('Moment', 3, 1.0),
                    ('Moment', 11, 1.0), ('Surface', 0)]}

input3 = {'Beam0': [('Force', 7, -0.1), ('Load', (3,5), -0.1), ('Load', (9,11), -1.0),
                    ('PinSupport',0),('RollerSupport', 11)]}

inputJim = {'Beam0': [('Force', 11, 1.0), ('Load', (0, 3), -9), ('PinSupport', 0), ('RollerSupport', 8)]}

balkar = list(input1.keys())
balk3 = input1[balkar[0]]

def get_forces(balk):
    return sorted([b for b in balk if b[0] in ['Force','Moment']],key=lambda tup: tup[1])

def get_supports(balk):
    return sorted([b for b in balk if b[0] in ['PinSupport','RollerSupport','Surface']],key=lambda tup: tup[1])

def get_loads(balk):
    return sorted([b for b in balk if b[0] in ['Load']],key=lambda tup: tup[1][0])


#print(get_forces(balk3))
#print(get_supports(balk3))
#print(get_loads(balk3))
forc = [('Force',11,1.0)]
supp = [('PinSupport', 0),('RollerSupport',7)]
loads = [('Load̈́',(0,3),-0.01)]
#balken = Beam(get_forces(balk3),get_supports(balk3),get_loads(balk3))
#balken.get_shear_diagram()


# coo = np.asarray(balken.get_coordinates()).reshape(28,1)
# edof = np.asarray(balken.get_edof())
# dof=[]
# for i in range(28):
#     dof.append([3*i+1,3*i+2,3*i+3])
# dof = np.asarray(dof)
# ex = cfc.coordxtr(edof,coo,dof)
# for i in ex:
#     plt.plot(i,[0,0],'k.')
#     plt.plot(i,[0,0],'k')
# #plt.show()

def FEM_main(balk_input,i):
    balkar = list(balk_input.keys())
    balk = balk_input[balkar[0]][3]
    balken = Beam(get_forces(balk),get_supports(balk),get_loads(balk))
    print(i)
    plt.figure()
    if i == 0:
       balken.get_shear_diagram()
    if i == 1:
       balken.get_normal_force_diagram()
    if i == 2:
       balken.get_torque_diagram()
    if i == 3:
       balken.get_deflection()
    plt.show()

inin = {'Beam0': (5.0,'0', 833333.3333333335, [('Force', 12, 1.0), ('Force', 10, 1.0), ('Force', 7, -1.0), ('Force', 4, -1.0), ('Force', 2, -1.0), ('PinSupport', 8), ('PinSupport', 5), ('RollerSupport', 12), ('RollerSupport', 0)])}

#FEM_main(inin,2)
#plt.figure()
#FEM_main(inin,3)
#plt.show()