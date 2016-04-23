from ffcsrh import F_FCSR_H

DUMP_PATH = "./"
DUMP_SIZE = 2**26

def main():
    key = 0x088639d6bf847ed59c6
    iv = 0x112233445566778899
    ffcsr = F_FCSR_H(key, iv)
    
    output = open(DUMP_PATH + "dump", "wb")
    for i in range(DUMP_SIZE):
        ffcsr.clock()
        output.write((ffcsr.filter_function().to_bytes(1, byteorder="big")))
    output.close()

if __name__ == '__main__':
    main()
