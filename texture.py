
from enum import Enum
from PIL import Image
import pyautogui



class Icons(Enum):
    PLAY_BUTTON = 0
    BUBBLE_BUTTON = 1
    HANGOUT_BUTTON = 2     
    PAIMON_BUTTON = 3


class Texture:

    button_texture = []
    subbutton_texture = []

    def __init__(self, button_texture=[], subbutton_texture=[]):
        self.button_texture = button_texture
        self.subbutton_texture = subbutton_texture
    
        # Automatically setup all the textures
        self.load_icon_texture()
        self.load_SubIcon_texture()
        self.removeDuplicateSubIcons()

    
    def load_icon_texture(self):
        for icon in Icons:
            icon_texture = Image.open(f'icons\{icon.name.lower()}.png').convert("RGBA")
            self.button_texture.append(icon_texture)


    def generate_Subregion(self, iconIndex):
        # Num of columns to split icon into. 
        xSubRegions = 7
        # Num of rows to split icon into. 
        ySubRegions = 7
        subRegionWidth = 12
        subRegionHeight = 12

        for xRegion in range(0, xSubRegions):
            for yRegion in range(ySubRegions):
                # Area of new sub-icon. 
                bounds = (
                    xRegion * subRegionWidth, yRegion * subRegionHeight, (xRegion 
                    * subRegionWidth) + subRegionWidth, (yRegion * subRegionHeight)
                    + subRegionWidth
                )
                yield self.button_texture[iconIndex].crop(bounds)

    
    def load_SubIcon_texture(self):
        for icon in Icons:
            if icon == Icons.PAIMON_BUTTON:
                continue

            subIcons = []
            
            for subIcon in self.generate_Subregion(icon.value):
                pixelCount = 0
                emptyPixels = 0

                # Allows for reading color data from each pixel. 
                subIcon = subIcon.convert("RGBA")

                for pixel in Image.Image.getdata(subIcon):
                    # Pixel is empty if it's alpha component is zero. 
                    if pixel[3] == 0:
                        emptyPixels += 1
                    pixelCount += 1
                
                # Adds sub-icon to array if doesn't contain transparent pixels. 
                if emptyPixels == 0:
                    subIcons.append(subIcon)      
            self.subbutton_texture.append(subIcons)

    
    def removeDuplicateSubIcons(self):
        for icon1 in Icons:
            for icon2 in Icons:
                if icon2 == Icons.PAIMON_BUTTON:
                    continue
                # Ensures same characters icons arent compared. 
                if icon1.value == icon2.value:
                    continue
            
                for i, subIcon in enumerate(self.subbutton_texture[icon2.value]):
                    iconBounds = pyautogui.locate(subIcon, self.button_texture[icon1.value], confidence=0.98)

                    # Removes sub-icon if it can be found in a different character.
                    if iconBounds is not None:
                        self.subbutton_texture[icon2.value].pop(i)
