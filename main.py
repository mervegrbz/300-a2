from mpi4py import MPI
import math
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

P = size-1
row_size = column_size = int(math.sqrt(P))


def find_myself(column, row, sqrt_cell):
    return (row//sqrt_cell)*row_size+(column//sqrt_cell+1)


if rank == 0:  # manager
    with open("input-output/input5.txt") as f:
        N, wave, c = [int(x) for x in f.readline().split()]
        future_towers = f.readlines()

        f.close()
    number_of_cells_per_worker = N ** 2 / P
    sqrt_cell = int(math.sqrt(number_of_cells_per_worker))
    game_map = [[{"row": x, "col": y, "cellIndex": (x)*N+y+1, "type": ".", "health": 0, "host": (x//sqrt_cell)*column_size+(y//sqrt_cell+1)}
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
        # add health of towers got can
        process_towers = [[] for x in range(size)]
        o_tower = o_s[i]
        plus_towers = plus_s[i]

        for o in o_tower:
            process_towers[find_myself(
                o["col"], o["row"], sqrt_cell)-1].append(o)
        for plus in plus_towers:
            process_towers[find_myself(
                plus["col"], plus["row"], sqrt_cell)-1].append(plus)
        # print(process_towers)
        for ad1 in range(1, P+1):
            comm.send(process_towers[ad1-1], dest=ad1, tag=22)
    final_maps = {}
    for ad2 in range(1, P+1):
        final_maps[ad2-1] = comm.recv(source=ad2, tag=100)
    # print(f"{final_maps=}")

    # print(f"wave {wave_count+1} basi:")
    game_map_final = [[{} for y in range(N)] for x in range(N)]
    for r in range(sqrt_p):  # 0 1 2 3
        for c in range(sqrt_p):  # 0 1 2 3
            p = r * row_size + c
            # print(f"{p=} {r=} {c=} ")
            for a in range(sqrt_cell):  # 0 1 2
                for t in final_maps[p][a]:
                    # print(t['type'], end=" ")
                    r_1 = t['row']
                    c_1 = t['col']
                    game_map_final[r_1][c_1] = t['type']

    # for x in range(N):
    #     print(" ".join(game_map_final[x]),end="")
    print("\n".join([" ".join(game_map_final[x])for x in range(N)]),end="")
        # for asd in range(8):
        #     print(f"end of round {asd}")
        #     for i in range(1, P+1):
        #         final_maps[i-1] = comm.recv(source=i, tag=100)
        #     game_map_final = [[{} for y in range(N)] for x in range(N)]
        #     for r in range(sqrt_p):  # 0 1 2 3
        #         for c in range(sqrt_p):  # 0 1 2 3
        #             p = r * row_size + c
        #             # print(f"{p=} {r=} {c=} ")
        #             for a in range(sqrt_cell):  # 0 1 2
        #                 for t in final_maps[p][a]:
        #                     # print(t['type'], end=" ")
        #                     r_1 = t['row']
        #                     c_1 = t['col']
        #                     game_map_final[r_1][c_1] = f"{t['type']}"

        #     for x in range(N):
        #         for y in range(N):
        #             print(game_map_final[x][y], end=" ")
        #         print()


else:
    # print(f"{rank=}")
    # you are a workerrr
    data = comm.recv(source=0, tag=0)
    row = data["row"] + 1
    wave = data["wave"]
    column = data["column"] + 1
    part_map = data["part_map"]
    sqrt_cell = len(part_map[0])
    N = sqrt_cell*size**(1/2)

    for i in range(wave):
        myself_towers = comm.recv(source=0, tag=22)
        for tower in myself_towers:
            if part_map[tower["row"] % sqrt_cell][tower["col"] % sqrt_cell]["type"] == ".":
                part_map[tower["row"] %
                         sqrt_cell][tower["col"] % sqrt_cell] = tower

        # start of wave
        # comm.send(part_map, dest=0, tag=100)  # to print first wave

        for i in range(8):
            # start of round
            top_neighbour = None
            bottom_neighbour = None
            left_neighbour = None
            right_neighbour = None
            # Horizontal
        #    tek rowlar alt kenarlarını alttaki çifte versin, alttaki çiften kenar beklesin

            if row % 2 == 1:
                target = rank + row_size
                if (1 <= target <= P):

                    comm.send(part_map[-1], dest=target, tag=2)
                    # print(f"S {rank} {target}")

                    bottom_neighbour = comm.recv(source=target, tag=1)
                else:
                    # print("Invalid attempt")
                    pass
            else:
                source = rank - row_size

                if (1 <= source <= P):
                    # print(f"W {rank} {source}")

                    top_neighbour = comm.recv(source=source, tag=2)
                    comm.send(part_map[0], dest=source, tag=1)
                else:
                    # print("Invalid attempt")
                    pass

        #    çift rowlar alt kenarlarını alttaki teke versin, alt rowdan kenar beklesin
            #
            if row % 2 == 0:
                target = rank + row_size
                if (1 <= target <= P):

                    comm.send(part_map[-1], dest=target, tag=2)
                    # print(f"S {rank} {target}")

                    bottom_neighbour = comm.recv(source=target, tag=1)
                else:
                    # print("Invalid attempt")
                    pass
            else:
                source = rank - row_size

                if (1 <= source <= P):
                    # print(f"W {rank} {source}")

                    top_neighbour = comm.recv(source=source, tag=2)
                    comm.send(part_map[0], dest=source, tag=1)
                else:
                    # print("Invalid attempt")
                    pass

        #    tek columnlar sag kenarlarını sagdaki çifte versin, sagdaki çiften kenar beklesin
            data_transfer_object = {}

            if column % 2 == 1:
                target = rank + 1
                if (rank % column_size != 0 and 1 <= target <= P):

                    # operation a
                    # print(f"S {rank} {target}")
                    if top_neighbour != None:
                        data_transfer_object["top_neighbour"] = top_neighbour[-1]
                    if bottom_neighbour != None:
                        data_transfer_object["bottom_neighbour"] = bottom_neighbour[-1]
                    data_transfer_object["me"] = [x[-1] for x in part_map]

                    comm.send(data_transfer_object, dest=target, tag=2)
                    right_neighbour = comm.recv(source=target, tag=1)
                else:
                    # print("Invalid attempt")
                    pass
            else:
                source = rank - 1

                if (rank % column_size != 1 and 1 <= source <= P):
                    # print(f"W {rank} {source}")
                    #  operation b
                    left_neighbour = comm.recv(source=source, tag=2)
                    if top_neighbour != None:
                        data_transfer_object["top_neighbour"] = top_neighbour[0]
                    if bottom_neighbour != None:
                        data_transfer_object["bottom_neighbour"] = bottom_neighbour[0]
                    data_transfer_object["me"] = [x[0] for x in part_map]
                    comm.send(data_transfer_object, dest=source, tag=1)
                else:
                    # print("Invalid attempt")
                    pass

        #    çift columnlar sag kenarlarını sagtaki teke versin, sag rowdan kenar beklesin
            data_transfer_object = {}

            if column % 2 == 0:
                target = rank + 1
                if (rank % column_size != 0 and 1 <= target <= P):

                    # operation a
                    # print(f"S {rank} {target}")
                    if top_neighbour != None:
                        data_transfer_object["top_neighbour"] = top_neighbour[-1]
                    if bottom_neighbour != None:
                        data_transfer_object["bottom_neighbour"] = bottom_neighbour[-1]
                    data_transfer_object["me"] = [x[-1] for x in part_map]

                    comm.send(data_transfer_object, dest=target, tag=2)
                    right_neighbour = comm.recv(source=target, tag=1)
                else:
                    # print("Invalid attempt")
                    pass
            else:
                source = rank - 1

                if (rank % column_size != 1 and 1 <= source <= P):
                    # print(f"W {rank} {source}")
                    #  operation b
                    left_neighbour = comm.recv(source=source, tag=2)
                    if top_neighbour != None:
                        data_transfer_object["top_neighbour"] = top_neighbour[0]
                    if bottom_neighbour != None:
                        data_transfer_object["bottom_neighbour"] = bottom_neighbour[0]
                    data_transfer_object["me"] = [x[0] for x in part_map]
                    comm.send(data_transfer_object, dest=source, tag=1)
                else:
                    # print("Invalid attempt")
                    pass

            # print(f"""I am {rank=}. I have :"/
            # \n\n top\n{top_neighbour}\n\n/
            # \n\n bottom\n{bottom_neighbour}\n\n/
            # \n\n left\n{left_neighbour}\n\n/
            # \n\n right\n{right_neighbour}\n\n""")

            size = int(N / math.sqrt(P))
            area = [[{"type": "."} for y in range(size + 2)]
                    for i in range(size + 2)]  # 5x5
            # area[1:-1][1:-1] = part_map
            # print(len(part_map))
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

            # print(f"""I am {rank=}. {area=}""")

            # attaaaccck
            attacks = [[0 for x in range(size+2)] for y in range(size+2)]
            for row in range(1, size+1):
                for column in range(1, size+1):
                    tower = area[row][column]
                    how_much_touched_my_ass_count = 0
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
                        how_much_touched_my_ass_count += len(
                            list(filter(lambda x: x["type"] == "o", nominees)))
                    elif tower["type"] == "o":
                        nominees = [
                            area[row][column+1],
                            area[row][column-1],
                            area[row+1][column],
                            area[row-1][column]]
                        attackers = list(
                            filter(lambda x: x["type"] == "+", nominees))
                        how_much_touched_my_ass_count += 2*len(attackers)
                        # print(
                        #     f"{area[row][column]} took damage from {attackers=} {nominees=}")
                    attacks[row][column] = how_much_touched_my_ass_count

            for row in range(1, size+1):
                for column in range(1, size+1):
                    area[row][column]["health"] -= attacks[row][column]
                    if area[row][column]["health"] <= 0:
                        area[row][column]["type"] = "."
                        area[row][column]['health'] = 0
            part_map = [x[1:-1] for x in area[1:-1]]
    comm.send(part_map, dest=0, tag=100)  # to print end of round

            # end of round

        # end of wave
    # get new towers from manager
