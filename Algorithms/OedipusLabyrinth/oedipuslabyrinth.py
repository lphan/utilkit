import sys
# print(sys.getrecursionlimit())

# position of stones
stone = {'L':(4, 1), 'A':(2, 6), 'I':(6, 1), 'O':(2, 4), 'S':(1, 6)}
st = list(stone.values())

# init path
path = []

# init obstacles
obstacle = [(0, 1), (1, 0), (1, 3), (2, 1), (3, 3), (5, 6)]


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

    path.append(start)
    obstacle.append(start)

    goto(x+1, y)
    goto(x, y+1)
    goto(x-1, y)
    goto(x, y-1)


print("Stone_list before goto: ", st)
goto(6, 2)
print("---------------------- ")
print("RESULT: \n")

# append the first item to the final path and drop all other redundant items because of running recursion
print(path)
print(len(path))
print("Stone_list after goto: ", st)
