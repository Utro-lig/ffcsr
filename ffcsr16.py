KEY_SIZE = 128
MASK_128b = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

feedback_polynomial = 0xCB5E129FAD4F7E66780CAA2EC8C9CEDB2102F996BAF08F39EFB55A6E390002C6

class F_FCSR_16:
    """
    Classe représentant un F-FCSR
    """
    def __init__(self, key, iv):
        """
        Fonction d'initialisation du F-FCSR
        """
        self.filter = feedback_polynomial
        self.key = key & MASK_128b
        self.iv = iv & MASK_128b
        self.state = (self.iv << KEY_SIZE) | self.key
        self.carry = 0x00
        
        S = [0] * 16
        for i in range(16):
            self.clock()
            S[i] = self.filter_function()

        self.state = 0x00
        for i in range(16):
            shift = i * 16
            self.state |= (S[i] << shift)

        self.carry = 0x00
        for _ in range(258):
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
        buffer = (self.filter & self.state) & 0xFFFFFFFF
        buffer ^= (self.filter & self.state) >> KEY_SIZE
        buffer ^= ((buffer >> 32) & 0xffffffff)
        buffer ^= ((buffer >> 64) & 0xffffffff)
        buffer ^= ((buffer >> 96) & 0xffffffff)
        buffer ^= (buffer >> 16)
        
        return (buffer & 0xFFFF)

    def process_bytes(self, input, len):
        """
        Fonction permettant de chiffrer ou déchiffrer un
        message de taille donnée
        """
        output = [0] * len

        for i in range(0, len, 2):
            self.clock()
            buffer = self.filter_function()
            try:
                output[i] = ord(input[i]) ^ (buffer & 0xFF)
                output[i + 1] = ord(input[i + 1]) ^ (buffer >> 8)
            except TypeError:
                output[i] = (input[i] & 0xff) ^ (buffer & 0xFF)
                output[i + 1] = (input[i + 1] & 0xff) ^ (buffer >> 8)

        return output