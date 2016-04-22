# coding: utf-8

KEY_SIZE = 80
MASK_80b = 0xffffffffffffffffffff

feedback_polynomial = 0xAE985DFF26619FC58623DC8AAF46D5903DD4254E

class F_FCSR_H:
    """
    Classe représentant un F-FCSR
    """
    def __init__(self, key, iv):
        """
        Fonction d'initialisation du F-FCSR
        """
        self.filter = feedback_polynomial
        self.key = key & MASK_80b
        self.iv = iv & MASK_80b
        self.state = (self.iv << KEY_SIZE) | self.key
        self.carry = 0x00
        
        S = [0] * 20
        for i in range(20):
            self.clock()
            S[i] = self.filter_function()

        self.state = 0x00
        for i in range(20):
            shift = i * 8
            self.state |= (S[i] << shift)

        self.carry = 0x00
        for _ in range(162):
            self.clock()
        
    def clock(self):
        """
        Fonction simulant un tick d'horloge
        """
        fb = self.state & 0x01
        feedback = feedback_polynomial if fb != 0 else 0x00
        self.state = self.state >> 1
        buffer = self.state ^ self.carry
        self.carry &= self.state
        
        self.carry ^= (buffer & feedback)
        buffer ^= feedback
        self.state = buffer

    def filter_function(self):
        """
        Fonction extrayant un octet avec la fonction de filtrage
        """
        buffer = self.filter & self.state
        buffer ^= ((buffer >> 32) & 0xffffffff)
        buffer ^= ((buffer >> 64) & 0xffffffff)
        buffer ^= ((buffer >> 96) & 0xffffffff)
        buffer ^= ((buffer >> 128) & 0xffffffff)
        buffer = buffer & 0xffffffff
        buffer ^= (buffer >> 16)
        buffer ^= (buffer >> 8)
        
        return (buffer & 0xff)

    def process_bytes(self, input, len):
        """
        Fonction permettant de chiffrer ou déchiffrer un
        message de taille donnée
        """
        output = [0] * len

        for i in range(len):
            self.clock()
            try:
                output[i] = ord(input[i]) ^ self.filter_function()
            except TypeError:
                output[i] = (input[i] & 0xff) ^ self.filter_function()

        return output

    # Debuging & Attack related stuff
    def generate_byteseq(self, filename, length):
        output = open(filename, "wb")
        for i in range(length):
            self.clock()
            output.write((self.filter_function().to_bytes(1, byteorder="big")))
        output.close()

    def goto_ezero(self):
        self.set_state(0b11110101100101101011011010000010000011010111011100000001011111010010011111111101011111011010000000001001001110001001010011110010011111111111111111111100)
        self.set_carry(0b100000000000000000000000000000100000000000000000000001000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000010)

    def print_z(self):
        self.goto_ezero()
        for i in range(20):
            self.clock()
            print("z(t+{})\t= ({})".format(i, format(self.filter_function(), '08b')))
    
    def print_M(self, i):
        self.goto_ezero()
        self.clock()
        M = [0] * 20
        for k in range(160):
            if k % 8 == i:
                M[19 - (k // 8)] = ((self.state & (1 << k)) >> k)
        print("M{} = ({})".format(i, M))

    def print_W(self, i):
        self.goto_ezero()
        W = [0] * 20
        for k in range(20):
            self.clock()
            index = (i - k) % 8
            W[k] = ((self.filter_function() & (1 << index)) >> index)
        print("W{} = ({})".format(i, W))

    def find_ezero(self, length):
        print("Initial C: {}".format(self.carry))
        zeroes = 0
        maxz = 0
        back_t = 0
        back_state = 0
        back_carry = 0
        self.goto_ezero()
        self.clock()
        print(format(self.state, '08b'))
        for i in range(length):
            self.clock()
            self.filter_function()
            if self.carry == 0b10:
                zeroes += 1
                if zeroes >= 20:
                    print("Ezero happens at t = {}".format(i+1))
                    print("After t = {}, C = 0b10 {} times in a row".format(back_t, zeroes))
                    print("State at t = {}:\n{}\n{}".format(back_t, bin(back_state), bin(back_carry)))
            else:
                if zeroes > maxz:
                    maxz = zeroes
                    print("Current maximum: {}".format(maxz))
                zeroes = 0
                back_t = i
                back_state = self.state
                back_carry = self.carry

    def set_state(self, state):
        self.state = state

    def set_carry(self, carry):
        self.carry = carry
