from PIL import Image
import os
import cv2
from scipy.interpolate import interp1d
import pandas as pd
imsize = 400
path = "C:\\Users\\tobia\\Desktop\\Kandidat\\keras-retinanet\\training_files2"
new_path = "C:\\Users\\tobia\\Desktop\\Kandidat\\keras-retinanet\\training_files3"
df = pd.read_csv(r'C:\Users\tobia\Desktop\Kandidat\keras-retinanet\training_files\annotations.csv')
new_df = df
for index, row in df.iterrows():
    image = row[0]
    img = Image.open(os.path.join(path,image))
    width, height = img.size
    #print(row)
    #print((width, height))
    m_x = interp1d([0, width], [0, imsize], kind = 'linear')
    m_y = interp1d([0, height], [0, imsize])
    try:
        new_df.iat[index,1] = int(m_x(row[1]))
        new_df.iat[index,2] = int(m_y(row[2]))
        new_df.iat[index,3] = int(m_x(row[3]))
        new_df.iat[index,4] = int(m_y(row[4]))
    except:
        new_df.iat[index,1] = int(1)
        new_df.iat[index,2] = int(1)
        new_df.iat[index,3] = int(399)
        new_df.iat[index,4] = int(399)

new_df.to_csv('file_name.csv', index=False)


#    new_img = img.resize((size, size))
#    new_img.save(image)