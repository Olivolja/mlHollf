import numpy as np
import matplotlib.pyplot as plt


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


with open('ca1_step1_input_data.txt', mode='r') as file:
    rad1 = file.readline()             # Kör 2 gånger för att printa varje rad
    rad2 = file.readline()             # Använda readline. för att använda mindre minne

    print(rad1)
    print(rad2)
    counter = 0
    signal = 2
    data = []
    tidssteg=[]
    raden = file.readline()
    for i in range(1001):
        raden = file.readline()
        tidssteg.clear()


        while not '# time_step' in raden:

            raden = raden.replace('\n', '')
            raden = raden.replace('\t', '')
            raden = raden.replace(';', ',')
            raden = raden.replace(' ', '')

            if hasNumbers(raden):

                floatskapare=[]
                raden = raden.split(',')
                for i in range(len(raden)):
                    floatskapare.append(float(raden[i]))
                tidssteg.append(floatskapare)
            if not hasNumbers(raden) and signal == 1:
                counter += 1




            raden = file.readline()

            if counter >= 401:
                break

        if '# time_step 999' in raden:
            signal = 1

        if len(tidssteg) != 0:
            data.append(tidssteg[:])

        if counter >= 401:
            break





print(len(data), len(data[0]), len(data[0][0]), type(data[0][0][0]))

rubrik = rad1.replace(';', ',')
rubrik = rubrik.replace('\n', '')
rubrik = rubrik.replace('# ', '')
rubrik = rubrik.replace(' (s)', '')
rubrik = rubrik.split(', ')

#print(rubrik)
testdata = rad2.replace(';', ',')
testdata = testdata.replace('\t', '')
testdata = testdata.replace('\n', '')
testdata = testdata.replace(' ', '')
testdata = testdata.split(',')

datafloat = []
for i in range(0, len(testdata)):
    datafloat.append(float(testdata[i]))
print(datafloat)

time_steps, time_step, radius, v_variance, N_particles = datafloat

print(time_steps, time_step, radius, v_variance, N_particles)
data = np.array(data)
print(type(data))
print(data.dtype)
print(data.shape)
print(data[0,0,0])
R = data[:,:,0:2]
V = data[:,:,2:4]
R = np.moveaxis(R,1,2)
V = np.moveaxis(V,1,2)
print(R.shape, V.shape)

plt.scatter(R[0,0,:],R[0,1,:])
plt.xlim(-1,1)
plt.ylim(-1,1)
plt.show()

