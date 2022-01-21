# Code runs successfully on all test cases

from mpi4py import MPI
from sys import argv
import math
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

P = size-1
row_size = column_size = int(math.sqrt(P))


def find_myself(column, row, sqrt_cell):
    return (row//sqrt_cell)*row_size+(column//sqrt_cell+1)


if rank == 0:  # manager
    filename = argv[1]
    with open(filename) as f:
        N, wave, c = [int(x) for x in f.readline().split()]
        future_towers = f.readlines()
        f.close()

    number_of_cells_per_worker = N ** 2 / P
    sqrt_cell = int(math.sqrt(number_of_cells_per_worker))
    game_map = [[{"row": x, "col": y, "type": ".", "health": 0}
                 for y in range(N)]for x in range(N)]

    sqrt_p = int(math.sqrt(P))
    for i in range(1, P+1):
        row = (i-1) // sqrt_p
        column = (i-1) % sqrt_p
        part_map = [[column for column in row[column * sqrt_cell:(
            column+1)*sqrt_cell]] for row in game_map[row * sqrt_cell:(row+1)*sqrt_cell]]
        comm.send({"row": row, "column": column, "wave": wave,
                  "part_map": part_map}, dest=i, tag=0)

    o_s = [[] for i in range(wave)]
    plus_s = [[] for i in range(wave)]

    for x in range(0, wave):
        l = future_towers[2*x].split(", ")
        for tower_position in l:
            position = tower_position.split(" ")
            row = int(position[0])
            col = int(position[1])
            o_s[x].append({"health": 6, 'type': 'o', 'row': row, 'col': col})

        l = future_towers[2*x+1].split(", ")
        for tower_position in l:
            position = tower_position.split(" ")
            row = int(position[0])
            col = int(position[1])
            plus_s[x].append(
                {"health": 8, 'type': '+', 'row': row, 'col': col})

    for i in range(wave):
        wave_count = i
        process_towers = [[] for x in range(size)]
        o_tower = o_s[i]
        plus_towers = plus_s[i]

        for o in o_tower:
            process_towers[find_myself(
                o["col"], o["row"], sqrt_cell)-1].append(o)
        for plus in plus_towers:
            process_towers[find_myself(
                plus["col"], plus["row"], sqrt_cell)-1].append(plus)
        for ad1 in range(1, P+1):
            comm.send(process_towers[ad1-1], dest=ad1, tag=22)

    final_maps = {}
    for j in range(1, P+1):  # get maps from workers at the end of the game
        final_maps[j-1] = comm.recv(source=j, tag=100)

    game_map_final = [[{} for y in range(N)] for x in range(N)]
    for r in range(sqrt_p):
        for c in range(sqrt_p):
            p = r * row_size + c
            for a in range(sqrt_cell):
                for t in final_maps[p][a]:
                    r_1 = t['row']
                    c_1 = t['col']
                    game_map_final[r_1][c_1] = t['type']

    print("\n".join([" ".join(game_map_final[x]) for x in range(N)]), end="")


else:
    data = comm.recv(source=0, tag=0)
    row = data["row"] + 1
    column = data["column"] + 1
    wave = data["wave"]
    part_map = data["part_map"]
    sqrt_cell = len(part_map[0])
    N = sqrt_cell*(P**(1/2))

    for i in range(wave):
        # start of wave
        myself_towers = comm.recv(source=0, tag=22)
        for tower in myself_towers:
            if part_map[tower["row"] % sqrt_cell][tower["col"] % sqrt_cell]["type"] == ".":
                part_map[tower["row"] %
                         sqrt_cell][tower["col"] % sqrt_cell] = tower

        for i in range(8):
            # start of round
            top_neighbour = None
            bottom_neighbour = None
            left_neighbour = None
            right_neighbour = None

            # Horizontal
            #   odd rows send bottom side to below even and wait response from it
            if row % 2 == 1:
                target = rank + row_size
                if (1 <= target <= P):  # check if it is in boundries
                    comm.send(part_map[-1], dest=target, tag=2)
                    bottom_neighbour = comm.recv(source=target, tag=1)
            else:
                source = rank - row_size
                if (1 <= source <= P):
                    top_neighbour = comm.recv(source=source, tag=2)
                    comm.send(part_map[0], dest=source, tag=1)

            #   even rows send bottom side to below odd and wait response from it
            if row % 2 == 0:
                target = rank + row_size
                if (1 <= target <= P):
                    comm.send(part_map[-1], dest=target, tag=2)
                    bottom_neighbour = comm.recv(source=target, tag=1)
            else:
                source = rank - row_size
                if (1 <= source <= P):
                    top_neighbour = comm.recv(source=source, tag=2)
                    comm.send(part_map[0], dest=source, tag=1)

            # We are transfering cross spots in two steps.
            # While communicating horizontally, left and right sides send their top and bottom neighbours, if any, too.
            # That's why we are using data_transfer_object to temporarly store those 2nd level neighbours
            data_transfer_object = {}

            # odd columns send their right sides to right and wait response from it
            if column % 2 == 1:
                target = rank + 1
                if (rank % column_size != 0 and 1 <= target <= P):

                    if top_neighbour != None:  # I have a top neighbour and i should send it to my right
                        data_transfer_object["top_neighbour"] = top_neighbour[-1]
                    if bottom_neighbour != None:  # I have a bottom neighbour and i should send it to my right
                        data_transfer_object["bottom_neighbour"] = bottom_neighbour[-1]
                    data_transfer_object["me"] = [x[-1]
                                                  for x in part_map]  # my right side

                    comm.send(data_transfer_object, dest=target, tag=2)
                    right_neighbour = comm.recv(source=target, tag=1)

            else:
                source = rank - 1
                if (rank % column_size != 1 and 1 <= source <= P):
                    left_neighbour = comm.recv(source=source, tag=2)
                    if top_neighbour != None:
                        data_transfer_object["top_neighbour"] = top_neighbour[0]
                    if bottom_neighbour != None:
                        data_transfer_object["bottom_neighbour"] = bottom_neighbour[0]
                    data_transfer_object["me"] = [x[0] for x in part_map]
                    comm.send(data_transfer_object, dest=source, tag=1)

            data_transfer_object = {}

            # even columns send their right sides to right and wait response from it
            if column % 2 == 0:
                target = rank + 1
                if (rank % column_size != 0 and 1 <= target <= P):
                    if top_neighbour != None:
                        data_transfer_object["top_neighbour"] = top_neighbour[-1]
                    if bottom_neighbour != None:
                        data_transfer_object["bottom_neighbour"] = bottom_neighbour[-1]
                    data_transfer_object["me"] = [x[-1] for x in part_map]
                    comm.send(data_transfer_object, dest=target, tag=2)
                    right_neighbour = comm.recv(source=target, tag=1)

            else:
                source = rank - 1
                if (rank % column_size != 1 and 1 <= source <= P):
                    left_neighbour = comm.recv(source=source, tag=2)
                    if top_neighbour != None:
                        data_transfer_object["top_neighbour"] = top_neighbour[0]
                    if bottom_neighbour != None:
                        data_transfer_object["bottom_neighbour"] = bottom_neighbour[0]
                    data_transfer_object["me"] = [x[0] for x in part_map]
                    comm.send(data_transfer_object, dest=source, tag=1)

            size = int(N / math.sqrt(P))
            area = [[{"type": "."} for y in range(size + 2)]
                    for i in range(size + 2)]  # 5x5

            for i in range(size):
                area[i+1][1:-1] = part_map[i]
            if top_neighbour != None:
                area[0][1:-1] = top_neighbour
            if bottom_neighbour != None:
                area[-1][1:-1] = bottom_neighbour
            if left_neighbour != None:
                for x in range(size):
                    area[x+1][0] = left_neighbour["me"][x]
                if "bottom_neighbour" in left_neighbour:
                    area[-1][0] = left_neighbour["bottom_neighbour"]
                if "top_neighbour" in left_neighbour:
                    area[0][0] = left_neighbour["top_neighbour"]
            if right_neighbour != None:
                for x in range(size):
                    area[x+1][-1] = right_neighbour["me"][x]
                if "bottom_neighbour" in right_neighbour:
                    area[-1][-1] = right_neighbour["bottom_neighbour"]
                if "top_neighbour" in right_neighbour:
                    area[0][-1] = right_neighbour["top_neighbour"]

            # Attack
            attacks = [[0 for x in range(size+2)] for y in range(size+2)]
            for row in range(1, size+1):
                for column in range(1, size+1):
                    tower = area[row][column]
                    how_much_touched_me_count = 0
                    if tower["type"] == ".":
                        continue
                    elif tower["type"] == "+":
                        nominees = [
                            area[row+1][column+1],
                            area[row+1][column],
                            area[row-1][column],
                            area[row][column+1],
                            area[row-1][column+1],
                            area[row][column-1],
                            area[row+1][column-1],
                            area[row-1][column-1]]
                        how_much_touched_me_count += len(
                            list(filter(lambda x: x["type"] == "o", nominees)))  # select "o" towers from nominees
                    elif tower["type"] == "o":
                        nominees = [
                            area[row][column+1],
                            area[row][column-1],
                            area[row+1][column],
                            area[row-1][column]]
                        attackers = list(
                            filter(lambda x: x["type"] == "+", nominees))
                        how_much_touched_me_count += 2*len(attackers)

                    attacks[row][column] = how_much_touched_me_count

            for row in range(1, size+1):
                for column in range(1, size+1):
                    # deduce hitpoints
                    area[row][column]["health"] -= attacks[row][column]
                    # remove + and o towers if they are dead
                    if area[row][column]["health"] <= 0:
                        area[row][column]["type"] = "."
                        area[row][column]['health'] = 0

            # update part map for the next round
            part_map = [x[1:-1] for x in area[1:-1]]
            # end of round
        # end of wave
    comm.send(part_map, dest=0, tag=100)  # to print end of wave
