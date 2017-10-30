from plotly import plotly
from plotly.graph_objs import Scatter, Bar, Layout, Data, Figure


def generate_time_estimates_plot(data_frame, xrange=None):
    trace0 = Scatter(
        x=data_frame.index.tolist(),
        y=data_frame['time_spent'],
        mode='markers',
        name='Time Spent'
    )
    trace1 = Scatter(
        x=data_frame.index.tolist(),
        y=data_frame['original_estimate'],
        mode='markers',
        name='Original Estimate'
    )
    trace2 = Bar(
        x=data_frame.index.tolist(),
        y=data_frame['original_estimate'] - data_frame['time_spent'],
        name='Difference'
    )
    data = Data([trace0, trace1, trace2])
    layout = Layout(
        title='Time Estimate Accuracy',
        xaxis=dict(
            title='Issue Number',
            range=xrange
        ),
        yaxis=dict(
            title='Time (s)'
        ),
    )
    figure = Figure(data=data, layout=layout)
    plotly.plot(figure, filename='test')
