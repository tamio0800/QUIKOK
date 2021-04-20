from time import time

def test_1(n=5000000):
    x = 'dwerfwrfwefd'
    st1 = time()
    for _ in range(n):
        len(x)
    end1 = time()
    for _ in range(n):
        x == ''
    end2 = time()
    for _ in range(n):
        x in ['',]
    end3 = time()
    for _ in range(n):
        x != ''
    end4 = time()
    for _ in range(n):
       not x == ''
    end5 = time()
    
    print(f"\nlen() takes {end1-st1} seconds\n=='' takes {end2-end1} seconds\nin takes {end3-end2} seconds\n!='' takes {end4-end3} seconds\nnot =='' takes {end5-end4} seconds\n")

if __name__ == '__main__':
    test_1()