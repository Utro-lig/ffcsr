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
        correct_state = True
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

# Avoid loading tables all at once
table_lock = mp.Lock()

def find_solutions(z, ffcsr, r):
    TABLE = [[] for i in range(8)]
    with table_lock:
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
            return True
    return False

class Worker():
    def __init__(self):
        self.pool = mp.Pool()
        bytedump = open(DUMP_PATH + "dump", "rb")
        self.z = bytedump.read()
        bytedump.close()
        self.ffcsr = ffcsrh.F_FCSR_H(0, 0)

    def callback(self, result):
        if result:
            # Result is True so we're done
            self.pool.terminate()

    def do_job(self):
        size_of_dump = len(self.z)
        sub_size = size_of_dump // mp.cpu_count()
        for i in range(0, size_of_dump, sub_size):
            self.pool.apply_async(find_solutions, [self.z, self.ffcsr, range(i, i + sub_size)])
        self.pool.close()
        self.pool.join()

def main():
    """
    Main function
    """
    worker = Worker()
    worker.do_job()
    
if __name__ == "__main__":
    main()
