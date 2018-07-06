import sys
# print(sys.getrecursionlimit())

# position of stones
stone = {'L':(1, 5), 'A':(0, 3), 'I':(2, 2), 'O':(5, 2), 'S':(0, 4)}
st = list(stone.values())

# init path & result
path = []
result = []

# init obstacles
obstacle = [(0, 2), (1, 3), (2, 4), (3, 5), (4, 4), (6, 4)]


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
        for k in list(stone.keys()):
            if stone.get(k) == start:
                result.append(k)
                print("..... Found STONE at ....", k," ",start)
        print("current path: ", path)

        # remove the already found stone from list_stone
        st.remove(start)
        print("list of stones after found: ", st)
    else:
        print("list of stones: ", st)
        # pass

    path.append(start)
    obstacle.append(start)
    
    goto(x+1, y)  # R
    goto(x, y+1)  # D
    goto(x-1, y)  # L    
    goto(x, y-1)  # U             


print("Stone_list before goto: ", st)
goto(1, 0)
print("---------------------- ")
print("RESULT: \n")  # Result: LSAOI  

# append the first item to the final path and drop all other redundant items because of running recursion
print(path)
print(len(path))
print("Stone_list after goto: ", st)
print("The order of collected items: ", result)
