import http_framework.interfaceUtils
import src.manipulation
from enum import Enum

### Returns a string containing the block names.
import src.states


def download_area(origin_x, origin_y, origin_z, end_x, end_y, end_z, flexible_tiles=False, leave_dark_oak=True):
    print("downloading area")
    block_string = ""
    dir_x = 1
    dir_y = 1
    dir_z = 1
    if end_x < origin_x:
        dir_x = -1
        # origin_x, end_x = end_x, origin_x
    if end_y < origin_y:
        dir_y = -1
    # origin_x, end_x = end_x, origin_x
    if end_z < origin_z:
        dir_z = -1
    # for y in range(origin_y, end_y, 1):
    woods = []
    if leave_dark_oak:
        woods = ["oak", "spruce", "birch", "acacia", "jungle"]  # woods that are determined to be switcheable. leaving out oak as an aesthetic cohice
    else:
        woods = ["dark", "oak", "spruce", "birch", "acacia", "jungle"]  # woods that are determined to be switcheable. leaving out oak as an aesthetic cohice

    for y in range(end_y, origin_y-dir_y, -dir_y):
        for z in range(origin_z, end_z+dir_z, dir_z):
            for x in range(origin_x, end_x+dir_x, dir_x):
                block = http_framework.interfaceUtils.getBlock(x, y, z)[10:].ljust(100, ' ')  # polished_blackstone_brick_stairs

                if flexible_tiles:
                    first_underscore = None
                    if '_' in block:
                        first_underscore = block.index('_')
                    if block[:8] == 'stripped':
                        # stripped_oak_log
                        block = "#9stripped__log"
                    elif block[-3:] == 'log':
                        block = '#0_log'  # index 0 is where you want to stick the type right after you remove the #0
                    elif first_underscore != None and block[:first_underscore] in woods and block[first_underscore:first_underscore+5] != "_door" and block[first_underscore:first_underscore+9] != "_trapdoor":
                        block = '#0'+block[first_underscore:]

                block_string = block_string + block + " "
            block_string+="\n"
        block_string+="\n"
    print("finished downloading area")
    return block_string


class Facing(Enum):
    north = 0
    west = 1
    south = 2
    east = 3

class rFacing(Enum):
    south = 0
    east = 3
    north = 2
    west = 1


def download_schematic(origin_x, origin_y, origin_z, end_x, end_y, end_z, file_name, flexible_tiles=False, leave_dark_oak=True):
    file = open(file_name, "w")
    len_x = abs(origin_x - end_x) + 1
    len_y = abs(origin_y - end_y) + 1
    len_z = abs(origin_z - end_z) + 1
    file.write(str(len_x) + " " + str(len_y) + " " + str(len_z))
    file.write("\n")
    file.write(download_area(origin_x, origin_y, origin_z, end_x, end_y, end_z, flexible_tiles, leave_dark_oak))
    file.close()


### Place a pre-authored building. Takes dir arguments, which essentially orient the schematic placement
def place_schematic_in_world(file_name, origin_x, origin_y, origin_z, dir_x=1, dir_y=-1, dir_z=1, rot=0):
    size, blocks = get_schematic_parts(file_name)
    length_x, length_y, length_z = size

    sx = sz = ex = ez = 0
    end_x, end_y, end_z = origin_x + length_x, origin_y + length_y, origin_z + length_z
    sx = origin_x
    sz = origin_z
    ex = end_x
    ez = end_z

    length_x = int(length_x)
    length_y = int(length_y)
    length_z = int(length_z)

    end_x = origin_x + int(length_x) - 1
    end_y = origin_y + int(length_y) - 1
    end_z = origin_z + int(length_z) - 1
    origin_x, origin_y, origin_z, end_x, end_y, end_z = handle_dir(
        origin_x, origin_y, origin_z, end_x, end_y, end_z, dir_x, dir_y, dir_z
    )
    XI = 0
    YI = max(length_y - 1, 0)
    ZI = 0
    yi = YI
    i = 0
    for y in range(origin_y, end_y + 1, -dir_y):
        zi = ZI
        for z in range(origin_z, end_z + 1, dir_z):
            xi = XI
            for x in range(origin_x, end_x + 1, dir_x):
                index = yi * length_z * length_x + zi * length_x + xi
                block = "minecraft:" + blocks[index]
                block = adjust_property_by_rotation(block, property="facing=", longest_len=5, rot=rot, shortest_len=4,
                                                    rot_factor=1)
                if rot == 0:
                    http_framework.interfaceUtils.setBlock(sx + xi, y, sz + zi, block)
                if rot == 1:
                    http_framework.interfaceUtils.setBlock(sx + zi, y, sz + xi, block)
                if rot == 2:
                    http_framework.interfaceUtils.setBlock(ex - xi - 1, y, ez - zi - 1, block)
                if rot == 3:
                    http_framework.interfaceUtils.setBlock(ex - zi + 1, y, ez - xi - 3, block)  # this is a hack for now
                i += 1
                xi += 1
            zi += 1
        yi -= 1
    print(str(i) + " schematic blocks placed")
    print("done placing schematic")
    # size, blocks = get_schematic_parts(file_name)
    # length_x, length_y, length_z = size
    # length_x = int(length_x)
    # length_y = int(length_y)
    # length_z = int(length_z)
    # n_blocks = len(blocks)
    # end_x = origin_x + int(length_x) - 1
    # end_y = origin_y + int(length_y) - 1
    # end_z = origin_z + int(length_z) - 1
    # origin_x, origin_y, origin_z, end_x, end_y, end_z = handle_dir(
    #     origin_x, origin_y, origin_z, end_x, end_y, end_z, dir_x, dir_y, dir_z
    #     )
    #
    # XI = 0
    # YI = max(length_y-1, 0)
    # ZI = 0
    # yi = YI
    # for y in range(origin_y, end_y+1, -dir_y):
    #     zi = ZI
    #     for z in range(origin_z, end_z+1, dir_z):
    #         xi = XI
    #         for x in range(origin_x, end_x+1, dir_x):
    #             index =yi*length_z*length_x + zi*length_x + xi
    #             block = "minecraft:"+blocks[index]
    #             http_framework.interfaceUtils.placeBlockBatched(x, y, z, block, n_blocks)#, n_blocks-1)
    #             xi += 1
    #         zi += 1
    #     yi -= 1
    # print("done placing schematic")


def adjust_property_by_rotation(block, property, longest_len, rot, rot_factor=1, shortest_len=1, use_num=False):
    index = len(property)
    facing_i = block.find(property)
    if facing_i != -1:
        # get facing dir string
        curr_dir = None
        start_i = facing_i + index
        facing_substr = block[start_i:start_i + longest_len]  # len of "facing="
        print("facing substr is "+facing_substr)
        # find dir
        for dir in Facing:
            if dir.name in facing_substr:
                curr_dir = dir.value * rot_factor
        if curr_dir == None:  # is up or down
            return block
        # change direction based on dir
        # new_dir = Facing((curr_dir + rot) % 4)
        print("curr dir is "+str(curr_dir))
        new_dir = Facing((curr_dir + rot) % 4)
        if use_num:
            new_dir = str(new_dir.value* rot_factor)
        else:
            new_dir = new_dir.name
        # if  rot == 0:
        #     if new_dir == 'east': new_dir = 'west'
        #     elif new_dir == 'west': new_dir = 'east'
        if rot == 1 or rot == 3:
            if new_dir == 'north': new_dir = 'south'
            elif new_dir == 'south': new_dir = 'north'
        # string maniup to add new dir
        first, second_old = block.split(property)
        second_old = second_old[shortest_len:]
        # print("second old is "+str(block))
        # print("with "+str(second_old))
        if second_old[0] == "h":
            second_old = second_old[1:]
        new_second = property + new_dir + second_old
        block = first + new_second
    return block



## where the origin coords are the local coords within state
def place_schematic_in_state(state, file_name, origin_x, origin_y, origin_z, dir_x=1, dir_y=-1, dir_z=1, rot=0, flex_tile = None):
    size, blocks = get_schematic_parts(file_name)
    length_x, length_y, length_z = size

    sx = sz = ex = ez = 0
    end_x, end_y, end_z = origin_x+length_x, origin_y+length_y, origin_z+length_z
    sx = origin_x
    sz = origin_z
    ex = end_x
    ez = end_z
    if state.out_of_bounds_3D(origin_x, origin_y, origin_z) or state.out_of_bounds_3D(end_x, end_y, end_z):
        print("Tried to build out of bounds!")
        return False
    length_x = int(length_x)
    length_y = int(length_y)
    length_z = int(length_z)

    end_x = origin_x + int(length_x) - 1
    end_y = origin_y + int(length_y) - 1
    end_z = origin_z + int(length_z) - 1
    origin_x, origin_y, origin_z, end_x, end_y, end_z = handle_dir(
        origin_x, origin_y, origin_z, end_x, end_y, end_z, dir_x, dir_y, dir_z
    )
    XI = 0
    YI = max(length_y-1, 0)
    ZI = 0
    yi = YI
    i = 0
    for y in range(origin_y, end_y+1, -dir_y):
        zi = ZI
        for z in range(origin_z, end_z+1, dir_z):
            xi = XI
            for x in range(origin_x, end_x+1, dir_x):
                index = yi * length_z * length_x + zi * length_x + xi
                block = blocks[index]
                # check for flex tile
                if block[0] == '#':
                    print("before: " + str(block))
                    insert_pos = int(block[1])
                    block = block[2:2+insert_pos]+"birch"+block[2+insert_pos:]
                    print(block)
                    print("after: "+str(block))

                block = "minecraft:" + block
                block = adjust_property_by_rotation(block, property="facing=", longest_len=5, rot=rot, shortest_len=4, rot_factor=1)
                if rot == 0:
                    src.states.set_state_block(state, sx + xi, y, sz + zi, block)
                if rot == 1:
                    src.states.set_state_block(state, sx + zi, y, sz + xi, block)
                if rot == 2:
                    src.states.set_state_block(state, ex - xi - 1, y, ez - zi - 1, block)
                if rot == 3:
                    src.states.set_state_block(state, ex - zi + 2, y, ez - xi - 3, block)  # this is a hack for now
                i+=1
                xi += 1
            zi += 1
        yi -= 1
    print(str(i)+" schematic blocks placed")
    print("done placing schematic")


def get_schematic_parts(file_name):
    file = open(file_name)
    raw = file.readlines()

    size_str = raw[0]
    size_arr = [int(i) for i in size_str.split()]

    blocks_lines = raw[1:]
    blocks_str = ''
    for n in range(len(blocks_lines)):
        blocks_str += blocks_lines[n]
    blocks_arr = blocks_str.split()

    file.close()

    return size_arr, blocks_arr


def handle_dir(origin_x, origin_y, origin_z, end_x, end_y, end_z, dir_x, dir_y, dir_z):
    if dir_x == -1:
        origin_x, end_x = end_x, origin_x - 2
    if dir_y == 1:
        origin_y, end_y = end_y, origin_y - 2
    if dir_z == -1:
        origin_z, end_z = end_z, origin_z - 2
    return(origin_x, origin_y, origin_z, end_x, end_y, end_z)


def array_XYZ_to_schema(blocks, dx, dy, dz, file_out_name):
    out = open(file_out_name, "w")
    out.write(str(dx)+" "+str(dy)+" "+str(dz)+'\n')
    block_string = ''
    for y in range(dy):
        for z in range(dz):
            for x in range(dx):
                inv_y = dy - 1 - y
                block = blocks[x][inv_y][z].ljust(100, ' ')  # polished_blackstone_brick_stairs
                block_string = block_string + block + " "
            block_string+="\n"
        block_string+="\n"
    out.write(block_string)


def arrayXZ_to_schema(blocks, dx, dz, file_out_name):
    out = open(file_out_name, "w")
    out.write(str(dx)+" "+str(dz)+'\n')
    block_string = ''
    for x in range(dx):
        for z in range(dz):
            block = str(blocks[x][z]).ljust(100, ' ')  # polished_blackstone_brick_stairs
            block_string = block_string + block + " "
        block_string+="\n"
    out.write(block_string)


def download_heightmap(heightmap, file_name):
    f = open(file_name, "w")
    f.write(heightmap)
