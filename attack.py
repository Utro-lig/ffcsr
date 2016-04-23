import ffcsrh
import cProfile

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

def rotate_left(array, n):
    """ Array rotation """
    return array[n:] + array[:n]

def rebuild_state(M):
    """
    Converts Mi matrices to an integer representation of the main register
    """
    result = 0
    for i in range(160):
        result = result | (int(M[i % 8][19 - (i // 8)]) << i)
    return result

def try_paths(cipher, t, z, M, P=[None]*8, depth=0):
    """
    Tests every solution given by Mi matrices
    """
    if depth >= len(M):
        state = rebuild_state(P)
        cipher.set_state(state)
        cipher.set_carry(0b10)
        correct_state = True
        for i in range(40):
            if ord(z[t + i]) != cipher.filter_function():
                return None
            cipher.clock()
        return state
    else:
        for i in range(len(M[depth])):
            P[depth] = M[depth][i]
            result = try_paths(cipher, t, z, M, P, depth + 1)
            if result != None:
                return result
        return None

def test_solutions(t, z, M):
    """
    Wrapper for our recursive function
    """
    ffcsr = ffcsrh.F_FCSR_H(0, 0) # Better avoid creating this more than one time
    return try_paths(ffcsr, t, z, M) 

def main():
    """
    Main function
    """
    # Reading the output values of our ffcsr from a file
    bytedump = open("./dump", "rb")
    z = bytedump.read()
    bytedump.close()
    size_of_dump = len(z)

    # Initializing our vector and matrix spaces
    VS = VectorSpace(GF(2), 20)
    MS = MatrixSpace(GF(2), 20, 20)

    # Gonna need this
    F = [None] * 8
    F[0] = 0b00110111010010101010
    F[1] = 0b10011010110111000001
    F[2] = 0b10111011101011101111
    F[3] = 0b11110010001110001001
    F[4] = 0b01110010001000111100
    F[5] = 0b10011100010010001010
    F[6] = 0b00110101001001100101
    F[7] = 0b11010011101110110100

    # Generating Pi's
    print("Generating Pi matrices ...")
    P = [None] * 8
    Prows = [[None] * 20 for i in range(8)]
    for k in range(8):
        j = k
        V = [None] * 20
        for i in range(20):
            shift = (i + j) // 8
            V[i] = rotate_left(bin_to_array(F[j]), shift)
            Prows[k][i] = VS(V[i]) # Avoid calling P.matrix_from_rows later on
            j = (j - 1) % 8
        P[k] = MS(V)

    # Precomputing Ci's
    C = [VS() for i in range(8)]
    print("Generating Ci matrices ...")
    for i in range(8):
        Ci = VS()
        for k in range(20):
            bit_index = (i - k) % 8
            # Holy crap, fasten your seatbelt, we're computing the carries
            C[i][k] = Prows[i][k]*Ci
            if (k % 8) == ((i-2) % 8):
                Ci[19 - ((k + bit_index) // 8)] = 1

    print("Starting search")
    W = [VS()] * 8
    # Starting at 36430000 because this shit is fucking slow right now
    # Main loop
    for t in range(36434700, size_of_dump):
        nb_solved = 0
        M = [[]]*8
        # Computing Wi's
        for i in range(8):   
            for k in range(20):
                bit_index = (i - k) % 8
                W[i][k] = ((ord(z[t + k]) & (1 << bit_index)) >> bit_index)
                    
            # Try to solve the associated system of equations
            try:
                particular_solution = P[i].solve_right(W[i]+C[i])
                # Look for other solutions, if there are any
                for homogeneous_soln in P[i].right_kernel():
                    M[i] = M[i] + [particular_solution + homogeneous_soln]
                nb_solved += 1
            # No solution, skip this batch !
            except ValueError:
                break

        # We found something interesting
        if nb_solved == 8:
            print("Found potential Ezero at t = {}".format(t))
            state = test_solutions(t, z, M)
            if state == None:
                print("Not good, continuing ...")
                continue
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
            return
    
if __name__ == "__main__":
    #cProfile.run('main()')
    main()
