#this is to create a simple gui for file selection
import tkinter as tk
from tkinter import filedialog as fd
#this is to delete previous content from detection result
import os

gui = tk.Tk()
pictureName = "" 

#Function that is run when tk.button is pressed
def selectFile():
    #Default is only to show jpg files but other options is available to select
    name = fd.askopenfilename(filetypes = (("jpeg files","*.jpg"),("png files", "*.png"),("all files","*.*")))
    print(name)
    pictureName = name
    gui.destroy()

errmsg = "error A-HA-HA"
#Button that calls function selectFile
tk.Button(text="Click to select a file", command=selectFile).pack(fill=tk.X)

#Opens window to select a file
gui.mainloop()
#pictureName now has the filepath of selected picture

#Get path of folder of old results
TrainYourOwnYoloRootFolder = os.path.join(os.getcwd(), "TrainYourOwnYOLO")
Data =                       os.path.join(TrainYourOwnYoloRootFolder, "Data")
SourceImages =               os.path.join(Data, "Source_Images")
TestImageDetectionResults =  os.path.join(SourceImages, "Test_Image_Detection_Results")

#Remove all previous files in Test_Image_Detection_Results
PreviousFiles = os.listdir(TestImageDetectionResults)
for file in PreviousFiles:
    os.remove(os.path.join(TestImageDetectionResults, file))

#----------ABOVE WORKS -- MOVE THIS LINE WHEN MORE IS WORKING----------

#Run decection script on our file
#os.system(os.path.join(TrainYourOwnYoloRootFolder, "3_inference")+"/Detector.py")

#me testing around different atempts
lol = print(os.listdir(os.path.join(TrainYourOwnYoloRootFolder, "3_Inference")))
os.system(lol[0])
print(os.path.join(TrainYourOwnYoloRootFolder, "3_inference")+"/Detector.py")