import ffcsrh
import pickle

DUMP_PATH = "./"
TABLES_PATH = "./"

ffcsr = ffcsrh.F_FCSR_H(0, 0) # Better avoid creating this more than one time

def try_paths(t, z, M, P=[0]*8, depth=0):
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
            result = try_paths(t, z, M, P, depth + 1)
            if result != None:
                return result
        return None

def test_solutions(t, z, M):
    """
    Wrapper for our recursive function
    """
    return try_paths(t, z, M) 

def load_table(name):
    fp = open(name, 'rb')
    table = pickle.load(fp)
    fp.close()

    return table

def main():
    """
    Main function
    """
    # Reading the output values of our ffcsr from a file
    bytedump = open(DUMP_PATH + "dump", "rb")
    z = bytedump.read()
    bytedump.close()
    size_of_dump = len(z)

    print("Loading tables ...")
    TABLE = [[[]] * 2**(20) for i in range(8)]
    for i in range(8):
        TABLE[i] = load_table(TABLES_PATH + "TABLE{}".format(i))
        print("TABLE{} loaded !".format(i))
    
    print("Starting search")
    # Main loop
    for t in range(0, size_of_dump):
        nb_solved = 0
        M = [[]] * 8
        # Computing Wi's
        W = [0] * 8
        for i in range(8):   
            for k in range(20):
                bit_index = (i - k) % 8
                W[i] = W[i] | (((z[t + k] & (1 << bit_index)) >> bit_index) << (19 - k))
            # Try to solve the associated system of equations
            M[i] = TABLE[i][W[i]]
            if len(M[i]) > 0:
                nb_solved += 1
            # No solution, skip this batch !
            else:
                break

        # We found something interesting
        if nb_solved == 8:
            #print("Found potential Ezero at t = {}".format(t))
            state = test_solutions(t, z, M)
            if state == None:
                #print("Not good, continuing ...")
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
    
if __name__ == "__main__":
    main()
