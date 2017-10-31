from plotly import plotly
from plotly.graph_objs import Scatter, Bar, Layout, Data, Figure


def time_estimates_plot(data_frame, xrange=None):
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


def bugs_open_by_sprint(data_frame, xrange=None):
    bugs_tally, sprint_list = _tally_bugs_by_sprint(data_frame)
    trace0 = Bar(
        x=sprint_list,
        y=[bugs_tally[sprint] for sprint in sprint_list],
        name='Total Bugs'
    )

    data = Data([trace0])
    layout = Layout(
        title='Bugs Open by Sprint',
        xaxis=dict(
            title='Sprint',
            range=xrange,
        ),
        yaxis=dict(
            title='Number of Bugs'
        ),
    )
    figure = Figure(data=data, layout=layout)
    plotly.plot(figure=figure, filename='test')


def _tally_bugs_by_sprint(data_frame):
    tally = {}
    sprint_list = []
    for i, row in data_frame.iterrows():
        sprints = row['sprints'].split(',') if row['sprints'] else None
        sprint_list.extend(sprints)
        if row['issue_type'] == 'Bug' and sprints:
            tally.update({sprint: tally.setdefault(sprint, 0) + 1 for sprint in sprints})

    return tally, sprint_list
