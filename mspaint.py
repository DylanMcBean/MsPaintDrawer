import pyautogui as pui
import time, random, colorama, math, sys, itertools
from colorama import init, Fore, Style, Back
from PIL import Image
##############################
# Functions
#############################
def load_colours(color_loc):
    colors = []
    with open(color_loc) as f:
        for line in f:
            if '#' in line: colors.append(tuple(int(line.strip('#')[i:i+2], 16) for i in (0, 2, 4)))
            elif 'rgb' in line: colors.append(tuple(int(x) for x in line.strip('rgb(').replace('\n','').replace(')','').split(',')))
    return colors

def distance(c1, c2):
    if type(c2) == int:
        c2 = [c2,c2,c2]
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) **2)

def get_color_positions(img, colors, size):
    color_positions = [[] for col in colors]
    color_dict = {}
    px = img.load()
    for y in range(size[1]):
        for x in range(size[0]):
            checking_color = px[x,y]
            if checking_color in color_dict:
                color_positions[color_dict[checking_color]].append((x,y))
            else:
                closest_index = colors.index(sorted(colors, key=lambda color: distance(color, checking_color))[0])
                color_dict[checking_color] = closest_index
                color_positions[closest_index].append((x,y))
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
##############################
# Main
#############################
paint_offset = 5,144
main_image = Image.open("data/img.png")
image_size = main_image.size
colors = load_colours(f"data/palettes/{input('Enter Pallete Name:')}.palette")
color_positions = get_color_positions(main_image,colors,image_size)
color_strokes = [get_strokes(x,single=True) for x in color_positions]
color_data = sorted([[colors[i],color_positions[i],color_strokes[i]] for i in range(len(colors))], key=lambda k: [len(k[2]), k[1], k[0]],reverse=True)
pui.click(paint_offset)
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
            time.sleep(sys.float_info.epsilon)
    print(f"Strokes: {paint_strokes}\r",end='')
