import ffcsrh

def main():
    """ Main function """
    # F-FCSR-H
    print("\nF-FCSR-H")
    key = 0x088639d6bf847ed59c6
    iv = 0x112233445566778899
    text = "SOSEMANUK"
    cipher = ffcsrh.F_FCSR_H(key, iv)
    """cipher.print_z()
    for i in range(8):
        cipher.print_M(i)
    for i in range(8):
        cipher.print_W(i)
    cipher.find_ezero(2**26)
    cipher.generate_byteseq("./dump", 2**26)"""
    decipher = ffcsrh.F_FCSR_H(key, iv)
    print("Plaintext: {}".format(text))

    ctext = cipher.process_bytes(text, 9)
    print("Ciphered text: {}".format(ctext))

    dctext = decipher.process_bytes(ctext, 9)
    print("Deciphered text: {}".format(dctext))

if __name__ == "__main__":
    main()
