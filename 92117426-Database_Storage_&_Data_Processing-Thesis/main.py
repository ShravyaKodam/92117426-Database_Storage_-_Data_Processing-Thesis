from turtle import width
import pandas as pd
from utilities.sqlite_utils import SQLLiteUtils
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral4
from bokeh.plotting import figure, show


# connecting to the Dabase
connectToString = "sqlite:///data.db"


# creating a def function to obtain four points out of the 50 ideal functions given
def idealFunction(trainData, idealData):
    # replacing the column names for uniqueness
    trainData.columns = trainData.columns.str.replace('y', 'train_y')
    idealData.columns = idealData.columns.str.replace('y', 'ideal_y')
    # merging both the tables based on x using pandas
    mergeDataFrame = pd.merge(trainData, idealData, left_on='x', right_on='x', how='inner')
    # creating dataframes to store our final values
    finalValues = pd.DataFrame()
    maxVal = pd.DataFrame()
    # looping through the merged data table
    for c_, i in enumerate([col for col in mergeDataFrame.columns if 'train_' in col]):
        # creating a temporary dataframe
        tempDataframe = pd.DataFrame()
        for j in [col for col in mergeDataFrame.columns if 'ideal_' in col]:
            tempDataframe["{1}_ls".format(i, j)] = (mergeDataFrame[i] - mergeDataFrame[j]) ** 2
        final = str(tempDataframe.sum().idxmin()).split("_")[1]
        finalValues[[final]] = mergeDataFrame[["ideal_" + final]]
        # getting the maximum deviation
        maxVal[final] = [tempDataframe["ideal_" + final + "_ls"].max() ** (1/2)]
    finalValues.insert(loc=0, column='x', value=mergeDataFrame['x'])
    return {'ideal': finalValues, 'max': maxVal}


def testFunction(test, ideal, max_d):
    # merging test and generated ideal functions tables
    mergeDataFrame = test.merge(ideal, on=['x'], how='left')
    testValues['ideal_func'] = None

    for _i, row in mergeDataFrame.iterrows():
        i_func = None
        minimumValue = float('inf')
        for _j, _row in max_d.T.iterrows():
            value = abs(row['y'] - row[_j])
            if _row[0] * (2 ** (1 / 2)) >= value and minimumValue > value:
                minimumValue = value
                i_func = _j
        testValues.at[_i, 'value'] = minimumValue if minimumValue < float('inf') else None
        testValues.loc[_i, 'ideal_func'] = i_func
        testValues.at[_i, 'ideal_y'] = mergeDataFrame[i_func][_i] if i_func else None
    return test

# function to plot the graphs
def _plot(a, b, c, d):
    # first graph with training function 
    graph_1 = figure(title="Training function 1")
    graph_1.circle(a.x.to_list(), a[a.columns[1]].to_list(), color='cyan', legend_label='Ideal Function 1', size=15)
    graph_1.line(b.x.to_list(), b.train_y1.to_list(), color='black', legend_label='Training 1')
    # training function 2 graph
    graph_2 = figure(title="Training function 2")
    graph_2.circle(a.x.to_list(), a[a.columns[2]].to_list(), color='yellow', legend_label='Ideal Function 2',size=15)
    graph_2.line(b.x.to_list(), b.train_y2.to_list(), color='red', legend_label='Training 2')
    # training function 3 graph
    graph_3 = figure(title="Training function 3")
    graph_3.circle(a.x.to_list(), a[a.columns[3]].to_list(), color='pink', legend_label='Ideal Function 3', size=15)
    graph_3.line(b.x.to_list(), b.train_y3.to_list(), color='blue', legend_label='Training 3')
    # training function 4 graph
    graph_4 = figure(title="Training function 4")
    graph_4.circle(a.x.to_list(), a[a.columns[4]].to_list(), color='orange', legend_label='Ideal Function 4', size=15)
    graph_4.line(b.x.to_list(), b.train_y4.to_list(), color='red', legend_label='Training 4')

    # For printing the graphs
    grid = gridplot([[graph_1], [graph_2], [graph_3], [graph_4]], width=1000, height=600)
    show(grid)
if __name__ == "__main__":
    connectSQLite = SQLLiteUtils(conn_string=connectToString)

    # Table 1 - The training data's database table:
    trainValues = pd.read_csv("data/train.csv")
    connectSQLite.put_df(df=trainValues, table='train', conn_string=connectToString)

    # Table 2 - The ideal functions database table:
    idealValues = pd.read_csv("data/ideal.csv")
    connectSQLite.put_df(df=idealValues, table='ideal', conn_string=connectToString)

    # Table 3 - The test data's database table:
    testValues = pd.read_csv("data/test.csv")
    connectSQLite.put_df(df=testValues, table='test', conn_string=connectToString)

    # generated 4 ideal functions, max deviation and mapping test data
    functionData = idealFunction(trainValues, idealValues)
    testMap = testFunction(testValues, functionData['ideal'], functionData['max'])

    # plotting graphs
    _plot(functionData['ideal'], trainValues, functionData['max'], testMap)
    testMap = testMap[['x', 'y', 'value', 'ideal_func']]
    connectSQLite.put_df(df=testMap, table='test_map', conn_string=connectToString)