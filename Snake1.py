
import numpy as np

# time_step 1
# x, y ; v_x, v_y


with open('ca1_step1_input_data.txt', mode='r') as file:
    rad1 = file.readline()             # Kör 2 gånger för att printa varje rad
    rad2 = file.readline()             # Använda readline. för att använda mindre minne
    print(rad1)
    print(rad2)

rubrik = rad1.replace(';', ',')
rubrik = rubrik.replace('\n', '')
rubrik = rubrik.replace('# ', '')
rubrik = rubrik.replace(' (s)', '')
rubrik = rubrik.split(', ')
print(rubrik)
data = rad2.replace(';', ',')
data = data.replace('\t', '')
data = data.replace('\n', '')
data = data.replace(' ', '')
data = data.split(',')
print(data)
print(type(data[0]))

d1 = int(data[0])
print(d1)
print(type(d1))


for x in range(len(rubrik)):
    rubrik[x] = float(data[x])



#for i in range(0, len(data)):
#    kalle.append(float(data[i]))
#print(kalle)







