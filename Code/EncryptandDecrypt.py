import numpy as np
import random
import PIL.Image
import PIL
import time
import matplotlib.pyplot as plt


def read_image(path):
    try:
        image = PIL.Image.open(path)
        return image
    except Exception as e:
        print(e)


def convert_to_grayscale(image):
    grayscale = image.convert("L")
    return grayscale


def matrix_sum(matrix, index, type):
    sum = 0
    if type == 0:  # column:
        for i in range(len(matrix[0])):
            sum += matrix[index][i]
    else:
        for i in range(len(matrix)):
            sum += matrix[i][index]
    return sum


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


def xor_operation(array, KRC, revKRC, i, j):
    if (i % 2) == 0:
        return array[i][j] ^ revKRC[j]
    else:
        return array[i][j] ^ KRC[j]

# --------------------------------------------------------------------------------------------------

start = time.time()
path = "lena.png"
I_0 = read_image(path)

mode_to_bpp = {'1': 1, 'L': 8, 'P': 8, 'RGB': 24, 'RGBA': 32, 'CMYK': 32, 'YCbCr': 24, 'I': 32, 'F': 32}
grayscale = convert_to_grayscale(I_0)

I_0 = grayscale
img_array = np.array(grayscale)
org_array = np.copy(img_array)
bpp = mode_to_bpp[I_0.mode]
# Bitsize bulundu. Grayscale için genellikle bpp=8

max_iteration = 1

M = len(img_array)
N = len(img_array[0])

KR = []
KC = []

print("---- Original Matrix: \n" + format(img_array))

# DEFINE KC AND KR
for i in range(0, M):
    KR.insert(i, random.randint(0, (2 ** bpp) - 1))
for j in range(0, N):  # prep
    KC.insert(j, random.randint(0, (2 ** bpp) - 1))

# SECTION 4-5 SUM AND SHIFT
for i in range(0, M):  # 4
    Ma = matrix_sum(img_array, i, 0) % 2  # 4a 4b
    img_array[i] = row_shift_by(Ma, abs(KR[i] % M), img_array, i)  # 4c

for i in range(0, N):  # 5
    Mb = matrix_sum(img_array, i, 1) % 2  # 5a 5b7
    img_array = col_shift_by(Mb, abs(KC[i] % N), img_array, i)

# SECTION 6 XOR OPERATIONS
revKC = KC[::-1]
revKR = KR[::-1]

for i in range(0, M):
    for j in range(0, N):
        img_array[i][j] = xor_operation(img_array, KR, revKR, i, j)

for j in range(0, N):
    for i in range(0, M):
        img_array[i][j] = xor_operation(img_array, KC, revKC, i, j)

print("---- Encrypted Matrix: \n" + format(img_array))
print("KR: " + format(KR))
print("KC: " + format(KC))

savepath = "enc_" + format(path)
enc_photo = PIL.Image.fromarray(img_array)
enc_photo = enc_photo.save(savepath)
encrypted=np.copy(img_array)

print("\n----- Decryption ----")

# DECRYPT XOR OPERATIONS

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

savepath = "dec_" + format(path)
dec_photo = PIL.Image.fromarray(img_array)
dec_photo = dec_photo.save(savepath)

print("---- Decrypted Matrix: \n" + format(img_array))

plt.scatter(org_array, encrypted)
plt.show()
corr1 = np.corrcoef(org_array.flat, encrypted.flat)
print("\nCorrelation Between Encrypted and Original Matrix: "+format(corr1[0, 1]))

plt.scatter(img_array, org_array)
plt.show()
corr2 = np.corrcoef(org_array.flat, img_array.flat)
print("\nCorrelation Between Decrypted and Original Matrix: "+format(corr2[0, 1]))
end = time.time()
print(path + " Dosyasının Şifreleme ve Deşifreleme Süresi: " + format(end - start))