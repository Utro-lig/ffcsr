import ffcsrh
import ffcsr16

def main():
    """ Main function """
    # F-FCSR-H
    print("\nF-FCSR-H")
    key = 0x088639d6bf847ed59c6
    iv = 0x112233445566778899
    text = "SOSEMANUK"
    FFCSRH_cipher = ffcsrh.F_FCSR_H(key, iv)
    FFCSRH_decipher = ffcsrh.F_FCSR_H(key, iv)
    print("Plaintext: {}".format(text))

    ctext = FFCSRH_cipher.process_bytes(text, 9)
    print("Ciphered text: {}".format(ctext))

    dctext = FFCSRH_decipher.process_bytes(ctext, 9)
    print("Deciphered text: {}".format(dctext))

    # F-FCSR-16
    print("\nF-FCSR-16")
    key = 0x088639d6bf847ed59c621795d3363f1
    iv = 0x0112233445566778899aabbccddeeff
    text = "F-FCSR-16!"
    FFCSR16_cipher = ffcsr16.F_FCSR_16(key, iv)
    print("Plaintext: {}".format(text))

    ctext = FFCSR16_cipher.process_bytes(text, 10)
    print("Ciphered text: {}".format(ctext))

if __name__ == "__main__":
    main()