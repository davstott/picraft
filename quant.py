#Take a source image and render it into Minecraft, Pi Edition
#assumes the Minecraft PI edition api is in the mcpi subdirectory
import Image, mcpi.minecraft
Debug = False

# palette values taken from http://teaminterrobang.com/showthread.php?35959-Minecraft-wool-color-Photoshop-ACO-file
# these could also be worked out from averaging the colours from the sprites in mcpi/data/images/terrain.png
# and extended by including other block types, but 16 colours works ok
colours = {"White": {"argb": "FFe4e4e4", "tileId": 0},
           "Light Grey": {"argb": "FFa0a7a7", "tileId": 8}, 
           "Dark Grey": {"argb": "FF414141", "tileId": 9},
           "Black": {"argb": "FF181414", "tileId": 15},
           "Red": {"argb": "FF9e2b27", "tileId": 14},
           "Orange": {"argb": "FFea7e35", "tileId": 1},
           "Yellow": {"argb": "FFc2b51c", "tileId": 4}, 
           "Lime Green": {"argb": "FF39ba2e", "tileId": 5},
           "Green": {"argb": "FF364b18", "tileId": 13},
           "Light Blue": {"argb": "FF6387d2", "tileId": 3},
           "Cyan": {"argb": "FF267191", "tileId": 9},
           "Blue": {"argb": "FF253193", "tileId": 11},
           "Purple": {"argb": "FF7e34bf", "tileId": 10},
           "Magenta": {"argb": "FFbe49c9", "tileId": 2},
           "Pink": {"argb": "FFd98199", "tileId": 6},
           "Brown": {"argb": "FF56331c", "tileId": 12}}

# store the tileIDs by the offset in the resulting palette List for later lookup
tileIdsByOffset = []

# create our intermediate image to do nothing but hold our palette
mcImage = Image.new("P", (1, 1))
palette = []
for name in colours:
  val = colours[name]["argb"]
  colours[name]["r"] = int(val[2:4], 16)
  colours[name]["g"] = int(val[4:6], 16)
  colours[name]["b"] = int(val[6:8], 16)
  tileIdsByOffset.append(colours[name]["tileId"])
  if Debug:
    print name, val, colours[name]["r"], colours[name]["g"], colours[name]["b"]
  palette.extend((colours[name]["r"], colours[name]["g"], colours[name]["b"]))

palette.extend((0,0,0) * (256 - len(colours)))
if Debug:
  print len(palette), palette

mcImage.putpalette(palette)

#Source image from Ordnance Survey 1:250k color raster using their openspace api. Its geographic parameters are:
#BBOX=460000,450000,470000,460000
HEIGHT=200
WIDTH=200

# plot the minecraft blocks at this Z position
z = 10

#TODO: read this png from a filename argument and eventually from http to a wms service
inputImage = Image.open("york.png")
#ensure the input image is a full 24bit RGB, then create a new quantised image using the intermediate image holding our palette
outputImage = inputImage.convert("RGB").quantize(palette = mcImage)
if Debug:
  #save the quantised image so we can look at it 
  outputImage.save("output.png")

#open a connection to our minecraft instance, defaulting to localhost
mc = mcpi.minecraft.Minecraft.create()

#if we assume the most common colour will be white, we can pre-paint the backgrund to save many setBlock()s
#35, 0 is tileID for wool, tileData for white
mc.setBlocks(0,z,0,WIDTH,z,HEIGHT,35,0)

#this is going to be verrrry slow to use nested loops with getPixel(). srsly. slow. but minecraft's setBlock() is slower.
for x in range(WIDTH):
  for y in range(HEIGHT):
    # fetch the pixel value at the current position, the units are the indexes into our palette
    pix = outputImage.getpixel((x,y)) 
    if (pix < len(tileIdsByOffset)):
      # lookup the minecraft wool tiledata ID for this palette entry
      tileColour = tileIdsByOffset[pix] 
    else:
      # didn't find one, so default to white
      tileColour = 0      
    if Debug:
      print x, y, pix, tileColour
    if (tileColour != 0):
      # only draw a block if it's not white. 35 is the block ID for wool
      mc.setBlock(x, z, y, 35, tileColour)

