from PIL import Image
import random

#Global Constants
ENCODER = "'[](){}:,!.-?\";/ ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n"
INPUT_STR = "input.txt"
OUTPUT_STR = "output.txt"
INPUT_PNG = "input.png"
OUTPUT_PNG = "output.png"

#Encoding settings. Any values without explicit explanations may cause unexpected behavior.
#True will encode INPUT_PNG with INPUT_STR to generate OUTPUT_PNG.
#False will decode OUTPUT_PNG to generate OUTPUT_STR.
#Currently, ENCODE_MODE=False leads to an error if COLOR_MODE does not match that from the creation of the image
ENCODE_MODE = True
#0 = red, 1 = green, 2 = blue.
COLOR_MODE = 0
#0 = [0:63], 1 = [64:127], 2 = [128:191], 0 = [192:255]
#4 = random ([0:3] for each pixel)
#5 = intelligent (picks value closest to original)
STRENGTH_MODE = 5

class Container:

    def __init__(self):
        self.dict = {}
        self.buildDict()
        self.imageIn = Image.open(INPUT_PNG)
        self.xRes = self.imageIn.size[0]
        self.yRes = self.imageIn.size[1]

    #Builds a dictionary from the ENCODER string matching characters to indices
    def buildDict(self):
        for i, char in enumerate(ENCODER):
            self.dict[char] = i

    #Returns the ratio of data expressed in the string to data the image can hold
    #Must be less than 1 in order to encode a string into an image
    def getValidity(self):
        numInts = len(self.intList)
        return numInts / (self.xRes * self.yRes)

    #Encodes a string into a list of integers based on self.dict
    def encodeString(self):
        self.intList = []
        with open(INPUT_STR, 'r') as textInput:
            stringIn = textInput.read().upper()
        for char in stringIn:
            try:
                self.intList.append(self.dict[char])
            #If an illegal character appears in the string, replace it with a space instead
            except KeyError:
                self.intList.append(0)

    #Encodes a list of integers into R/G/B pixel data of a given .png file
    def encodeInts(self):
        self.pixels = self.imageIn.load()
        numInts = len(self.intList)
        for y in range(self.yRes):
            for x in range(self.xRes):
                i = (y * self.xRes) + x
                if 0 <= STRENGTH_MODE <= 3:
                    tempMode = STRENGTH_MODE
                elif STRENGTH_MODE == 4:
                    tempMode = random.randint(0,3)
                elif STRENGTH_MODE == 5:
                    tempMode = self.pixels[x,y][COLOR_MODE] // 64
                else:
                    print("STRENGTH_MODE must be an integer between 0 and 4 inclusive.")
                    exit(1)
                colorList = list(self.pixels[x,y])
                colorList[COLOR_MODE] = 64 * tempMode + self.intList[i % numInts]
                self.pixels[x,y] = tuple(colorList)
        self.imageIn.save(OUTPUT_PNG)

    #Decodes the output image into an output text file, using the ENCODER string
    def decodeImg(self):
        imageOut = Image.open(OUTPUT_PNG)
        pixels = imageOut.load()
        outString = ""
        for y in range(self.yRes):
            for x in range(self.xRes):
                charIdx = pixels[x,y][COLOR_MODE] % 64
                char = ENCODER[charIdx]
                outString += char
        with open(OUTPUT_STR, 'w') as textOutput:
            textOutput.write(outString)

def main():
    cont = Container()
    if ENCODE_MODE:
        cont.encodeString()
        dataRatio = cont.getValidity()
        if dataRatio > 1:
            print("self.imageIn does not contain enough pixels to encode theString")
            exit(1)
        else:
            #Data ratio is the percent of the image that is "filled" with the text data
            print("Data ratio: " + str(dataRatio))
        cont.encodeInts()
    else:
        cont.decodeImg()

main()