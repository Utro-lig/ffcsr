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