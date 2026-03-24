import sys

def get_scalars_from_args():
    if len(sys.argv) != 4:
        print("Usage: python process_scalars.py <matrix-scalar-1> <matrix-scalar-2> <matrix-scalar-3>")
        sys.exit(1)
    try:
        d1 = int(sys.argv[1])
        d2 = int(sys.argv[2])
        d3 = int(sys.argv[3])
        return d1, d2, d3
    except ValueError:
        print("Invalid input. Expected scalars need to be integers.")
        return
 
def main():
    d1, d2, d3 = get_scalars_from_args()

    flag = f"apoorvctf{{{d1}_{d2}_{d3}}}"
    print(flag)


if __name__ == "__main__":
    main()