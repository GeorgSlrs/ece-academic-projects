for i in range(40000):
    if i%50==0:
        print(f"\n{i}-{i+9}: ", end="")
    print(chr(i), end="")