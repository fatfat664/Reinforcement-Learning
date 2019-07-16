import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from PIL import Image
np.set_printoptions(threshold=sys.maxsize)


def compute_array(df, current_index, window_size):  # Arranges the prices in graph format
    test_array = []

    # Creating the array
    for i in range(current_index - window_size + 1, current_index + 1):
        if i < 0:
            print("Indexing error")
            break

        data = df[['Low', 'Close', 'Open', 'High']].iloc[i].values

        low = data[0]
        close = data[1]
        open = data[2]
        high = data[3]

        test_array.append([high, open, close, low])

    test_array = np.transpose(test_array)
    return test_array


def reduce_dim(test_array, scaling_factor):  # Converts the prices into indexes and rescales according to the Max Range

    test_array = test_array - np.amin(test_array)
    test_array = test_array * scaling_factor

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
    final_array = np.zeros(static_image_size)

    close_current = test_array[len(test_array) - 2][columns - 1]  # TODO: Comment this
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
                    final_array[i][j] = 40

            for i in range(close, open):
                if i < static_image_size[0] and i >= 0:
                    final_array[i][j] = 10

            for i in range(open, high):
                if i < static_image_size[0] and i >= 0:
                   final_array[i][j] = 100

        else:
            for i in range(low, open):
                if i < static_image_size[0] and i >= 0:
                    final_array[i][j] = 40

            for i in range(open, close):
                if i < static_image_size[0] and i >= 0:
                    final_array[i][j] = 150

            for i in range(close, high):
                if i < static_image_size[0] and i >= 0:
                    final_array[i][j] = 100

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


if __name__ == '__main__':  # To run tests, is not accessed during main function call

    # Parameters
    current_index = 4  # Index to get data from
    window_size = 5  # Number of data points in the state
    static_image_size = (64, 5)  # Shape on input image into the CNN.
    mode = 'train'

    if mode == 'train':
        df = pd.read_csv("S&P500_train.csv")
    else:
        df = pd.read_csv("S&P500_train.csv")

    data_high = df['High'].values
    data_open = df['Open'].values
    data_close = df['Close'].values
    data_low = df['Low'].values

    # To compute a 2D array of low, close, open, high prices as indexes
    test_array = compute_array(df, current_index, window_size)
    print(test_array)

    # Calculating Dollars per pixel based on max range
    maxRange = -1000000
    for i in range(0, 252):
        maxRange = max(maxRange,
                       max(data_high[i:i + window_size]) - min(data_low[i:i + window_size]))

    print("Max range = ", maxRange)
    dollars_per_pixel = maxRange/64
    print("Dollars per Pixel = ", dollars_per_pixel)
    scaling_factor = 1 / dollars_per_pixel
    print("Scaling Factor = ", scaling_factor)

    test_array = reduce_dim(test_array, scaling_factor)
    print(test_array)

    # To plot a stacked bar graph based on the test array for visualization
    make_graph(test_array, current_index, window_size)
    plt.show()

    # Creating the final colored 2D array representation of the graph
    final_array = coloring(test_array, static_image_size)
    print((final_array).shape)

    # To check if I've got the pixel values correctly
    save_to_file(final_array)
    date = '12.12.2016'
    reward = 5.26
    action = 'Sell'

    # Displaying the graph equivalent of my np array CNN fodder
    im = Image.fromarray(np.uint8(final_array), 'L')
    im.save("Images/{}ing-{}-{}-{}.bmp".format(action, date, round(dollars_per_pixel, 4), str(round(reward, 2))))
    im.show()