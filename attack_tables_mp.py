import ffcsrh
import cProfile
import pickle
import multiprocessing as mp

def bin_to_array(number):
    """ Number -> Binary representation """
    array = [0] * 20
    for i in range(20):
        array[19-i] = number & 1
        number = number >> 1
    return array

def bin_to_vec(number):
    """ Number -> Element of vector space over F2 """
    VS = VectorSpace(GF(2), 20)
    return VS(bin_to_array(number))

def vec_to_bin(v):
    result= 0
    for i in range(20):
        result = result | (v[19 - i] << i)
    return result

def rebuild_state(M):
    """
    Converts Mi matrices to an integer representation of the main register
    """
    result = 0
    for i in range(8):
        result = result | M[i]
    return result

def try_paths(ffcsr, t, z, M, P=[0]*8, depth=0):
    """
    Tests every solution given by Mi matrices
    """
    if depth >= len(M):
        state = rebuild_state(P)
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

def find_solutions(z, ffcsr, r):
    TABLE = [[] for i in range(8)]
    for i in range(8):
        TABLE[i] = load_table("./TABLE{}".format(i))
    print("Tables loaded")
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
            print("Found potential Ezero at t = {}".format(t))
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
            return

class Worker():
    def __init__(self):
        self.pool = mp.Pool()
        bytedump = open("./dump", "rb")
        self.z = bytedump.read()
        bytedump.close()
        self.ffcsr = ffcsrh.F_FCSR_H(0, 0)

    def callback(self, result):
        if result:
            print("Solution found! Yay!")
            self.pool.terminate()

    def do_job(self):
        size_of_dump = len(self.z)
        sub_size = size_of_dump // mp.cpu_count()
        results = [self.pool.apply_async(find_solutions, [self.z, self.ffcsr, range(i, i + sub_size)]) for i in range(0, size_of_dump, sub_size)]
        self.pool.close()
        self.pool.join()

def main():
    """
    Main function
    """
    #pool = mp.Pool()
    #cpu_count = mp.cpu_count()
    
    #ffcsr = ffcsrh.F_FCSR_H(0, 0) # Better avoid creating this more than one time

    # Reading the output values of our ffcsr from a file
    #bytedump = open("./dump", "rb")
    #z = bytedump.read()
    #bytedump.close()
    #size_of_dump = len(z)

    #sub_size = size_of_dump // cpu_count
    #find_solutions(TABLE, z, ffcsr, range(36430000, size_of_dump))
    #result = pool.apply_async(find_solutions, [z, ffcsr, range(36430000, size_of_dump)])
    #print(result.get())
    worker = Worker()
    worker.do_job()
    #results = [pool.apply_async(find_solutions, [z, ffcsr, range(i, i + sub_size)]) for i in range(0, size_of_dump, sub_size)]
    

    
if __name__ == "__main__":
    #cProfile.run('main()')
    main()
