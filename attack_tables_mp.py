import ffcsrh
import cPickle as pickle
import cProfile
from multiprocessing import Pool

ffcsr = ffcsrh.F_FCSR_H(0, 0) # Better avoid creating this more than one time
TABLE = [[[]] * 2**(20) for i in range(8)]
z = []

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
        result = result | (int(v[19 - i]) << i)
    return result

def rebuild_state(M):
    """
    Converts Mi matrices to an integer representation of the main register
    """
    result = 0
    for i in range(8):
        result = result | M[i]
    return result

def try_paths(t, z, M, P=[0]*8, depth=0):
    """
    Tests every solution given by Mi matrices
    """
    if depth >= len(M):
        state = rebuild_state(P)
        ffcsr.set_state(state)
        ffcsr.set_carry(0b10)
        correct_state = True
        for i in range(22):
            if ord(z[t + i]) != ffcsr.filter_function():
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

def find_solution(t):
    W = [VS()] * 8
    M = [[]] * 8
    # Computing Wi's
    for i in range(8):
        for k in range(20):
            bit_index = (i - k) % 8
            W[i][k] = ((ord(z[t + k]) & (1 << bit_index)) >> bit_index)

        # Try to solve the associated system of equations
        M[i] = TABLE[i][vec_to_bin(W[i])]
        if len(M[i]) == 0:
            return

    # We found something interesting
    print("Found potential Ezero at t = {}".format(t))
    state = test_solutions(t, z, M)
    if state == None:
        return
    # Master has presented Dobby with a solution
    # Dobby is free \o/
    print("\nA solution has been found:")
    print("M({}) = {}".format(t, hex(state)))
    q = 0x15d30bbfe4cc33f8b0c47b9155e8dab207ba84a9b
    # p(t) = M + 2*C
    pt = IntegerModRing(q)(state + 4)
    # p(0) = p(t) * 2^t mod q
    p0 = IntegerModRing(q)(pt * (2**(t+163)))
    print("M(0) = {}".format(hex(int(p0))))


def main():
    """
    Main function
    """
    # Reading the output values of our ffcsr from a file
    bytedump = open("./dump", "rb")
    z = bytedump.read()
    bytedump.close()
    size_of_dump = len(z)

    pool = Pool()

    # Initializing our vector and matrix spaces
    VS = VectorSpace(GF(2), 20)

    print("Loading tables ...")
    for i in range(8):
        TABLE[i] = load_table("./TABLE{}".format(i))
    
    # Let's go
    print("Starting search")
    pool.map(find_solution, range(0, size_of_dump))
    
if __name__ == "__main__":
    #cProfile.run('main()')
    main()