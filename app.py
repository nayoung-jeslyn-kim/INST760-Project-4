import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

# ------------------------------
# Load dataset
# ------------------------------
df = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
df.columns = df.columns.str.strip()
df['Sample ID'] = range(1, len(df) + 1)

# ------------------------------
# Dash App
# ------------------------------
app = dash.Dash(__name__)
app.title = "Unified Sleep & Lifestyle Dashboard"

# Card style for clean layout
card_style = {
    'backgroundColor': 'white',
    'padding': '20px',
    'borderRadius': '12px',
    'boxShadow': '0px 2px 6px rgba(0,0,0,0.08)',
    'marginBottom': '25px'
}

# ------------------------------
# Layout
# ------------------------------
app.layout = html.Div([
    html.H1("Sleep & Lifestyle Interactive Story Dashboard",
            style={
                'textAlign': 'center',
                'marginBottom': '30px',
                'marginTop': '10px',
                'fontFamily': 'Inter, sans-serif'
            }),

    # ---------------------- FILTER BAR ----------------------
    html.Div([
        html.Div([
            html.Label("Sleep Duration Filter", style={'fontWeight': '600'}),
            dcc.RangeSlider(
                id='sleep-filter',
                min=df['Sleep Duration'].min(),
                max=df['Sleep Duration'].max(),
                value=[df['Sleep Duration'].min(), df['Sleep Duration'].max()],
                step=0.5,
                marks={i: str(i) for i in range(
                    int(df['Sleep Duration'].min()),
                    int(df['Sleep Duration'].max()) + 1)}
            )
        ], style={'marginBottom': '20px'}),

        html.Div([
            html.Div([
                html.Label("Stress Level Filter", style={'fontWeight': '600'}),
                dcc.Dropdown(
                    id='stress-filter',
                    options=[{'label': s, 'value': s} for s in sorted(df['Stress Level'].unique())],
                    multi=True,
                    placeholder="Select stress levels",
                )
            ], style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                html.Label("Activity Level Filter", style={'fontWeight': '600'}),
                dcc.Dropdown(
                    id='activity-filter',
                    options=[{'label': a, 'value': a} for a in sorted(df['Physical Activity Level'].unique())],
                    multi=True,
                    placeholder="Select activity levels"
                )
            ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'}),
        ])
    ], style={**card_style}),

    # ---------------------- PLOT GRID ----------------------
    html.Div([
        html.Div(dcc.Graph(id='plot-overview'),
                 style={**card_style, 'width': '49%', 'display': 'inline-block'}),

        html.Div(dcc.Graph(id='plot-stress'),
                 style={**card_style, 'width': '49%', 'display': 'inline-block', 'marginLeft': '2%'}),

        html.Div(dcc.Graph(id='plot-activity'),
                 style={**card_style, 'width': '49%', 'display': 'inline-block'}),

        html.Div(dcc.Graph(id='plot-comprehensive'),
                 style={**card_style, 'width': '49%', 'display': 'inline-block', 'marginLeft': '2%'}),
    ])
], style={
    'maxWidth': '1300px',
    'margin': '0 auto',
    'padding': '20px',
    'fontFamily': 'Inter, sans-serif'
})


# ------------------------------
# Helper
# ------------------------------
def filter_df(df, stress=None, activity=None, sleep_range=None):
    filtered = df.copy()
    if sleep_range:
        filtered = filtered[
            (filtered['Sleep Duration'] >= sleep_range[0]) &
            (filtered['Sleep Duration'] <= sleep_range[1])
        ]
    if stress:
        filtered = filtered[filtered['Stress Level'].isin(stress)]
    if activity:
        filtered = filtered[filtered['Physical Activity Level'].isin(activity)]
    return filtered


# ------------------------------
# Callback for ALL PLOTS
# ------------------------------
@app.callback(
    [
        Output('plot-overview', 'figure'),
        Output('plot-stress', 'figure'),
        Output('plot-activity', 'figure'),
        Output('plot-comprehensive', 'figure'),
    ],
    [
        Input('sleep-filter', 'value'),
        Input('stress-filter', 'value'),
        Input('activity-filter', 'value'),
    ]
)
def update_all_plots(sleep_range, selected_stress, selected_activity):

    filtered = filter_df(df, sleep_range=sleep_range,
                         stress=selected_stress,
                         activity=selected_activity)

    # -------------------- Plot 1: Overview Histogram --------------------
    fig1 = px.histogram(
        filtered, x='Sleep Duration', nbins=20,
        title='Sleep Duration Distribution',
        hover_data=['Quality of Sleep']
    )
    fig1.update_layout(bargap=0.25, template='simple_white')

    # -------------------- Plot 2: Stress Scatter --------------------
    fig2 = px.scatter(
        filtered, x='Sleep Duration', y='Quality of Sleep',
        color='Stress Level', size='Stress Level',
        title='Sleep vs Quality by Stress Level',
        hover_data=['Physical Activity Level']
    )
    fig2.update_layout(template='simple_white')

    # -------------------- Plot 3: Activity — Box Plot (NEW) --------------------
    fig3 = px.box(
        filtered,
        x='Physical Activity Level',
        y='Sleep Duration',
        color='Physical Activity Level',
        title='Sleep Duration Distribution by Physical Activity Level',
        points='all'
    )
    fig3.update_layout(template='simple_white')

    # -------------------- Plot 4: Comprehensive — Density Heatmap (NEW) --------------------
    fig4 = px.density_heatmap(
        filtered,
        x='Sleep Duration',
        y='Quality of Sleep',
        z=None,
        histfunc='count',
        color_continuous_scale='Viridis',
        title='Comprehensive Density Heatmap: Sleep vs Quality'
    )
    fig4.update_layout(template='simple_white')

    return fig1, fig2, fig3, fig4


# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
