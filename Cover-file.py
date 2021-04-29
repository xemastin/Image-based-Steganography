from PIL import Image
from shutil import copyfile
import os
from os import path
import traceback

# Hàm được sử dụng đối với dữ liệu cần che giấu là file
def genData(file):
    byte = file.read(1)
    newd = []
    while byte:
        newd.append(format(ord(byte), "08b"))
        byte = file.read(1)

    return newd


# Hàm được sử dụng đối với dữ liệu cần che giấu là văn bản
def genDatabyText(file):

    newd = []

    for i in file:
        newd.append(format(ord(i), "08b"))
    return newd


def modPix(pix, file):

    datalist = file
    lendata = len(datalist)
    imdata = iter(pix)
    # Với mỗi kí tự đã được chuyển sang dạng bit
    for i in range(lendata):
        # Mỗi lần imdata.__next__() được gọi đến thì trả về 3 value của một pixel
        pix = [
            value
            for value in imdata.__next__()[:3]
            + imdata.__next__()[:3]
            + imdata.__next__()[:3]
        ]
        # Xét 8 bit có trong mảng
        for j in range(0, 8):
            # Xét từng bit trong byte
            # Nếu bit j là số 0 thì pixel sẽ giảm đi 1 để trở thành số chẵn
            if datalist[i][j] == "0" and pix[j] % 2 != 0:
                pix[j] -= 1
            # Nếu bit j là số 1 thì pixel sẽ giảm đi 1 để trở thành số lẻ
            elif datalist[i][j] == "1" and pix[j] % 2 == 0:
                if pix[j] != 0:
                    pix[j] -= 1
                # Trường hợp giá trị của pixel này là số 0 thì ta cộng 1 để trở thành
                # số lẻ vì pixel không có giá trị -1
                else:
                    pix[j] += 1

        # Nếu đây là 8 bit cuối cùng trong chuỗi dữ liệu được ẩn giấu
        if i == lendata - 1:
            # Giá trị pixel thứ 9 trong 3 pixels sẽ được đặt
            # thành số lẻ nếu không còn dữ liệu được ẩn giấu
            if pix[-1] % 2 == 0:
                if pix[-1] != 0:
                    pix[-1] -= 1
                else:
                    pix[-1] += 1
        # Trường hợp vẫn còn dữ liệu
        else:
            # Giá trị pixel này sẽ luôn được đặt thành số chẵn
            if pix[-1] % 2 != 0:
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]  # Trả về pixel 1
        yield pix[3:6]  # Trả về pixel 2
        yield pix[6:9]  # Trả về pixel 3


def encode_enc(newimg, file):
    w = newimg.size[0]  # Trả về chiều rộng của bức hình
    (x, y) = (0, 0)  # Cặp giá trị width : height

    for pixel in modPix(newimg.getdata(), file):

        # Đặt từng pixel đã được thay đổi vào trong hình ảnh mới
        newimg.putpixel((x, y), pixel)
        if x == w - 1:
            x = 0
            y += 1
        else:
            x += 1


def encode():
    # Nhập vào tên file hình ảnh
    img = input("Enter image name(with extension): ")
    # Tạo nên tập tin tạm
    img_temp = "temp.png"
    copyfile(img, img_temp)
    # Đọc dữ liệu của hình ảnh
    image = Image.open(img_temp, "r")
    newimg = image.copy()
    # Nhập tên file hoặc văn bản
    check = input("Enter txt file name or text need to be encoded: ")
    # Nếu không có file tồn tại thì sẽ được xem là văn bản
    if path.isfile(check):
        filee = open(check, "rb")
        encode_enc(newimg, genData(filee))
    else:
        encode_enc(newimg, genDatabyText(check))
    # Tạo hành file hình ảnh dựa vào dữ liệu mới
    new_img_name = input("Enter the name of new image (without extension):  : ")
    newimg.save(new_img_name + ".png")
    os.remove(img_temp)


def decode():
    # Mở hình ảnh chứa dữ liệu được che giấu
    img = input("Enter image name(with extension) : ")
    image = Image.open(img, "r")

    data = ""
    imgdata = iter(image.getdata())
    file = open("Result.txt", "at")
    while True:
        # Đọc lần lượt 3 pixel của hình ảnh
        pixels = [
            value
            for value in imgdata.__next__()[:3]
            + imgdata.__next__()[:3]
            + imgdata.__next__()[:3]
        ]

        # Biến chứa chuỗi nhị phân đọc được
        binstr = ""
        # Đọc từng giá trị trong pixel
        for i in pixels[:8]:
            if i % 2 == 0:
                binstr += "0"
            else:
                binstr += "1"
        # Chuyển mỗi 8bit thành một kí tự
        data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            break
    # Ghi dữ liệu vào file
    file.write(data)
    file.close()
    return "Result.txt"


def main():
    a = int(input(":: Welcome to Steganography ::\n" "1. Encode\n2. Decode\n"))
    if a == 1:
        encode()

    elif a == 2:
        print("Decoded Word : " + decode())
    else:
        raise Exception("Enter correct input")


try:
    main()
except Exception as err:
    os.remove("temp.png")
    os.remove("Result.txt")
    traceback.print_tb(err.__traceback__)
