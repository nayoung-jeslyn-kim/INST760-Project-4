import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

# ------------------------------
# Load dataset
# ------------------------------
df = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
df.columns = df.columns.str.strip()

# For animation demo, create a pseudo time variable
df['Sample ID'] = range(1, len(df)+1)

# ------------------------------
# Initialize Dash app
# ------------------------------
app = dash.Dash(__name__)
server = app.server 

app.title = "Interactive Sleep & Lifestyle Story Dashboard"

# ------------------------------
# Layout
# ------------------------------
app.layout = html.Div([
    html.H1("Sleep & Lifestyle Interactive Story Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    dcc.Tabs([
        dcc.Tab(label='Overview', children=[
            html.Div([
                html.H3("Filter by Sleep Duration:"),
                dcc.RangeSlider(
                    id='sleep-slider',
                    min=df['Sleep Duration'].min(),
                    max=df['Sleep Duration'].max(),
                    step=0.5,
                    value=[df['Sleep Duration'].min(), df['Sleep Duration'].max()],
                    marks={i: str(i) for i in range(int(df['Sleep Duration'].min()), int(df['Sleep Duration'].max())+1)}
                )
            ], style={'padding': '20px'}),
            html.Div(dcc.Graph(id='overview-plot'))
        ]),
        
        dcc.Tab(label='Stress Analysis', children=[
            html.Div([
                html.Label("Select Stress Levels:"),
                dcc.Checklist(
                    id='stress-checklist',
                    options=[{'label': level, 'value': level} for level in sorted(df['Stress Level'].unique())],
                    value=[],
                    inline=True
                )
            ], style={'padding': '10px'}),
            html.Div(dcc.Graph(id='stress-plot'))
        ]),
        
        dcc.Tab(label='Activity Analysis', children=[
            html.Div([
                html.Label("Select Physical Activity Levels:"),
                dcc.Checklist(
                    id='activity-checklist',
                    options=[{'label': level, 'value': level} for level in sorted(df['Physical Activity Level'].unique())],
                    value=[],
                    inline=True
                )
            ], style={'padding': '10px'}),
            html.Div(dcc.Graph(id='activity-plot'))
        ]),
        
        dcc.Tab(label='Comprehensive Overview', children=[
            html.Div([
                html.Label("Stress Level Filter:"),
                dcc.Dropdown(
                    id='stress-dropdown',
                    options=[{'label': level, 'value': level} for level in sorted(df['Stress Level'].unique())],
                    value=[],
                    multi=True,
                    placeholder="Select Stress Levels"
                ),
                html.Label("Activity Level Filter:", style={'marginTop': '10px'}),
                dcc.Dropdown(
                    id='activity-dropdown',
                    options=[{'label': level, 'value': level} for level in sorted(df['Physical Activity Level'].unique())],
                    value=[],
                    multi=True,
                    placeholder="Select Activity Levels"
                )
            ], style={'width': '50%', 'padding': '20px'}),
            html.Div(dcc.Graph(id='comprehensive-plot'))
        ])
    ])
], style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '1200px', 'margin': '0 auto'})

# ------------------------------
# Helper function
# ------------------------------
def filter_df(df, stress=None, activity=None, sleep_range=None):
    filtered = df.copy()
    if stress:
        filtered = filtered[filtered['Stress Level'].isin(stress)]
    if activity:
        filtered = filtered[filtered['Physical Activity Level'].isin(activity)]
    if sleep_range:
        filtered = filtered[(filtered['Sleep Duration'] >= sleep_range[0]) & (filtered['Sleep Duration'] <= sleep_range[1])]
    return filtered

# ------------------------------
# Callbacks
# ------------------------------

# Overview Tab
@app.callback(
    Output('overview-plot', 'figure'),
    Input('sleep-slider', 'value')
)
def update_overview(sleep_range):
    filtered = filter_df(df, sleep_range=sleep_range)
    fig = px.histogram(
        filtered, x='Sleep Duration', nbins=20, marginal='box',
        title='Distribution of Sleep Duration', labels={'Sleep Duration': 'Sleep Duration (hours)'},
        hover_data=['Quality of Sleep']
    )
    fig.update_layout(bargap=0.3)
    fig.update_traces(marker_color='skyblue')
    return fig

# Stress Analysis Tab
@app.callback(
    Output('stress-plot', 'figure'),
    Input('stress-checklist', 'value')
)
def update_stress(selected_stress):
    filtered = filter_df(df, stress=selected_stress)
    fig = px.scatter(
        filtered, x='Sleep Duration', y='Quality of Sleep',
        color='Stress Level', size='Stress Level',
        trendline='ols',
        title='Sleep Duration vs Quality of Sleep by Stress Level',
        hover_data=['Physical Activity Level']
    )
    return fig

# Activity Analysis Tab
@app.callback(
    Output('activity-plot', 'figure'),
    Input('activity-checklist', 'value')
)
def update_activity(selected_activity):
    filtered = filter_df(df, activity=selected_activity)
    fig = px.scatter(
        filtered, x='Sleep Duration', y='Quality of Sleep',
        color='Physical Activity Level', size='Stress Level',
        animation_frame='Sample ID',
        title='Quality of Sleep vs Sleep Duration (Animated by Sample)',
        hover_data=['Stress Level']
    )
    return fig

# Comprehensive Overview Tab
@app.callback(
    Output('comprehensive-plot', 'figure'),
    [Input('stress-dropdown', 'value'),
     Input('activity-dropdown', 'value')]
)
def update_comprehensive(selected_stress, selected_activity):
    filtered = filter_df(df, stress=selected_stress, activity=selected_activity)
    fig = px.scatter(
        filtered, x='Sleep Duration', y='Quality of Sleep',
        color='Physical Activity Level', size='Stress Level',
        hover_data=['Sleep Duration','Quality of Sleep','Stress Level','Physical Activity Level'],
        trendline='ols',
        animation_frame='Sample ID',
        title='Comprehensive Overview: Sleep Duration vs Quality of Sleep'
    )
    fig.update_layout(legend_title_text='Physical Activity Level')
    return fig

# ------------------------------
# Local Run
# ------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
