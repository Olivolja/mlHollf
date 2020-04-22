#this is to create a simple gui for file selection
import tkinter as tk
from tkinter import filedialog as fd
#this is to delete previous content from detection result
import os
#to run detector.py
import subprocess 

gui = tk.Tk()
pictureName = "" 

#Function that is run when tk.button is pressed
def selectFile():
    #Default is only to show jpg files but other options is available to select
    name = fd.askopenfilename(filetypes = (("jpeg files","*.jpg"),("png files", "*.png"),("all files","*.*")))
    print(name) #remove me when done
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

#venv path
pythonBin = os.path.join(os.path.join(os.path.join(TrainYourOwnYoloRootFolder, "env"), "bin"), "python")
#detector.py path
scriptFile = os.path.join(os.path.join(TrainYourOwnYoloRootFolder, "3_Inference"), "Detector.py")
#runs detector.py and waits for it to finish
subprocess.Popen([pythonBin, scriptFile]).wait()

#----------ABOVE WORKS -- MOVE THIS LINE WHEN MORE IS WORKING----------

#Detection_Results.csv now exists :)