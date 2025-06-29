import pandas as pd
from dash import dash_table, dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
import plotly.express as px
from dash import Input, Output

def create_customer_dashboard(server):
    # Load data
    df = pd.read_csv('data_dash.csv')

    # Dark theme layout
    dark_layout = dict(
        paper_bgcolor="#161A42",
        plot_bgcolor="#161A42",
        font=dict(color="#FFFFFF"),
        xaxis=dict(color="#FFFFFF", gridcolor="#2E335A"),
        yaxis=dict(color="#FFFFFF", gridcolor="#2E335A"),
        title=dict(font=dict(color="#FFFFFF")),
    )

    # Bootstrap & Font Awesome stylesheets
    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

    app = Dash(
        __name__,
        server=server,
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css],
        routes_pathname_prefix="/customer/"
    )



    # ------------- CARDS ---------------------

    # Dropdown filter card
    city_dropdown = dcc.Dropdown(
        id='city-filter',
        options=[{'label': city, 'value': city} for city in df['City'].unique()],
        placeholder='Select a City',
        multi=False,
        clearable=True,
        className='dbc'
    )

    dropdown_card = dbc.Card(
        dbc.CardBody([
            html.H6([
                html.I(className="fas fa-city me-2"),
                "Filter by City"
            ], style={"marginTop": "-20px"}, className="card-title text-white"),
            city_dropdown
        ]),
        className="card shadow-sm",
        style={"backgroundColor": "#161A42", "color": "white",
               "width": "95%", "height": "100px", "marginBottom": "20px"}
    )

    # Age slider filter card
    age_slider = dcc.RangeSlider(
        id='age-slider',
        min=df['Age'].min(),
        max=df['Age'].max(),
        step=1,
        value=[df['Age'].min(), df['Age'].max()],
        marks={i: str(i) for i in range(df['Age'].min(), df['Age'].max()+1, 5)},
        tooltip={"placement": "bottom", "always_visible": False},
        className='dbc'
    )

    age_card = dbc.Card(
        dbc.CardBody([
            html.H6([
                html.I(className="fas fa-user-clock me-2"),
                "Filter by Age"
            ], style={"marginTop": "-20px"}, className="card-title text-white mb-2"),
            age_slider
        ]),
        className="card shadow-sm",
        style={"backgroundColor": "#161A42", "color": "white", "width": "95%", "height": "100px",
                "marginTop": "-15px"}
    )

    # Graph cards with icons in titles
    def graph_card(graph_id, icon_class, title_text):
        return dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.I(className=f"fas {icon_class} text-info me-2", style={"fontSize": "0.9rem"}),
                    html.Span(title_text, className="fw-bold text-white", style={"fontSize": "0.95rem"})
                ], className="mb-2", style={"marginBottom": "4px", "marginTop": "-15px"}),
                dcc.Graph(id=graph_id, className="dbc", style={"marginTop": "-10px"})
            ]),
            className="card shadow-sm custom-card-height",
            style={"paddingTop": "10px", "paddingBottom": "0px"}
        )


    top_10_card = graph_card('top10-card', 'fas fa-user-tie', 'Top 10 Customers by Bank Deposit')
    loan_by_city_card = graph_card('loan_by_city', 'fa-building-columns', 'Total Bank Loans by City')
    avg_deposit_card = graph_card('avg_deposit', 'fa-coins', 'Average Bank Deposit by City')
    avg_saving_card = graph_card('avg_saving_id', 'fa-wallet', 'Average Saving Accounts by City')
    by_occ_card = graph_card('by_occ_id', 'fa-user-tie', 'Average Bank Deposit by Occupation')

    # ------------ LAYOUT ---------------

    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Col([
                    html.A(
                        html.Div(
                            [
                                html.I(className="fas fa-exchange-alt me-2"),
                                "Transactions"
                            ],
                            style={"display": "inline-flex", "alignItems": "center"}
                        ),
                        href="/transaction/",
                        className="transaction-link ms-4",
                    )
                ], width = 3),

                html.H4([
                    html.I(className="fas fa-chart-pie me-2"),
                    "Customer Dashboard"
                ], className="text-white fw-bold mb-4 ms-3"),
                age_card,
                dropdown_card
            ], width=3),

            dbc.Col(top_10_card, width=5),
            dbc.Col(loan_by_city_card, width=4)
        ], className="mb-1 gx-1"),

        dbc.Row([
            dbc.Col(avg_deposit_card, width=4),
            dbc.Col(avg_saving_card, width=4),
            dbc.Col(by_occ_card, width=4),
        ], className="mb-1 gx-1")

    ], fluid=True, style={"backgroundColor": "#0f112b"})

    # ------------ CALLBACK ---------------

    @app.callback(
        Output('top10-card', 'figure'),
        Output('loan_by_city', 'figure'),
        Output('avg_deposit', 'figure'),
        Output('avg_saving_id', 'figure'),
        Output('by_occ_id', 'figure'),
        Input('city-filter', 'value'),
        Input('age-slider', 'value')
    )
    def update_graphs(selected_city, age_range):
        filtered_df = df if not selected_city else df[df['City'] == selected_city]
        filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]

        # Top 10 Customers by Bank Deposit
        top10 = filtered_df[['Full name', 'Bank Deposit', 'Saving Accounts']].nlargest(10, ['Bank Deposit', 'Saving Accounts'])
        top_10_fig = px.bar(top10, x='Full name', y='Bank Deposit')
        top_10_fig.update_layout(dark_layout, height=247)
        top_10_fig.update_traces(marker_color="#00FFFF")

        # Total Bank Loans by City
        loan_by_city = filtered_df.groupby('City', as_index=False)['Bank Loans'].sum()
        loan_by_city_fig = px.bar(loan_by_city, x='City', y='Bank Loans')
        loan_by_city_fig.update_layout(dark_layout, height=247)
        loan_by_city_fig.update_traces(marker_color="#00FFFF")

        # Average Bank Deposit by City
        avg_deposit = filtered_df.groupby('City', as_index=False)['Bank Deposit'].mean()
        avg_deposit_fig = px.bar(avg_deposit, x='City', y='Bank Deposit')
        avg_deposit_fig.update_layout(dark_layout, height=247)
        avg_deposit_fig.update_traces(marker_color="#00FFFF")

        # Average Saving Accounts by City
        avg_saving = filtered_df.groupby('City', as_index=False)['Saving Accounts'].mean()
        avg_saving_fig = px.bar(avg_saving, x='City', y='Saving Accounts')
        avg_saving_fig.update_layout(dark_layout, height=247)
        avg_saving_fig.update_traces(marker_color="#00FFFF")

        # Average Bank Deposit by Occupation
        by_occ = filtered_df.groupby('Occupation', as_index=False)['Bank Deposit'].mean()
        by_occ_fig = px.bar(by_occ, x='Occupation', y='Bank Deposit')
        by_occ_fig.update_layout(dark_layout, height=247)
        by_occ_fig.update_traces(marker_color="#00FFFF")

        return top_10_fig, loan_by_city_fig, avg_deposit_fig, avg_saving_fig, by_occ_fig
    return app

