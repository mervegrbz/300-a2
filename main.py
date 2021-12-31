from mpi4py import MPI
import math
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

P = size-1
N = 12

row_size = column_size = int(math.sqrt(P))

if rank == 0:  # manager
    game_map = [[{'type': '.', 'health': 0}
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
else:
    # you are a workerrr
    data = comm.recv(source=0, tag=0)
    row = data['row'] + 1
    column = data['column'] + 1
    part_map = data['part_map']

    # Horizontal
#    tek rowlar alt kenarlarını alttaki çifte versin, alttaki çiften kenar beklesin

    if row % 2 == 1:
        target = rank + row_size
        if (1 <= target <= P):

            comm.send(part_map[-1], dest=target, tag=2)
            print(f"S {rank} {target}")

            bottom_neighbour = comm.recv(source=target, tag=1)
        else:
            print("Invalid attempt")
    else:
        source = rank - row_size

        if (1 <= source <= P):
            print(f"W {rank} {source}")

            top_neighbour = comm.recv(source=source, tag=2)
            comm.send(part_map[0], dest=source, tag=1)
        else:
            print("Invalid attempt")

#    çift rowlar alt kenarlarını alttaki teke versin, alt rowdan kenar beklesin
    #
    if row % 2 == 0:
        target = rank + row_size
        if (1 <= target <= P):

            comm.send(part_map[-1], dest=target, tag=2)
            print(f"S {rank} {target}")

            bottom_neighbour = comm.recv(source=target, tag=1)
        else:
            print("Invalid attempt")
    else:
        source = rank - row_size

        if (1 <= source <= P):
            print(f"W {rank} {source}")

            top_neighbour = comm.recv(source=source, tag=2)
            comm.send(part_map[0], dest=source, tag=1)
        else:
            print("Invalid attempt")

    if column % 2 == 1:
        target = rank + column_size
        if (1 <= target <= P):

            comm.send([x[-1] for x in part_map], dest=target, tag=2)
            print(f"S {rank} {target}")

            right_neighbour = comm.recv(source=target, tag=1)
        else:
            print("Invalid attempt")
    else:
        source = rank - column_size

        if (1 <= source <= P):
            print(f"W {rank} {source}")

            left_neighbour = comm.recv(source=source, tag=2)
            comm.send([x[0] for x in part_map], dest=source, tag=1)
        else:
            print("Invalid attempt")


    if column % 2 == 0:
        target = rank + column_size
        if (1 <= target <= P):

            comm.send([x[-1] for x in part_map], dest=target, tag=2)
            print(f"S {rank} {target}")

            right_neighbour = comm.recv(source=target, tag=1)
        else:
            print("Invalid attempt")
    else:
        source = rank - column_size

        if (1 <= source <= P):
            print(f"W {rank} {source}")

            left_neighbour = comm.recv(source=source, tag=2)
            comm.send([x[0] for x in part_map], dest=source, tag=1)
        else:
            print("Invalid attempt")