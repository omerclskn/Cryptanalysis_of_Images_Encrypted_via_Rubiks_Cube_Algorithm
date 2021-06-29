import numpy as np
import random
import PIL.Image
import PIL
import matplotlib.pyplot as plt


def read_image(path):
    try:
        image = PIL.Image.open(path)
        return image
    except Exception as e:
        print(e)


def matrix_sum(matrix, index, type):
    sum = 0
    if type == 0:  # column:
        for i in range(len(matrix[0])):
            sum += matrix[index][i]
    else:
        for i in range(len(matrix)):
            sum += matrix[i][index]
    return sum


def xor_operation(array, KRC, revKRC, i, j):
    if (i % 2) == 0:
        return array[i][j] ^ revKRC[j]
    else:
        return array[i][j] ^ KRC[j]


def col_shift_by(direction, num, array, colno):
    length = len(array)
    temp = np.arange(length)
    if direction == 0:  # shift down
        for j in range(0, length):
            temp[j] = array[(j - num + length) % length][colno]
    else:  # shift up
        for j in range(0, length):
            temp[j] = array[(j + num) % length][colno]
    for j in range(0, length):
        array[j][colno] = temp[j]
    return array


def row_shift_by(direction, num, array, rowno):
    length = len(array[0])
    temp = np.arange(length)
    if direction == 0:  # shift right
        for j in range(0, length):
            temp[j] = array[rowno][(j - num + length) % length]
    else:  # shift left
        for j in range(0, length):
            temp[j] = array[rowno][(j + num) % length]
    return temp


# --------------------------------------------------------------------------------------------------


path_enc = "enc_lena_32.png"
path_dec = "dec_lena_32.png"

IO_enc = read_image(path_enc)
IO_dec = read_image(path_dec)

img_array = np.array(IO_enc)
org_array = np.array(IO_dec)
bpp = 8

max_iteration = 1

M = len(img_array)
N = len(img_array[0])

print(format(M) + format(N))

KR = []
KC = []
correlation = 0

k = 1

print("---- Original Matrix: \n" + format(img_array))
while correlation < 0.30:
    # DEFINE KC AND KR

    for i in range(0, M):
        KR.insert(i, random.randint(0, 255))
    for j in range(0, N):  # prep
        KC.insert(j, random.randint(0, 255))

    print("\n----- Attack ---- " + format(k))

    # DECRYPT XOR OPERATIONS

    revKC = KC[::-1]
    revKR = KR[::-1]

    for j in range(0, N):
        for i in range(0, M):
            img_array[i][j] = xor_operation(img_array, KR, revKR, i, j)

    for i in range(0, M):
        for j in range(0, N):
            img_array[i][j] = xor_operation(img_array, KC, revKC, i, j)

    # DECRYPT SUM-SHIFT OPERATIONS !!

    for i in range(0, N):
        Mb = matrix_sum(img_array, i, 1) % 2
        img_array = col_shift_by(not Mb, abs(KC[i] % N), img_array, i)

    for i in range(0, M):
        Ma = matrix_sum(img_array, i, 0) % 2
        img_array[i] = row_shift_by(not Ma, abs(KR[i] % M), img_array, i)

    print("---- Cracked Matrix: \n" + format(img_array))

    plt.scatter(img_array, org_array)
    corr2 = np.corrcoef(org_array.flat, img_array.flat)
    correlation = corr2[0, 1]
    k += 1
    print(format(corr2[0, 1]))

plt.show()
savepath = "attack_lena.png"
dec_photo = PIL.Image.fromarray(img_array)
dec_photo = dec_photo.save(savepath)

print("\nCorrelation Between Decrypted and Original Matrix: " + format(corr2[0, 1]))
