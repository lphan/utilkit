import sys
# print(sys.getrecursionlimit())

# position of stones
stone = {'L': (6, 1), 'A': (3, 2), 'I': (6, 5), 'O': (1, 3), 'S': (0, 1)}
st = list(stone.values())

# init path
path = []
tmp = []

# init obstacles
obstacle = [(0, 6), (2, 1), (3, 0), (4, 2), (5, 6), (6, 0)]


def weight(s1, s2):
    return abs(s1[0]-s2[0]) + abs(s1[1]-s2[1])


def shortest_path(start):
    dist = [(weight(start, s), s) for s in st]
    return min(dist)


def invalid(x, y):
    # (x, y) is out of bound
    if (x < 0) or (x > 7) or (y < 0) or (y > 7):
        print("Out of bound")
        return True

    # (x, y) is already visited
    if (x, y) in obstacle:
        print("Already visited")
        return True

    return False


def goto(x, y):
    # set starting point to choose direction
    start = (x, y)
    print("Starting point: ", start)

    if invalid(x, y):
        return

    if start in st:
        print("..... Found STONE at ....", start)
        print("current path: ", path)

        # remove the already found stone from list_stone
        st.remove(start)
        print("list of stones after found: ", st)
    else:
        print("list of stones: ", st)

    # found all stones in path
    if set(stone.values()).issubset(set(path)) or not st:
        print("..... All STONES found, exit")
        print(path)
        # save the last position where the stone is found
        tmp.append(start)
        return

    # (x, y) in position surrounded by 4 obstacles
    elif (x + 1, y) in obstacle and (x - 1, y) in obstacle and (x, y - 1) in obstacle and (x, y + 1) in obstacle:
        print("Surrounded by 4 obstacles")
        if (x, y) in stone.values():
            print("..... Found STONE at ....", (x, y))
            path.append((x, y))
            obstacle.append((x, y))
            return
        else:
            obstacle.append((x, y))
            return
    else:
        path.append((x, y))
        obstacle.append((x, y))

    # find shortest path from starting point s(x,y)
    sp = shortest_path(start)[1]
    print("Shortest path is the next target: ", sp)

    if start[0] == sp[0] and start[1] > sp[1]:
        print("--> go down")
        goto(x, y - 1)
        print("--> go up")
        goto(x, y + 1)
        print("--> go left")
        goto(x - 1, y)
        print("--> go right")
        goto(x + 1, y)

    elif start[0] == sp[0] and start[1] < sp[1]:
        # go up
        print("--> go up")
        goto(x, y + 1)
        print("--> go down")
        goto(x, y - 1)
        print("--> go left")
        goto(x - 1, y)
        print("--> go right")
        goto(x + 1, y)

    elif start[1] == sp[1] and start[0] > sp[0]:
        # go left
        print("--> go left")
        goto(x - 1, y)
        print("--> go right")
        goto(x + 1, y)
        print("--> go up")
        goto(x, y + 1)
        print("--> go down")
        goto(x, y - 1)

    # elif start[1] == sp[1] and start[0] < sp[0]:
    else:
        # go right
        print("--> go right")
        goto(x + 1, y)
        print("--> go left")
        goto(x - 1, y)
        print("--> go up")
        goto(x, y + 1)
        print("--> go down")
        goto(x, y - 1)


print("list of stone before start: ", st)
goto(3, 1)
print("---------------------- ")
print("RESULT: \n")
print('tmp:', tmp)
# append the first item to the final path and drop all other redundant items because of running recursion
path.append(tmp[0])
print(path)
print(len(path))
print("list of stone after all: ", st)
