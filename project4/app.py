import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load dataset
df = pd.read_csv('/kaggle/input/sleep-health-and-lifestyle-dataset/Sleep_health_and_lifestyle_dataset.csv')

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Interactive Sleep & Lifestyle Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Interactive Sleep & Lifestyle Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("Filter by Stress Level:"),
        dcc.Dropdown(
            id='stress-filter',
            options=[{'label': level, 'value': level} for level in sorted(df['Stress Level'].unique())],
            value=[],
            multi=True,
            placeholder="Select Stress Levels"
        ),
    ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        html.Label("Filter by Physical Activity Level:"),
        dcc.Dropdown(
            id='activity-filter',
            options=[{'label': level, 'value': level} for level in sorted(df['Physical Activity Level'].unique())],
            value=[],
            multi=True,
            placeholder="Select Activity Levels"
        ),
    ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

    # Plot 1: Distribution of Sleep Duration
    dcc.Graph(id='plot1'),

    # Plot 2: Sleep Duration by Stress Level
    dcc.Graph(id='plot2'),

    # Plot 3: Quality of Sleep by Sleep Duration
    dcc.Graph(id='plot3'),

    # Plot 4: Quality of Sleep by Physical Activity Level
    dcc.Graph(id='plot4'),

    # Plot 5: Comprehensive Overview
    dcc.Graph(id='plot5')
])

# Callbacks
@app.callback(
    [
        Output('plot1', 'figure'),
        Output('plot2', 'figure'),
        Output('plot3', 'figure'),
        Output('plot4', 'figure'),
        Output('plot5', 'figure')
    ],
    [
        Input('stress-filter', 'value'),
        Input('activity-filter', 'value')
    ]
)
def update_plots(selected_stress, selected_activity):
    # Apply filters
    filtered_df = df.copy()
    if selected_stress:
        filtered_df = filtered_df[filtered_df['Stress Level'].isin(selected_stress)]
    if selected_activity:
        filtered_df = filtered_df[filtered_df['Physical Activity Level'].isin(selected_activity)]

    # Plot 1: Distribution of Sleep Duration
    fig1 = px.histogram(
        filtered_df,
        x='Sleep Duration',
        nbins=20,
        marginal='box',
        title="Distribution of Sleep Duration",
        labels={'Sleep Duration': 'Sleep Duration (hours)'}
    )

    fig1.update_layout(bargap=0.3) 

    # Plot 2: Sleep Duration by Stress Level
    fig2 = px.box(
        filtered_df,
        x='Stress Level',
        y='Sleep Duration',
        color='Stress Level',
        title="Sleep Duration by Stress Level",
        points='all'
    )

    # Plot 3: Quality of Sleep by Sleep Duration
    fig3 = px.scatter(
        filtered_df,
        x='Sleep Duration',
        y='Quality of Sleep',
        trendline='ols',
        title="Quality of Sleep by Sleep Duration",
        labels={'Sleep Duration': 'Sleep Duration (hours)', 'Quality of Sleep': 'Quality of Sleep'}
    )

    # Plot 4: Quality of Sleep by Physical Activity Level
    fig4 = px.box(
        filtered_df,
        x='Physical Activity Level',
        y='Quality of Sleep',
        color='Physical Activity Level',
        title="Quality of Sleep by Physical Activity Level",
        points='all'
    )

    # Plot 5: Comprehensive Overview
    fig5 = px.scatter(
        filtered_df,
        x='Sleep Duration',
        y='Quality of Sleep',
        color='Physical Activity Level',
        size='Stress Level',
        hover_data=['Sleep Duration', 'Quality of Sleep', 'Stress Level', 'Physical Activity Level'],
        title="Quality of Sleep vs Sleep Duration (Stress size, Activity hue)"
    )

    return fig1, fig2, fig3, fig4, fig5

# Run server
if __name__ == '__main__':
    app.run_server(debug=True)
