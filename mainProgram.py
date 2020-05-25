import tkinter as tk #this is to create a simple gui for file selection
from tkinter import filedialog as fd #file selector
import os #this is to delete previous content from folders
import shutil #copying files
import subprocess #to run detector.py
import platform #need this to check if system is running windows/linux/macos
#TODO add requirment file that will install when run?

selectedPicture = ""
gui = tk.Tk()
#Function that is run when tk.button is pressed
def selectFile():
    global selectedPicture
    #Default is only to show jpg files but other options is available to select
    selectedPicture = fd.askopenfilename(filetypes = (("jpeg files","*.jpg"),("png files", "*.png"),("all files","*.*")))
    gui.destroy()
errmsg = "error A-HA-HA"
#Button that calls function selectFile
tk.Button(text="Click to select a file", command=selectFile).pack(fill=tk.X)
#Opens window to select a file
gui.mainloop()



#Get path of folder of old results
TrainYourOwnYoloRootFolder = os.path.join(os.getcwd(), "TrainYourOwnYOLO")
SourceImages =               os.path.join(TrainYourOwnYoloRootFolder, "Data/Source_Images")
#SourceImages =               os.path.join(Data, "Source_Images")
#TODO This block is a workaround from that i dint not find a wasy for a subprocess to take an argument simultaneusly as running it from the venv
#---------------------------------------------------------------------
testImages =  os.path.join(SourceImages, "Test_Images")
OldTestFiles = os.listdir(testImages)
for file in OldTestFiles:
    os.remove(os.path.join(testImages, file))
shutil.copy(selectedPicture, testImages)
#---------------------------------------------------------------------



#Remove all previous files in Test_Image_Detection_Results
#fails if no previous test results exist but in that case you can skip this step
try :
    TestImageDetectionResults =  os.path.join(SourceImages, "Test_Image_Detection_Results")
    OldTestResults = os.listdir(TestImageDetectionResults)
    for file in OldTestResults:
        os.remove(os.path.join(TestImageDetectionResults, file))
except (FileNotFoundError):
    pass



#check os and get path to venv

if(platform.system() == "Linux"):
    #venv path
    pythonBin = os.path.join(TrainYourOwnYoloRootFolder, "env/bin/python")
elif (platform.system() == "Windows"):
    #raise Exception("we dont support Windows as of this moment. Please get another OS or trying another software")
    pythonBin = os.path.join(TrainYourOwnYoloRootFolder, "env/Scrips/python")
elif (platform.system() == "Darwin"):
    raise Exception("we dont support MacOS as of this moment. Please get another OS or trying another software")
else:
    raise Exception("we could not find what OS you are running")


#detector.py path
scriptFile = os.path.join(TrainYourOwnYoloRootFolder, "3_Inference/Detector.py")
#runs detector.py and waits for it to finish
subprocess.Popen([pythonBin, scriptFile]).wait() #TODO make scriptFile take argument selectedPicture
#Detection_Results.csv now exists 


#----------ABOVE WORKS -- MOVE THIS LINE WHEN MORE IS WORKING----------

import Image_generator3

