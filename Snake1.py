
import numpy as np

# time_step 1
# x, y ; v_x, v_y

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)



with open('ca1_step1_input_data.txt', mode='r') as file:
    rad1 = file.readline()             # Kör 2 gånger för att printa varje rad
    rad2 = file.readline()             # Använda readline. för att använda mindre minne
    #print(rad1)
    #print(rad2)

    data = []
    partikel=[]

    for i in range(1000):
        raden = file.readline()
        partikel.clear()
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
                partikel.append(floatskapare)
            raden = file.readline()
        data.append(partikel)

print(len(data), len(data[0]), len(data[0][0]), type(data[0][0][0]))

rubrik = rad1.replace(';', ',')
rubrik = rubrik.replace('\n', '')
rubrik = rubrik.replace('# ', '')
rubrik = rubrik.replace(' (s)', '')
rubrik = rubrik.split(', ')
#print(rubrik)
data = rad2.replace(';', ',')
data = data.replace('\t', '')
data = data.replace('\n', '')
data = data.replace(' ', '')
data = data.split(',')

datafloat = []
for i in range(0, len(data)):
    datafloat.append(float(data[i]))
#print(datafloat)

time_steps, time_step, radius, v_variance, N_particles = datafloat

#print(time_steps, time_step, radius, v_variance, N_particles)







