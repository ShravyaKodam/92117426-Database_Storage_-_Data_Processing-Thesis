import sqlite3
#to create database
from utilities.sqlite_utils import SQLLiteUtils
#provide the collection of palettes for color mapping in the graph
from bokeh.palettes import Spectral4 
#arrage the layout objects
from bokeh.layouts import gridplot 
#sharing the data between the plots and data tables
from bokeh.models import ColumnDataSource
#for visualizations
from bokeh.plotting import figure, show
from bokeh.io import curdoc
#to deal with the dataframes
import pandas as pd


# connecting to the Dabase
connectToString = "sqlite:///data.db"


#creating a def function to obtain four points out of the 50 ideal functions given
def idealFunction(trainData, idealData):
    #naming the column variables
    trainData.columns = trainData.columns.str.replace("y", "trainValue_y")
    #print(trainData.columns)
    idealData.columns = idealData.columns.str.replace("y", "idealValue_y")
    #merging the tables
    mergeDataFrame = pd.merge(trainData, idealData, right_on='x', left_on='x')
    #print(mergeDataFrame)
    #creating dataframes
    finalValues = pd.DataFrame()
    maxVal = pd.DataFrame()
    #performing looing to deal with large data
    mergeDFcolumns=[d_ for d_ in mergeDataFrame.columns if 'trainValue_' in d_]
    #print(mergeDFcolumns)
    for a_, b_ in enumerate(mergeDFcolumns):
        #for temporary dataframe
        tempDataframe = pd.DataFrame()
        columnDataFrame=[d_ for d_ in mergeDataFrame.columns if 'idealValue_' in d_]
        #print(columnDataFrame)
        for c_ in columnDataFrame:
            k="{1}_ls".format(b_, c_)
            tempDataframe[k] = (mergeDataFrame[b_] - mergeDataFrame[c_]) ** 2
        tempDF=tempDataframe.sum().idxmin()
        final = str(tempDF).split("_")[1]
        finalValues[[final]] = mergeDataFrame[["idealValue_" + final]]
    print(finalValues)
        # getting the maximum deviation
    '''maxVal[final] = [tempDataframe["idealValue_" + final + "_ls"].max() ** (0.5)]
    print(maxVal)'''
    finalValues.insert(loc=0, column='x', value=mergeDataFrame["x"])
    return {'idealValue': finalValues, 'max': maxVal}

def testFunction(testValue, idealValue, f_):
    # merging test datasets and generated ideal functions tables
    mergeDataFrame = testValue.merge(idealValue, on=['x'], how='left')
    testTableValues['idealVal'] = None

# function to plot the graphs
def plotgraph(a, b, c, d): #dataframe Ideal, Training, Max deviation, Test
    # first graph with training function 
    graph_1 = figure(x_axis_label="x values", title="Training dataset function - 1")
    a1=a.x.to_list()
    b1=b.x.to_list()
    a_col1=a[a.columns[1]].to_list()
    b_col1=b[b.columns[1]].to_list()
    a_col2=a[a.columns[2]].to_list()
    b_col2=b[b.columns[2]].to_list()
    a_col3=a[a.columns[3]].to_list()
    b_col3=b[b.columns[3]].to_list()
    a_col4=a[a.columns[4]].to_list()
    b_col4=b[b.columns[4]].to_list()
    graph_1.circle(a1, a_col1, color='cyan',size=15, legend_label='  Ideal Function - "'+ a.columns[1] +'"')
    graph_1.line(b1,b_col1, color='olive', legend_label='  Training Function - "'+ b.columns[1]+'"')
    # training function 2 graph
    graph_2 = figure(x_axis_label="x values", title="Training dataset function - 2")
    graph_2.circle(a1,a_col2, color='yellow', size=15, legend_label='  Ideal Function - "'+  a.columns[2]+'"')
    graph_2.line(b1,b_col2, color='red', legend_label='  Training Function - "'+  b.columns[2]+'"')
    # training function 3 graph
    graph_3 = figure(x_axis_label="x values", title="Training dataset function - 3")
    graph_3.circle(a1, a_col3, color='pink', size=15, legend_label='  Ideal Function - "' +  a.columns[3]+'"')
    graph_3.line(b1, b_col3,color='blue', legend_label='  Training Function - "'+ b.columns[3]+'"')
    # training function 4 graph
    graph_4 = figure(x_axis_label="x values",title="Training dataset function - 4")
    graph_4.circle(a1, a_col4, color='orange', size=15, legend_label='  Ideal Function - "'+  a.columns[4]+'"')
    graph_4.line(b1, b_col4, color='red', legend_label='  Training Function - "'+ b.columns[4]+'"')

    # For printing the graphs
    show(gridplot([[graph_1], [graph_2], [graph_3], [graph_4]], width=1000, height=600))
if __name__ == "__main__":
    connectSQLite = SQLLiteUtils(conn_string=connectToString)

    # Table 1: The training data
    testTableValues = pd.read_csv("Data_Tables/test.csv")
    trainTableValues = pd.read_csv("Data_Tables/train.csv")
    idealTableValues = pd.read_csv("Data_Tables/ideal.csv")
    connectSQLite.put_df(df=trainTableValues, conn_string=connectToString, table='train')
    # Table 2: The ideal data
    connectSQLite.put_df(df=idealTableValues, conn_string=connectToString, table='ideal')
    # Table 3: The test data
    connectSQLite.put_df(df=testTableValues, conn_string=connectToString, table="test")
    # generated 4 ideal functions, maximum deviation and mapping test data
    functionData = idealFunction(trainTableValues, idealTableValues)
    testMap = testFunction(testTableValues, functionData["idealValue"], functionData["max"])

    # plotting graphs
    curdoc().theme = "dark_minimal"
    plotgraph(functionData["idealValue"], trainTableValues, functionData["max"], testMap)