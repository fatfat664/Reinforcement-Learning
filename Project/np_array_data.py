import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from PIL import Image
np.set_printoptions(threshold=sys.maxsize)

def compute_array(mode, current_index, window_size, precision):

    if mode == 'train':
        df = pd.read_csv("NFLX.csv")  # Reading the data
    elif mode == 'test':
        df = pd.read_csv("NFLX_test.csv")  # Reading the data

    # To store indexes for Low, Close, Open, High for 'window_size' number of days at current_index
    test_array = []

    # Creating the array
    for i in range(current_index - window_size + 1, current_index + 1):
        data = df[['Low', 'Close', 'Open', 'High']].iloc[i].values

        # Standardizing to an integer range for indexes
        low = int(round(data[0], precision) * 10 ** precision)
        close = int(round(data[1], precision) * 10 ** precision)
        open = int(round(data[2], precision) * 10 ** precision)
        high = int(round(data[3], precision) * 10 ** precision)

        test_array.append([high, open, close, low])

    test_array = np.transpose(test_array)
    test_array = test_array - np.amin(test_array)

    return test_array

def reduce_dim(test_array):

    temp = test_array
    temp = temp.flatten()
    temp.sort()
    temp = np.trim_zeros(temp)

    if len(temp) != 0:
        test_array = test_array / temp[0]
    return test_array.astype(int)

def make_graph(test_array, current_index, window_size):

    # Graph drawing parameters
    w = 1.0
    lw = 0.5

    for j in range(0, len(test_array[0])):  # 0 -> Total number of columns
        for i in range(0, len(test_array)):  # 0 -> Total number of rows

            low = test_array[len(test_array) - 1][j]
            close = test_array[len(test_array) - 2][j]
            open = test_array[len(test_array) - 3][j]
            high = test_array[len(test_array) - 4][j]

        # Coloring the graph based on open and close differences
        if open > close:
            plt.bar(current_index - window_size + 1 + j, close - low, width=w, bottom=low, color='#be2409',
                    edgecolor='Black', linewidth=lw)
            plt.bar(current_index - window_size + 1 + j, open - close, width=w, bottom=close, color='Black',
                    edgecolor='Black', linewidth=lw)
            plt.bar(current_index - window_size + 1 + j, high - open, width=w, bottom=open, color='#fddc54',
                    edgecolor='Black', linewidth=lw)
        else:
            plt.bar(current_index - window_size + 1 + j, open - low, width=w, bottom=low, color='#be2409',
                    edgecolor='Black', linewidth=lw)
            plt.bar(current_index - window_size + 1 + j, close - open, width=w, bottom=open, color='White',
                    edgecolor='Black', linewidth=lw)
            plt.bar(current_index - window_size + 1 + j, high - close, width=w, bottom=close, color='#fddc54',
                    edgecolor='Black', linewidth=lw)

    plt.xlabel('Days')
    plt.ylabel('Price Range')
    plt.title('Day vs Price Range')

def coloring(test_array, static_image_size):

    # Dimensions of the final array
    columns = len(test_array[0])  # window_size
    rows = np.amax(test_array)  # Depends on the relative ranges between Low, Close, Open, High

    # Array of 255s (white pixels) based on financial data ranges for 'window_size' number of days at current_index
    final_array = np.ones(static_image_size) * 255
    # final_array = np.ones([rows, columns]) * 255

    close_current = test_array[len(test_array) - 2][columns - 1]
    shift = static_image_size[0]/2 - close_current

    # Filling in the colors in the final array similar to the graph
    for j in range(0, columns):

        low = test_array[len(test_array) - 1][j] + int(shift)
        close = test_array[len(test_array) - 2][j] + int(shift)
        open = test_array[len(test_array) - 3][j] + int(shift)
        high = test_array[len(test_array) - 4][j] + int(shift)

        if open > close:

            for i in range(low, close):
                if i < static_image_size[0] and i >= 0:
                    final_array[i][j] = 100

            for i in range(close, open):
                if i < static_image_size[0] and i >= 0:
                    final_array[i][j] = 50

            for i in range(open, high):
                if i < static_image_size[0] and i >= 0:
                   final_array[i][j] = 150

        else:
            for i in range(low, open):
                if i < static_image_size[0] and i >= 0:
                    final_array[i][j] = 100

            for i in range(open, close):
                if i < static_image_size[0] and i >= 0:
                    final_array[i][j] = 200

            for i in range(close, high):
                if i < static_image_size[0] and i >= 0:
                    final_array[i][j] = 150

    final_array = np.flip(final_array, axis=0)
    return(final_array)

def coloring_visual(test_array):

    # Dimensions of the final array
    columns = len(test_array[0])  # window_size
    rows = np.amax(test_array)  # Depends on the relative ranges between Low, Close, Open, High

    # Creating an array of zeros based on financial data ranges for 'window_size' number of days at current_index
    final_array = np.ones([rows, columns + 127*5]) * 255

    # j -> 0,1,2,3,4
    # j -> 0-127, 128-255, 256-383, 384-511, 512-640

    # Filling in the colors in the final array similar to the graph
    for j in range(0, columns):

        low = test_array[len(test_array) - 1][j]
        close = test_array[len(test_array) - 2][j]
        open = test_array[len(test_array) - 3][j]
        high = test_array[len(test_array) - 4][j]

        if open > close:

            for i in range(low, close):
                final_array[i][(j + (j*127)):(j + ((j+1)*127))] = 100

            for i in range(close, open):
                final_array[i][(j + (j*127)):(j + ((j+1)*127))] = 50

            for i in range(open, high):
                final_array[i][(j + (j*127)):(j + ((j+1)*127))] = 150

        else:
            for i in range(low, open):
                final_array[i][(j + (j*127)):(j + ((j+1)*127))] = 100

            for i in range(open, close):
                final_array[i][(j + (j*127)):(j + ((j+1)*127))] = 200

            for i in range(close, high):
                final_array[i][(j + (j*127)):(j + ((j+1)*127))] = 150

    final_array = np.flip(final_array, axis=0)
    return(final_array)

def save_to_file(final_array):
    f = open("image.txt", "w")

    rows = len(final_array)
    columns = len(final_array[0])

    for i in range(rows):
        for j in range(columns):
            f.write("{}   ".format(str(int(final_array[i][j]))))
        f.write("\n")

    f.close()

if __name__ == '__main__':


    # Parameters
    current_index = 1500  # Index to get data from
    # current_index = 1500  # Index to get data from
    window_size = 5  # Number of data points in the state
    precision = 3  # Number of significant digits after the decimal. Lower values = Doesn't capture fine variations.
    static_image_size = (512, 5)  # Shape on input image into the CNN.
    mode = 'train'

    # TODO: Test for lower precision/longer image if too much data is going out of bounds.
    # TODO: Test for precision combinations. Try and see if you can get the 256 lower

    # To compute a 2D array of low, close, open, high prices as indexes
    test_array = compute_array(mode, current_index, window_size, precision)

    # TODO: For now sacrificing accuracy to reduce size of the input image. Come up with a better representation later.
    # test_array = reduce_dim(test_array)
    print(test_array)
    print(np.amax(test_array))

    # To plot a stacked bar graph based on the test array for visualization
    make_graph(test_array, current_index, window_size)
    plt.show()

    # Creating the final colored 2D array representation of the graph
    final_array = coloring(test_array, static_image_size)
    # final_array = coloring_visual(test_array)  # Uncomment for visualization of the state
    print((final_array).shape)

    # To check if I've got the pixel values correctly
    save_to_file(final_array)
    date = '12.12.2016'
    reward = 5.26
    action = 'Sell'

    # Displaying the graph equivalent of my np array CNN fodder
    im = Image.fromarray(np.uint8(final_array), 'L')
    im.save("Images/{}-{}-{}.bmp".format(action, str(reward), date))
    im.show()