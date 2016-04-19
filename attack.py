def main():
    bytedump = open("./dump", "rb")
    z = bytedump.read()

    for t in range(len(z)):
        for i in range(8):
            Wi = [0] * 20
            for k in range(20):
                Wi[k] = 1 if ((z[t + k] & (((i - k) & 7) << 1)) != 0) else 0
            print("W{}: {}".format(i, Wi))
    bytedump.close()

if __name__ == "__main__":
    main()
