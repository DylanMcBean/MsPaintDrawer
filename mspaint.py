import pyautogui as pui
import time, datetime, random, colorama, math, sys, itertools, os, pprint
from colorama import init, Fore, Style, Back
from PIL import Image
##############################
# Functions
#############################
def load_colours(color_loc):
    colors = []
    with open(color_loc,'rb') as f:
        while True:
            b = f.read(3)
            if not b: break
            colors.append(tuple(int(b[i]) for i in range(3)))
    return colors

def distance(c1, c2):
    if type(c2) == int:
        c2 = [c2,c2,c2]
    return (c1[0] - c2[0])**2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) **2

def stroke_wait(distance):
    return (max(sys.float_info.epsilon,(distance-810000)/144000000))

def get_color_positions(img, colors,size,dithering=False):
    start_time = datetime.datetime.now()
    print(f"Getting Colour Positions: {start_time.strftime('%H:%M:%S.%f')}\r",end='')
    color_positions = [[] for col in colors]
    color_dict = {}
    px = img.load()
    for y in range(size[1]):
        for x in range(size[0]):
            checking_color = px[x,y]
            if checking_color in color_dict:
                color_positions[color_dict[checking_color]].append((x,y))
            else:
                closest_colour = sorted(colors, key=lambda color: distance(color, checking_color))[0]
                if dithering: #!DITHERING ALGORITHM
                    quant_error = [a-b for a,b in zip(checking_color,closest_colour)]
                    if x + 1 < size[0]:
                        error_col_1 = tuple(int(a+b*7.0/16.0) for a,b in zip(px[x+1,y],quant_error))
                        px[x+1,y] = error_col_1
                    if x - 1 > 0 and y + 1 < size[1]:
                        error_col_2 = tuple(int(a+b*3.0/16.0) for a,b in zip(px[x-1,y+1],quant_error))
                        px[x-1,y+1] = error_col_2
                    if y + 1 < size[1]:
                        error_col_3 = tuple(int(a+b*5.0/16.0) for a,b in zip(px[x,y+1],quant_error))
                        px[x,y+1] = error_col_3
                    if x + 1 < size[0] and y + 1 < size[1]:
                        error_col_4 = tuple(int(a+b*1.0/16.0) for a,b in zip(px[x+1,y+1],quant_error))
                        px[x+1,y+1] = error_col_4
                closest_index = colors.index(closest_colour)
                if not dithering: color_dict[checking_color] = closest_index
                color_positions[closest_index].append((x,y))
    print(f"Sorted Colour Positions: {datetime.datetime.now() - start_time}{' '*12}")
    return color_positions

def set_colour(col):
    pui.PAUSE = 0.07
    pui.click(997,78)           #click color selector
    pui.doubleClick(1473,779)   #Click Red Color 
    pui.typewrite(str(col[0]))  #Enter Red Color #F00
    pui.press('tab')
    pui.typewrite(str(col[1]))  #Enter Green Color #0F0
    pui.press('tab')
    pui.typewrite(str(col[2]))  #Enter Blue Color #00F
    pui.press('enter')
    pui.PAUSE = 0

def set_size(image_size):
    pui.PAUSE = 0.1
    pui.click(186,83)
    pui.click(73,264)
    pui.click(236,157)
    pui.press('tab')
    pui.typewrite(str(image_size[0]))
    pui.press('tab')
    pui.typewrite(str(image_size[1]))
    pui.press('enter')
    pui.PAUSE = 0

def get_strokes(color_positions,current_col=None,single=False):
    strokes = []
    pos_index = 0
    if not single:
        current_col = set(current_col[1])
    while pos_index < len(color_positions):
        start_pos = color_positions[pos_index][0]+paint_offset[0],color_positions[pos_index][1]+paint_offset[1]
        end_pos = color_positions[pos_index][0]+paint_offset[0],color_positions[pos_index][1]+paint_offset[1]
        if not single: contains_current_col = color_positions[pos_index] in current_col
        while True:
            if pos_index+1 < len(color_positions) and color_positions[pos_index+1][0]+paint_offset[0] == end_pos[0] + 1:
                pos_index += 1
                end_pos = color_positions[pos_index][0]+paint_offset[0],color_positions[pos_index][1]+paint_offset[1]
                if not single and not contains_current_col and color_positions[pos_index] in current_col:
                    contains_current_col = True
            else:
                break
        if single or contains_current_col:
            strokes.append((start_pos,end_pos))
        pos_index += 1
    return strokes

def select_palette():
    base_dir = "data/palettes"
    while True:
        os.system("cls")
        items = [os.path.join("/",x) for x in os.listdir(base_dir)]
        print(f"SELECT COLOR PALETTE\nDir: {base_dir}")
        for i in range(len(items)):
            print(f"{i}: {items[i]}")
        if base_dir != "data/palettes": print(f"{len(items)}: ..")
        index = int(input("Enter Index: "))
        if index == len(items) and base_dir != "data/palettes": 
            base_dir = '/'.join(base_dir.split("/")[:-1])
        elif ".palette" in items[index]:
            return base_dir + items[index]
        else: base_dir += items[index]
##############################
# Main
#############################
paint_offset = 5,144
main_image = Image.open("data/img.png")
image_size = main_image.size
colors = load_colours(select_palette() if len(sys.argv) < 2 else "data/palettes/" + sys.argv[1] + ".palette")
os.system("cls")
dither = input("Dithering (may slow down processing) [y/n]:")
if dither == 'y': 
    pass
color_positions = get_color_positions(main_image,colors,image_size,True) if dither == 'y' else get_color_positions(main_image,colors,image_size)
color_strokes = [get_strokes(x,single=True) for x in color_positions]
color_data = sorted([[colors[i],color_positions[i],color_strokes[i]] for i in range(len(colors))], key=lambda k: [len(k[2]), k[1], k[0]],reverse=True)

input("\nPress Enter to draw:")
#! CLEARING SCREEN
pui.click(paint_offset)
pui.hotkey('ctrl','a')
pui.press('del')
pui.click(244,71)

set_size(image_size)
paint_strokes = 0
for index in range(len(color_data)):
    if len(color_data[index][1]) > 0:
        set_colour(color_data[index][0])
        all_colours = []
        for j in range(index, len(color_data)):
            all_colours += color_data[j][1]
        all_colours = get_strokes(sorted(all_colours, key=lambda k: [k[1], k[0]]),color_data[index])
        if len(color_data[index][2]) < len(all_colours):
            all_colours = color_data[index][2]
        for stroke in all_colours:
            pui.moveTo(stroke[0])
            pui.dragTo(stroke[1])
            paint_strokes += 1
            time.sleep(stroke_wait(image_size[0]*image_size[1]))
    print(f"Strokes: {paint_strokes}\r",end='')
