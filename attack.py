def main():
    bytedump = open("./dump", "rb")
    bytestream = bytedump.read()

    for i in range(len(bytestream)):
        print(int(bytestream[i]))
        W = [0] * 8
        for j in range(8):
            W[j] = 0

    bytedump.close()

if __name__ == "__main__":
    main()
