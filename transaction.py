import pandas as pd
from dash import dash_table, dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
import plotly.express as px
from dash import Input, Output
import plotly.graph_objects as go


def create_trans_dashboard(server):

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
        routes_pathname_prefix="/transaction/"
    )

    # ------------- CARDS ---------------------

    # Dropdown filter card
    radio_gender = dcc.RadioItems(
        id = 'gender-filter',
        options=[{'label': 'All', 'value':'All'}] +
                 [{'label':g, 'value':g} for g in df['Sex'].unique()],
        value= 'All',
        inline= True,
        labelStyle= {"margin-right": '15px'}
    )

    radio_card = dbc.Card(
        dbc.CardBody([
            html.H6([
                html.I(className="fa fa-venus-mars me-2"),
                "Filter by Gender"
            ], style={"marginTop": "-20px"}, className="card-title text-white"),
            radio_gender
        ]),
        className="card shadow-sm",
        style={"backgroundColor": "#161A42", "color": "white",
               "width": "95%", "height": "100px", "marginTop": "10px", "marginLeft": "-10px"},
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
        style={"backgroundColor": "#161A42", "color": "white", "width": "100%", "height": "100px",
                "marginTop": "10px"}
    )
    medium_filter = dcc.Dropdown(
        id='medium-filter',
        options=[{'label': m, 'value': m} for m in df['Transaction Medium'].unique()],
        value=[],
        multi=True,
        clearable=False,
        placeholder="Select Medium(s)…",
        style={
            "backgroundColor": "#161A42",  # input box background
            "color": "white",              # selected text color
            "border": "1px solid white",   # border around input
        },
        className="bg-dark text-white",          # applies to the control
        #dropdownClassName="bg-dark text-white",  # applies to the options menu
    )


    medium_card = dbc.Card(
        dbc.CardBody([
            html.H6([
                html.I(className="fa fa-credit-card me-2"),
                "Filter by Medium"
            ], style={"marginTop": "-20px"}, className="card-title text-white"),
            medium_filter
        ]),
        className="card shadow-sm",
        style={"backgroundColor": "#161A42", "color": "white",
               "width": "95%", "height": "100px", "marginTop": "10px"}
    )

    # 1. Build the pivot DataFrame
    pivot_df = pd.pivot_table(
        data=df,
        index='Account officer',
        columns='Account Type',
        values='Customer_id',
        aggfunc='count',
        fill_value=0,
        margins=True,
        margins_name='Total Account Manage'
    ).reset_index()

    # 2. Create the paginated, sortable, filterable DataTable
    pivot_table = dash_table.DataTable(
        id='pivot-table',
        columns=[{"name": col, "id": col} for col in pivot_df.columns],
        data=pivot_df.to_dict('records'),
        page_action="native",       # enable client-side pagination
        page_size=10,               # rows per page
        sort_action="native",       # enable column sorting
        filter_action="native",     # enable column filtering
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": "#161A42",
            "color": "#FFFFFF",
            "fontWeight": "bold",
        },
        style_cell={
            "backgroundColor": "#0f112b",
            "color": "#FFFFFF",
            "textAlign": "center",
            "padding": "4px",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#161A42",
            }
        ],
    )

    # 3. Wrap it in a dark-themed Card
    # Wrap it in a dark-themed Card
    pivot_card = dbc.Card(
        dbc.CardBody([
            html.H5(
                [
                    html.I(className="fas fa-user-tie me-2", style={"fontSize": "1.5rem"}),  # tie icon, bigger
                    "Accounts Managed by Officer"
                ],
                className="text-white mb-3",
                style={
                    #"fontSize": "1.75rem",    # make the text bigger
                    "fontWeight": "700"       # bold
                }
            ),
            pivot_table
        ]),
        className="shadow-sm pivot_table-card-height ms-0",
        style={"backgroundColor": "#161A42"}
    )



    # Graph cards with icons in titles
    def graph_card(graph_id, icon_class, title_text):
        return dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.I(className=f"fas {icon_class} text-info me-2", style={"fontSize": "0.9rem"}),
                    html.Span(title_text, className="fw-bold text-white", style={"fontSize": "0.95rem"})
                ], className="mb-2", style={"marginBottom": "4px", "marginTop": "-15px"}),
                dcc.Graph(id=graph_id, className="dbc", style={"marginTop": "-77px", "marginLeft":"-40px"})
            ]),
            className="card shadow-sm custom2-card-height ms-3",
            style={"paddingTop": "10px", "paddingBottom": "0px"}
        )


    trans_amt_card = graph_card('trans_amt_id',  'fa-coins', 'Total Transaction Amount')
    hour_amt_card = graph_card('hour_amt_id', 'fa-clock',  'Amount by Transaction Hour')
    daily_amount_card = graph_card('daily_amt_id', 'fa-calendar-alt', 'Total Transaction Amount per Day')
    savings_vs_deposits_card = graph_card('savings_vs_deposits_id', 'fa-chart-scatter', 'Total savings vs deposits')

    # ------------ LAYOUT ---------------
    app.layout = dbc.Container(
        [
            # first row: link + title, then three filter cards
            dbc.Row(
                [
                    dbc.Col(
                        [
                    html.A(
                        html.Div(
                            [
                                html.I(className="fas fa-exchange-alt me-2"),
                                "Customer"
                            ],
                            style={"display": "inline-flex", "alignItems": "center"}
                        ),
                        href="/customer/",
                        className="transaction-link ms-4",
                    ),
                            html.H4(
                                [
                                    html.I(className="fas fa-chart-pie me-2"),
                                    "Transaction Dashboard"
                                ],
                                className="text-white fw-bold ms-4 mt-1", style = {"font-size":"22px"}
                            ),
                        ],
                        width=3,
                        className="px-1"
                    ),

                    dbc.Col(age_card,    width=3, className="px-1"),
                    dbc.Col(medium_card, width=3, className="px-1"),
                    dbc.Col(radio_card,  width=3, className="px-1"),
                ],
                className="gx-1 mb-4"
            ),

            # second row: your graph cards
            dbc.Row(
                [
                    dbc.Col(
                        [
                            daily_amount_card,
                            hour_amt_card,
                        ],
                        width=4,
                        className="px-0",
                        style = {"marginTop": "-30px"}
                    ),

                    dbc.Col(pivot_card, width=4, className="px-0",
                            style = {"marginTop": "-30px", "marginLeft": "0px"}),

                    dbc.Col(
                        [
                            trans_amt_card,
                            savings_vs_deposits_card,
                        ],
                        width=4,
                        className="px-0", style = {"marginTop": "-30px", "marginLeft": "-15px"}
                    ),
                ],
                className="gx-1"
            )
        ],
        fluid=True,
        style={"backgroundColor": "#0f112b"},
    )




    # ------------ CALLBACK ---------------

    @app.callback(
        Output('trans_amt_id', 'figure'),
        Output('hour_amt_id', 'figure'),
        Output('daily_amt_id', 'figure'),
        Output('savings_vs_deposits_id', 'figure'),
        Input('gender-filter', 'value'),
        Input('age-slider', 'value'),
        Input('medium-filter', 'value'),
    )
    def update_graphs(selected_sex, age_range, selected_medium):

        filtered_df = df if selected_sex == 'All' else df[df['Sex'] == selected_sex]
        filtered_df = filtered_df[(filtered_df['Age'] >= age_range[0]) & (filtered_df['Age'] <= age_range[1])]
        if selected_medium:
            # Checklist.value is a list, so we use isin()
            filtered_df = filtered_df[filtered_df['Transaction Medium'].isin(selected_medium)]
        # Group data
        filtered_df.rename(columns = {
            "Transaction Medium": "Medium",
            "Transaction type": "Type"
        }, inplace=True)
        medium_data = filtered_df.groupby('Medium')['Amount'].sum()
        type_data = filtered_df.groupby('Type')['Amount'].sum()


        # Create a single figure with both bar traces
        trans_fig = go.Figure()

        # Bar for Transaction Medium
        trans_fig.add_trace(go.Bar(
            x=medium_data.index,
            y=medium_data.values,
            name='Medium',
            marker_color='cyan'
        ))

        # Bar for Transaction Type
        trans_fig.add_trace(go.Bar(
            x=type_data.index,
            y=type_data.values,
            name='Type',
            marker_color='gold'
        ))

        # Update layout
        trans_fig.update_layout(
            dark_layout,
            #title='Total Transaction Amounts',
            #xaxis_title='Category',

            yaxis_title='Total Amount',
            barmode='group',  # places bars side by side
            width=450,
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        # 1. Bar chart: Amount by Transaction Hour
        hour_amount_fig = px.bar(
            filtered_df.groupby('Transaction Hour', as_index=False)['Amount'].sum(),
            x='Transaction Hour',
            y='Amount',
            #title='Amount by Transaction Hour',
            width=450,
            height=300,
        )
        hour_amount_fig.update_layout(
            dark_layout,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        hour_amount_fig.update_traces(marker_color="#00FFFF")

        # 2. Line chart: Total Transaction Amount per Day
        daily_amount_fig = px.line(
        filtered_df.groupby('Date_of_transaction', as_index=False)['Amount'].sum(),
        x='Date_of_transaction',
        y='Amount',
        #title='Total Transaction Amount per Day',
        width=450,
        height=300,
        )
        daily_amount_fig.update_layout(
            dark_layout,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        daily_amount_fig.update_traces(line_color="#00FFFF")

        # 4. Scatter plot: Savings vs Deposits
        savings_vs_deposits_fig = px.scatter(
            filtered_df,
            x='Bank Deposit',
            y='Saving Accounts',
            #title='Savings vs Deposits',
            width=450,
            height=300,

        )
        savings_vs_deposits_fig.update_layout(
            dark_layout,
            xaxis_title='Bank Deposit',
            yaxis_title='Saving Accounts',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        savings_vs_deposits_fig.update_traces(marker_color="#00FFFF")

        return trans_fig, hour_amount_fig, daily_amount_fig, savings_vs_deposits_fig
    return app



