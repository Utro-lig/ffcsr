import ffcsrh
import pickle
import multiprocessing as mp

DUMP_PATH = "./"
TABLES_PATH = "./"

def try_paths(ffcsr, t, z, M, P=[0]*8, depth=0):
    """
    Tests every solution given by Mi matrices
    """
    if depth >= len(M):
        state = 0
        for i in range(8):
            state = state | P[i]
        ffcsr.set_state(state)
        ffcsr.set_carry(0b10)
        for i in range(22):
            if z[t + i] != ffcsr.filter_function():
                return None
            ffcsr.clock()
        return state
    else:
        for i in range(len(M[depth])):
            P[depth] = M[depth][i]
            result = try_paths(ffcsr, t, z, M, P, depth + 1)
            if result != None:
                return result
        return None

def test_solutions(ffcsr, t, z, M):
    """
    Wrapper for our recursive function
    """
    return try_paths(ffcsr, t, z, M) 

def load_table(name):
    fp = open(name, 'rb')
    table = pickle.load(fp)
    fp.close()

    return table

def find_solutions(found, z, ffcsr, r):
    """
    Note: The way tables are loaded is currently really bad
    When there are too many cores, multiprocessing too much
    becomes less effecient because of the intial overhead
    TODO: Find a way to load the tables only once and run
    the workers on these unique copies
    """
    TABLE = [[] for i in range(8)]
    for i in range(8):
        TABLE[i] = load_table(TABLES_PATH + "TABLE{}".format(i))
    print("Now searching between {} and {} ...".format(r.start, r.stop))
    for t in r:
        nb_solved = 0
        W = [0] * 8
        M = [[] for i in range(8)]
        # Computing Wi's
        for i in range(8):
            for k in range(20):
                bit_index = (i - k) % 8
                W[i] = W[i] | (((z[t + k] & (1 << bit_index)) >> bit_index) << (19 - k))

            # Try to solve the associated system of equations
            M[i] = TABLE[i][W[i]]
            if len(M[i]) > 0:
                nb_solved += 1
            else:
                break

        if nb_solved == 8:
            # We found something interesting
            state = test_solutions(ffcsr, t, z, M)
            if state == None:
                continue
            # Master has presented Dobby with a solution
            # Dobby is free \o/
            print("\nA solution has been found:")
            print("M({}) = {}".format(t, hex(state)))
            q = 0x15d30bbfe4cc33f8b0c47b9155e8dab207ba84a9b
            # p(t) = M + 2*C
            pt = state + 4
            # p(0) = p(t) * 2^t mod q
            p0 = (pt * (2**(t+163))) % q
            print("M(0) = {}".format(hex(p0)))
            found.set()
            return True
    return False

def main():
    """
    Main function
    """
    pool = mp.Pool()
    bytedump = open(DUMP_PATH + "dump", "rb")
    z = bytedump.read()
    bytedump.close()

    ffcsr = ffcsrh.F_FCSR_H(0, 0)
    manager = mp.Manager()
    found_solution = manager.Event()
    size_of_dump = len(z)

    sub_size = size_of_dump // mp.cpu_count()
    for i in range(0, size_of_dump, sub_size):
        pool.apply_async(find_solutions, [found_solution, z, ffcsr, range(i, i + sub_size)])

    pool.close()
    found_solution.wait()
    pool.terminate()

    
if __name__ == "__main__":
    main()
