from mpi4py import MPI
import math
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

P = size-1
N = 12

row_size = column_size = int(math.sqrt(P))

if rank == 0:  # manager
    game_map = [[{'cellIndex': (x)*N+y+1, 'host': (x//3)*column_size+(y//3+1)}
                 for y in range(N)]for x in range(N)]
    # some random values
    game_map[0][1]['type'] = 'o'
    game_map[2][3]['type'] = '+'
    game_map[0][3]['type'] = 'o'
    number_of_cells_per_worker = N ** 2 / P
    sqrt_cell = int(math.sqrt(number_of_cells_per_worker))
    sqrt_p = int(math.sqrt(P))
    for i in range(1, P+1):
        row = (i-1) // 4
        column = (i-1) % 4
        part_map = [[column for column in row[column * sqrt_cell:(
            column+1)*sqrt_cell]] for row in game_map[row * sqrt_cell:(row+1)*sqrt_cell]]
        comm.send({"row": row, "column": column,
                  "part_map": part_map}, dest=i, tag=0)
    wave = 2
    for i in range(wave):
        o_s = [{"row":3,"col": 0,"type":'o'},{"row":0,"col": 0,"type":'o'},{"row":0,"col": 2,"type":'o'},{"row":1,"col": 0,"type":'o'}]
        plus_s = [{"row":3,"col": 3,"type":'+'},{"row":0,"col": 3,"type":'+'},{"row":0,"col": 3,"type":'+'},{"row":1,"col": 3,"type":'+'}]
        # BURADAYYIZZZZ
else:
    # print(f"{rank=}")
    # you are a workerrr
    data = comm.recv(source=0, tag=0)
    row = data['row'] + 1
    column = data['column'] + 1
    part_map = data['part_map']

    # start of wave

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
                    data_transfer_object['top_neighbour'] = top_neighbour[-1]
                if bottom_neighbour != None:
                    data_transfer_object['bottom_neighbour'] = bottom_neighbour[-1]
                data_transfer_object['me'] = [x[-1] for x in part_map]

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
                    data_transfer_object['top_neighbour'] = top_neighbour[0]
                if bottom_neighbour != None:
                    data_transfer_object['bottom_neighbour'] = bottom_neighbour[0]
                data_transfer_object['me'] = [x[0] for x in part_map]
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
                    data_transfer_object['top_neighbour'] = top_neighbour[-1]
                if bottom_neighbour != None:
                    data_transfer_object['bottom_neighbour'] = bottom_neighbour[-1]
                data_transfer_object['me'] = [x[-1] for x in part_map]

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
                    data_transfer_object['top_neighbour'] = top_neighbour[0]
                if bottom_neighbour != None:
                    data_transfer_object['bottom_neighbour'] = bottom_neighbour[0]
                data_transfer_object['me'] = [x[0] for x in part_map]
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
        area = [[None for y in range(size + 2)] for i in range(size + 2)]  # 5x5
        # area[1:-1][1:-1] = part_map
        for i in range(size):
            area[i+1][1:-1] = part_map[i]
        if top_neighbour != None:
            area[0][1:-1] = top_neighbour
        if bottom_neighbour != None:
            area[-1][1:-1] = bottom_neighbour
        if left_neighbour != None:
            for x in range(size):
                area[x+1][0] = left_neighbour['me'][x]
            if 'bottom_neighbour' in left_neighbour:
                area[-1][0] = left_neighbour['bottom_neighbour']
            if 'top_neighbour' in left_neighbour:
                area[0][0] = left_neighbour['top_neighbour']
        if right_neighbour != None:
            for x in range(size):
                area[x+1][-1] = right_neighbour['me'][x]
            if 'bottom_neighbour' in right_neighbour:
                area[-1][-1] = right_neighbour['bottom_neighbour']
            if 'top_neighbour' in right_neighbour:
                area[0][-1] = right_neighbour['top_neighbour']

        print(f"""I am {rank=}. {area=}""")

        # attaaaccck

        for row in range(1, size+1):
            for column in range(1, size+1):
                tower = area[row][column]
                how_much_touched_my_ass_count = 0
                if tower['type'] == '.':
                    continue
                elif tower['type'] == '+':
                    nominees = [
                        area[row][column+1],
                        area[row][column-1],
                        area[row+1][column],
                        area[row-1][column]]
                    how_much_touched_my_ass_count += len(
                        filter(lambda x: x['type'] == 'o'), nominees)

                elif tower['type'] == 'o':
                    nominees = [
                        area[row+1][column+1],
                        area[row+1][column],
                        area[row-1][column],
                        area[row][column+1],
                        area[row-1][column+1],
                        area[row][column-1],
                        area[row+1][column-1],
                        area[row-1][column-1]]
                    how_much_touched_my_ass_count += 2 * len(
                        filter(lambda x: x['type'] == '+'), nominees)

                area[row][column]['health'] -= how_much_touched_my_ass_count
                if area[row][column]['health'] <= 0: area[row][column]['type'] = '.'
        part_map=area[1:-1][1:-1]
        # end of round

    # end of wave
    # get new towers from manager
    new_towers = comm.recv(source=0, tag=23)