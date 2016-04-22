import pickle
import thread

#TABLE = [[[]] * (2**20) for i in range(8)]

def save_obj(obj, name):
    with open('tables/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def precompute_table(i, P, C):
    print("Generating TABLE{} ...".format(i))
    TABLE = [[]] * (2**20)
    for k in range(2**20):
        try:
            particular_solution = P[i].solve_right(bin_to_vec(k)+C[i])
            for homogeneous_solution in P[i].right_kernel():
                TABLE[k] = TABLE[k] + [particular_solution + homogeneous_solution]
        except ValueError:
            continue #TABLE[k] = []

    save_obj(TABLE, "TABLE{}".format(i))
    print("TABLE{} generated !".format(i))

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

if __name__ == '__main__':
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
    
    # Starting table generation
    for i in range(8):
        thread.start_new_thread(precompute_table, (i, P, C, ))
    while True:
        pass
