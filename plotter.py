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
    plotly.plot(figure, filename='test')


def _tally_bugs_by_sprint(data_frame):
    tally = {}
    sprint_list = []
    for i, row in data_frame.iterrows():
        sprints = row['sprints'].split(',') if row['sprints'] else None
        if sprints:
            for sprint in sprints:
                if sprint not in sprint_list:
                    sprint_list.append(sprint)
        if row['issue_type'] == 'Bug' and sprints:
            tally.update({sprint: tally.setdefault(sprint, 0) + 1 for sprint in sprints})

    return tally, sprint_list


def calc_average_time_est_error(data_frame):
    """
    Calculates average time estimation error.
    :param data_frame:
    :return:
    """
    # TODO: Refactor me. I am a mess.
    overestimated_count = 0
    underestimated_count = 0
    spot_on = 0
    total_diff = 0
    time_tracked_issues = 0
    for i, row in data_frame.iterrows():
        original_estimate = row['original_estimate'] if pd.notnull(row['original_estimate']) else None
        time_spent = row['time_spent'] if pd.notnull(row['time_spent']) else None
        if original_estimate and time_spent:
            if original_estimate < time_spent:
                underestimated_count += 1
            elif original_estimate > time_spent:
                overestimated_count += 1
            else:
                spot_on += 1
            time_tracked_issues += 1
            diff = original_estimate - time_spent
            total_diff += diff
    average_estimate = round(data_frame['original_estimate'].mean() / 60, 2)
    average_actual = round(data_frame['time_spent'].mean() / 60, 2)
    average_diff = round(total_diff / (time_tracked_issues * 60), 2)
    print('Overestimated issues: {}'.format(overestimated_count))
    print('Underestimated issues: {}'.format(underestimated_count))
    print('Spot on: {}'.format(spot_on))
    print('Total time tracked issues: {}'.format(time_tracked_issues))
    print('Average etimate: {}m'.format(average_estimate))
    print('Average actual: {}m'.format(average_actual))
    print('Average estimate off by {}m.'.format(average_diff))
