import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
import base64
import datetime
import requests
import pathlib
import math
import pandas as pd
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import io
from dash.dependencies import Input, Output, State
from plotly import tools
import dash_table
from dash.exceptions import PreventUpdate
import collections
import plotly.express as px
from plotly.validators.scatter.marker import SymbolValidator


external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(
    suppress_callback_exceptions=True,
)


app.css.append_css({"external_url": external_stylesheets})

##########################################Charts########################################################################


def scatter_symbols():
    raw_symbols = SymbolValidator().values
    namestems = []
    namevariants = []
    symbols = []
    for i in range(0, len(raw_symbols), 3):
        name = raw_symbols[i + 2]
        symbols.append(raw_symbols[i])
        namestems.append(name.replace("-open", "").replace("-dot", ""))
        namevariants.append(name[len(namestems[-1]) :])
    symbols = [name + variant for name, variant in zip(namestems, namevariants)]
    return [dict(zip(("label", "value"), symbol)) for symbol in zip(symbols, symbols)]


def default_graph(df, xaxis_column_name, yaxis_column_name, marker_size, marker_style, color, opacity, marker_border_width, marker_border_color):
    fig = go.Figure()
    for y in yaxis_column_name:
        fig.add_trace(
            go.Scatter(
                x=df[xaxis_column_name[0]],
                y=df[y],
                mode="markers",
                marker=dict(
                    color=color,
                    size=marker_size,
                    opacity=opacity,
                    line=dict(width=marker_border_width,
                              color=marker_border_color

                    )
                ),
                name=y,
               # marker_size=marker_size,
                marker_symbol=marker_style,
            )
        )
    return fig


def line_chart(
    df,
    xaxis_column_name,
    yaxis_column_name,
):
    fig = go.Figure()
    for y in yaxis_column_name:
        fig.add_trace(
            go.Scatter(x=df[xaxis_column_name[0]], y=df[y], mode="lines", name=y)
        )
    return fig


def bar_chart(
    df,
    xaxis_column_name,
    yaxis_column_name,
):
    fig = go.Figure()
    for y in yaxis_column_name:
        fig.add_trace(go.Bar(x=df[xaxis_column_name[0]], y=df[y], name=y))
    return fig


def area_chart(
    df,
    xaxis_column_name,
    yaxis_column_name,
):
    fig = go.Figure()
    for y in yaxis_column_name:
        fig.add_trace(
            go.Scatter(x=df[xaxis_column_name[0]], y=df[y], name=y, fill="tozeroy")
        )
    return fig


def box_plot(
    df,
    xaxis_column_name,
    yaxis_column_name,
):
    fig = go.Figure()
    for i in yaxis_column_name:
        if len(xaxis_column_name) > 0:
            for y in yaxis_column_name:
                fig.add_trace(go.Box(x=df[xaxis_column_name[0]], y=df[y], name=y))
        else:
            for y in yaxis_column_name:
                fig.add_trace(go.Box(y=df[y], name=y))
    return fig


def default_layout(fig):
    fig.update_layout(
        template="ggplot2",
    )
    fig.update_layout(plot_bgcolor="white")
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=True,
        showgrid=True,
        gridwidth=1,
        gridcolor="#F4F4F4",
    )
    fig.update_xaxes(
        showline=True, linewidth=1, linecolor="black", mirror=True, showgrid=False
    )


########################################################################################################################

########################################################################################################################


df = pd.DataFrame()
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "2rem 1rem",
    "background-color": "#3B4873",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 62.5,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0.5rem 1rem",
    "background-color": "#1d1b31",
}

#################### Navbar#################################################################################
navbar_ = html.Div(
    [
        dbc.NavbarSimple(
            children=[
                dbc.Button(
                    "Sidebar", outline=True, color="secondary", id="btn_sidebar_"
                ),
                dbc.NavItem(dbc.NavLink("Page 1", href="#")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("More pages", header=True),
                        dbc.DropdownMenuItem("Page 2", href="#"),
                        dbc.DropdownMenuItem("Page 3", href="#"),
                    ],
                    nav=True,
                    in_navbar=True,
                    # label="More",
                ),
            ],
        )
    ],
    className="topnav",
)

navbar = html.Div(
    [
        html.A(
            "Tutorial",
            href="/tutorial",
        ),
        html.A(
            "Guidelines",
            href="/guidelines",
        ),
        html.A("Home", href="/", className="active"),
    ],
    className="topnav",
)

SIDEBAR_STYLE = {
    "position": "absolute",
    "top": 60,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "height": "1080px",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0.5rem 1rem",
    "background-color": "#1d1b31",
}

SIDEBAR_STYLE_ = {
    "position": "absolute",
    "top": 5,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "height": "1080px",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0.5rem 1rem",
    "background-color": "#1d1b31",
}
SIDEBAR_STYLE_2 = {
    "position": "absolute",
    "left": "-16rem",
    "top": 5,
    "bottom": 0,
    "width": "20rem",
    "height": "1080px",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0.5rem 1rem",
    "background-color": "#1d1b31",
}

primary_graph_style = {
    "color": "white",
    "position": "relative",
    "margin-left": "70px",
    "display": "block",
}
graph_options_1_style = {"padding-top": "5px", "display": "block"}
graph_options_2_style = {"padding-top": "5px", "display": "block"}
graph_options_3_style = {
    "padding-top": "5px",
    "display": "block",
    "position": "relative",
}
normal_side = {"top": 53, "position": "absolute", "height": "1000"}

sidebar_ = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Nav(
                        [
                            html.Ul(
                                children=[
                                    html.Li(
                                        [
                                            html.Div(
                                                children=[
                                                    html.I(
                                                        className="bx bx-collection"
                                                    ),
                                                    html.Span(
                                                        children=[
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        html.Button(
                                                                            dbc.Row(
                                                                                [
                                                                                    dbc.Col(
                                                                                        html.Div(
                                                                                            children=[
                                                                                                html.Img(
                                                                                                    src="/assets/icons/house-fill.svg",
                                                                                                    height="20px",
                                                                                                    className="center",
                                                                                                ),
                                                                                                html.A(
                                                                                                    "Main",
                                                                                                    style={
                                                                                                        "color": "white"
                                                                                                    },
                                                                                                ),
                                                                                            ]
                                                                                        ),
                                                                                    ),
                                                                                ],
                                                                                align="center",
                                                                                no_gutters=True,
                                                                            ),
                                                                            className="iocn-link",
                                                                            id="btn_sidebar",
                                                                        ),
                                                                    ),
                                                                ]
                                                            ),
                                                        ],
                                                        className="link_name",
                                                    ),
                                                ],
                                                className="iocn-link",
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        html.Div(
                                            children=[
                                                html.I(className="bx bx-collection"),
                                                html.Span(
                                                    children=[
                                                        html.Button(
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        html.Div(
                                                                            children=[
                                                                                html.Img(
                                                                                    src="/assets/icons/file-earmark-font-fill.svg",
                                                                                    height="20px",
                                                                                    className="center",
                                                                                ),
                                                                                html.A(
                                                                                    "Text",
                                                                                    className="",
                                                                                    style={
                                                                                        "color": "white"
                                                                                    },
                                                                                ),
                                                                            ]
                                                                        )
                                                                    ),
                                                                ],
                                                                align="center",
                                                                no_gutters=True,
                                                            ),
                                                            className="iocn-link",
                                                            id="btn_sidebar_text",
                                                        )
                                                    ],
                                                    className="link_name",
                                                ),
                                            ],
                                            className="iocn-link",
                                            style={"padding-top": "15px"},
                                        )
                                    ),
                                    html.Li(
                                        html.Div(
                                            children=[
                                                html.I(className="bx bx-collection"),
                                                html.Span(
                                                    children=[
                                                        html.Button(
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        html.Div(
                                                                            children=[
                                                                                html.Img(
                                                                                    src="/assets/icons/question-square-fill.svg",
                                                                                    height="20px",
                                                                                    className="center",
                                                                                ),
                                                                                html.A(
                                                                                    "Text",
                                                                                    className="",
                                                                                    style={
                                                                                        "color": "white"
                                                                                    },
                                                                                ),
                                                                            ]
                                                                        )
                                                                    ),
                                                                ],
                                                                align="center",
                                                                no_gutters=True,
                                                            ),
                                                            className="iocn-link",
                                                            id="tutorial",
                                                        )
                                                    ],
                                                    className="link_name",
                                                ),
                                            ],
                                            className="iocn-link",
                                            style={"padding-top": "15px"},
                                        )
                                    ),
                                ],
                                className="nav-links",
                            ),
                        ],
                        className="sidebar close",
                        vertical=True,
                        pills=True,
                        id="sidebar",
                    ),
                ),
                dbc.Col(
                    [
                        html.Div(
                            dcc.Markdown("**Primary Graph Type**"),
                            id="main-title",
                            style={
                                "color": "white",
                                "position": "relative",
                                "margin-left": "70px",
                                "display": "block",
                            },
                        ),
                        html.Div(
                            children=[
                                html.Button(
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        children=[
                                                            html.Img(
                                                                src="/assets/icons/icons8-scatter-plot-64.png",
                                                                # height="64px",
                                                                className="center",
                                                            ),
                                                            html.A(
                                                                "Scatter",
                                                                className="",
                                                                style={
                                                                    "color": "white"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                            ),
                                        ],
                                        align="center",
                                        no_gutters=True,
                                    ),
                                    n_clicks=0,
                                    id="btn_sidebar_scatter",
                                    style={
                                        "position": "relative",
                                        "margin-left": "70px",
                                        "padding": "3px",
                                        "border": "none",
                                        "background": "white",
                                        "display": "inline",
                                    },
                                ),
                                html.Button(
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        children=[
                                                            html.Img(
                                                                src="/assets/icons/icons8-line-chart-64.png",
                                                                className="center",
                                                            ),
                                                            html.A(
                                                                "Line",
                                                                className="",
                                                                style={
                                                                    "color": "white"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                            ),
                                        ],
                                        align="center",
                                        no_gutters=True,
                                    ),
                                    id="btn_sidebar_lines",
                                    n_clicks=0,
                                    style={
                                        "position": "sticky",
                                        "margin-left": "40px",
                                        "padding": "3px",
                                        "border": "none",
                                        "background": "white",
                                        "display": "inline",
                                    },
                                ),
                            ],
                            id="graph-options-1",
                            style={
                                "padding-top": "5px",
                            },
                        ),
                        html.Div(
                            children=[
                                html.Button(
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        children=[
                                                            html.Img(
                                                                src="/assets/icons/icons8-bar-chart-64.png",
                                                                className="center",
                                                            ),
                                                            html.A(
                                                                "Bar",
                                                                className="",
                                                                style={
                                                                    "color": "white"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                            ),
                                        ],
                                        align="center",
                                        no_gutters=True,
                                    ),
                                    n_clicks=0,
                                    id="btn_sidebar_bar",
                                    style={
                                        "position": "relative",
                                        "margin-left": "70px",
                                        "padding": "3px",
                                        "border": "none",
                                        "background": "white",
                                        "display": "inline",
                                    },
                                ),
                                html.Button(
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        children=[
                                                            html.Img(
                                                                src="/assets/icons/boxplot.png",
                                                                height="30px",
                                                                width="15px",
                                                                className="center",
                                                            ),
                                                            html.A(
                                                                "Boxplot",
                                                                className="",
                                                                style={
                                                                    "color": "white"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                            ),
                                        ],
                                        align="center",
                                        no_gutters=True,
                                    ),
                                    id="btn_sidebar_box",
                                    style={
                                        "position": "sticky",
                                        "margin-left": "40px",
                                        "padding": "3px",
                                        "border": "none",
                                        "background": "white",
                                        "display": "inline",
                                    },
                                ),
                            ],
                            style={
                                "padding-top": "5px",
                            },
                            id="graph-options-2",
                        ),
                        html.Div(
                            children=[
                                html.Button(
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        children=[
                                                            html.Img(
                                                                src="/assets/icons/icons8-area-chart-64.png",
                                                                className="center",
                                                            ),
                                                            html.A(
                                                                "Area",
                                                                className="",
                                                                style={
                                                                    "color": "white"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                            ),
                                        ],
                                        align="center",
                                        no_gutters=True,
                                    ),
                                    id="btn_sidebar_area",
                                    style={
                                        "position": "relative",
                                        "margin-left": "70px",
                                        "padding": "3px",
                                        "border": "none",
                                        "background": "white",
                                        "display": "inline",
                                    },
                                ),
                                html.Button(
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        children=[
                                                            html.Img(
                                                                src="/assets/icons/icons8-foam-bubbles-64.png",
                                                                className="center",
                                                            ),
                                                            html.A(
                                                                "Bubble",
                                                                className="",
                                                                style={
                                                                    "color": "white"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                            ),
                                        ],
                                        align="center",
                                        no_gutters=True,
                                    ),
                                    id="btn_sidebar_bubble",
                                    style={
                                        "position": "sticky",
                                        "margin-left": "40px",
                                        "padding": "3px",
                                        "border": "none",
                                        "background": "white",
                                        "display": "inline",
                                    },
                                ),
                            ],
                            style={
                                "padding-top": "5px",
                            },
                            id="graph-options-3",
                        ),
                        html.Div(
                            dcc.Markdown("**Scatter Formatting**"),
                            id="main-title_2",
                            style={
                                "color": "white",
                                "position": "relative",
                                "margin-left": "70px",
                                "display": "block",
                                "padding-top": "5px",
                            },
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    "Marker Size:",
                                    id="btn_sidebar_area__",
                                    style={
                                        "position": "relative",
                                        "margin-left": "67px",
                                        "padding": "3px",
                                        "border": "none",
                                        "color": "white",
                                        "display": "inline",
                                        "size": "10",
                                    },
                                ),
                                dbc.Input(
                                    placeholder="5",
                                    bs_size="sm",
                                    value=5,
                                    id="marker_size",
                                    style={
                                        "position": "sticky",
                                        "margin-left": "3px",
                                        # "padding": "3px",
                                        "border": "none",
                                        "display": "inline",
                                        "width": "10%",
                                        "textAlign": "center",
                                    },
                                ),
                            ],
                            style={
                                "padding-top": "5px",
                            },
                            id="graph-options-4",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    "Marker Symbol:",
                                    style={
                                        "position": "relative",
                                        "margin-left": "67px",
                                        "top": "8px",
                                        "padding": "3px",
                                        "border": "none",
                                        "color": "white",
                                        "display": "inline",
                                        "size": "10",
                                    },
                                ),
                                html.Div(
                                    dcc.Dropdown(
                                        id="marker_style_dropdown",
                                        options=scatter_symbols(),
                                        value="circle",
                                        style={
                                            "width": "100px",
                                            "height": "8px",
                                            "vertical-align": "middle",
                                            "font-size": 10,
                                        },
                                    ),
                                    style={
                                        "position": "absolute",
                                        "margin-left": "5px",
                                        "margin-top": "3px",
                                        "background": "",
                                        "display": "inline",
                                    },
                                ),
                            ],
                            style={
                                "padding-top": "5px",
                            },
                            id="graph-options-5",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    "Marker Color:",
                                    style={
                                        "position": "relative",
                                        "margin-left": "67px",
                                        "top": "8px",
                                        "padding": "3px",
                                        "border": "none",
                                        "color": "white",
                                        "display": "inline",
                                        "size": "10",
                                    },
                                ),
                                html.Div(
                                    dbc.Input(
                                        type="color",
                                        id="colorpicker",
                                        value="#000000",
                                        style={"width": 20, "height": 20},
                                    ),
                                    style={
                                        "position": "absolute",
                                        "margin-left": "5px",
                                        "margin-top": "8px",
                                        "background": "",
                                        "display": "inline",
                                    },
                                ),
                            ],
                            style={
                                "padding-top": "20px",
                            },
                            id="graph-options-6",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    "Opacity:",
                                    style={
                                        "position": "relative",
                                        "margin-left": "67px",
                                        "top": "8px",
                                        "padding": "3px",
                                        "border": "none",
                                        "color": "white",
                                        "display": "inline",
                                        "size": "10",
                                    },
                                ),
                                dbc.Input(
                                    placeholder="1.0",
                                    bs_size="sm",
                                    value=1.0,
                                    id="opacity",
                                    style={
                                        "position": "absolute",
                                        "margin-left": "3px",
                                        # "padding": "3px",
                                        "border": "none",
                                        "display": "inline",
                                        "width": "10%",
                                        "textAlign": "center",
                                        "margin-top": "11px",
                                    },
                                ),
                            ],
                            style={
                                "padding-top": "5px",
                            },
                            id="graph-options-7",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    "Marker Border Width:",
                                    style={
                                        "position": "relative",
                                        "margin-left": "67px",
                                        "top": "8px",
                                        "padding": "3px",
                                        "border": "none",
                                        "color": "white",
                                        "display": "inline",
                                        "size": "10",
                                    },
                                ),
                                dbc.Input(
                                    placeholder="0",
                                    bs_size="sm",
                                    value=0,
                                    id="border_width",
                                    style={
                                        "position": "absolute",
                                        "margin-left": "3px",
                                        # "padding": "3px",
                                        "border": "none",
                                        "display": "inline",
                                        "width": "10%",
                                        "textAlign": "center",
                                        "margin-top": "11px",
                                    },
                                ),
                            ],
                            style={
                                "padding-top": "5px",
                            },
                            id="graph-options-8",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    "Marker Border Color:",
                                    style={
                                        "position": "relative",
                                        "margin-left": "67px",
                                        "top": "8px",
                                        "padding": "3px",
                                        "border": "none",
                                        "color": "white",
                                        "display": "inline",
                                        "size": "10",
                                    },
                                ),
                                html.Div(
                                    dbc.Input(
                                        type="color",
                                        id="colorpicker_marker_border",
                                        value="#000000",
                                        style={"width": 20, "height": 20},
                                    ),
                                    style={
                                        "position": "absolute",
                                        "margin-left": "5px",
                                        "margin-top": "8px",
                                        "background": "",
                                        "display": "inline",
                                    },
                                ),
                            ],
                            style={
                                "padding-top": "5px",
                            },
                            id="graph-options-9",
                        ),
                        html.Div(
                            dcc.Markdown("**Conditional Formatting**"),
                            id="main-title_3",
                            style={
                                "color": "white",
                                "position": "absolute",
                                "margin-left": "70px",
                                "display": "block",
                                "padding-top": "20px",
                            },
                        ),
                    ],
                    style=SIDEBAR_STYLE_2,
                    id="pls",
                ),
            ]
        )
    ],
    style=normal_side,  # normal_side
)


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


############################################################################################################

CONTENT_STYLE_OLD = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

CONTENT_STYLE = {
    "transition": "margin-left .5s",
    "margin-left": "8rem",
    "margin-right": "0rem",
    "padding": "2rem 1rem",
}

CONTENT_STYLE1 = {
    "transition": "margin-left .5s",
    "margin-left": "5rem",
    "margin-right": "1rem",
    "padding": "2rem 1rem",
}
CONTENT_STYLE2 = {
    "transition": "margin-left .5s",
    "margin-left": "1800rem",
    "padding": "2rem 1rem",
}


content = html.Div(id="page-content", style=CONTENT_STYLE)

other_stylez = {
    "position": "relative",
    "color": "#3456FF",
    "size": "1000",
    "top": 100,
    "left": 100,
    "right": 0,
    "bottom": 0,
    "display": "show",
}

app.layout = html.Div(
    [
        dcc.Store(id="side_click"),
        dcc.Store(id="session", storage_type="session"),
        dcc.Location(id="url"),
        navbar,
        sidebar_,
        content,
    ]
)

load_div = html.Div(
    children=[
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "800px",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "position": "fixed",
                "top": "50.5%",
                "left": "20%",
                "margin-top": "-50px",
                "margin-left": "-50px",
                "font-size": "16px",
            },
            # Allow multiple files to be uploaded
            multiple=True,
        ),
        html.Div(
            id="output-data-upload",
            style={
                "position": "relative",
                "overflow-y": "hidden",
                "width": "800px",
                "right": "20%",
            },
        ),
    ],
    id="page-content",
)


@app.callback(
    [
        Output("page-content", "style"),
        Output("pls", "style"),
        Output("side_click", "data"),
    ],
    [Input("btn_sidebar", "n_clicks")],
    [
        State("side_click", "data"),
    ],
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            pls = SIDEBAR_STYLE_
            content_style = {
                "transition": "margin-left .5s",
                "margin-left": "20rem",
            }
            cur_nclick = "HIDDEN"

        else:
            pls = SIDEBAR_STYLE_2
            content_style = {
                "transition": "margin-left .5s",
                "margin-left": "8rem",
            }
            cur_nclick = ("SHOW",)

    else:
        content_style = CONTENT_STYLE
        pls = SIDEBAR_STYLE_2
        cur_nclick = "SHOW"

    return content_style, pls, cur_nclick


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return load_div
    elif pathname == "/guidelines":
        return html.P("Guidelines")
    elif pathname == "/tutorial":
        return "Tutorial"
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


############################################################################


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    global df
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return html.Div(
        [  # Chart Top Bar
            html.Div(
                className="row chart-top-bar",
                children=[
                    html.Span(
                        id="Graph Type" + "menu_button",
                        className="inline-block chart-title",
                        children=f"Graph Type ☰",
                        n_clicks=0,
                        style={"color": "white"},
                    ),
                    # Dropdown and close button float right
                    html.Div(
                        className="graph-top-right inline-block",
                        children=[
                            html.Div(
                                className="inline-block",
                                children=[
                                    dcc.Dropdown(
                                        className="dropdown-period",
                                        id="Graph Menu" + "dropdown_period",
                                        options=[
                                            {"label": "5 min", "value": "5Min"},
                                            {"label": "15 min", "value": "15Min"},
                                            {"label": "30 min", "value": "30Min"},
                                        ],
                                        value="Select...",
                                        clearable=False,
                                    )
                                ],
                            ),
                            html.Span(
                                id="yea" + "close",
                                className="chart-close inline-block float-right",
                                children="×",
                                n_clicks=0,
                            ),
                        ],
                    ),
                ],
            ),
            dcc.Dropdown(
                id="xaxis-column",
                options=[{"value": x, "label": x} for x in df],
                placeholder="Select x axis",
                multi=True,
                value=[],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="yaxis-column",
                            options=[{"value": x, "label": x} for x in df],
                            placeholder="Select y axis",
                            multi=True,
                            value=[],
                            style={"width": "97%"},
                        )
                    ),
                ]
            ),
            dcc.Dropdown(
                id="secondary-yaxis-column",
                options=[{"value": x, "label": x} for x in df],
                placeholder="Select secondary y axis",
                multi=True,
                value=[],
                style={"display": "none"},
            ),
            dcc.Graph(id="indicator-graphic"),
            dash_table.DataTable(
                id="table-sorting-filtering",
                style_data={
                    "minWidth": "180px",
                    "width": "180px",
                    "maxWidth": "180px",
                    "height": "auto",  # ,
                },
                style_table={"overflowX": "auto", "overflowY": "auto"},
                data=df.to_dict("records"),
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10,
                tooltip_duration=None,
                page_current=0,
                page_action="custom",
                filter_action="custom",
                filter_query="",
                sort_action="custom",
                sort_mode="multi",
                sort_by=[],
            ),
            html.Hr(),  # horizontal line
        ]
    )


@app.callback(
    Output("Graph Type" + "menu", "className"),
    [Input("Graph Type" + "menu_button", "n_clicks")],
    [State("Graph Type" + "menu", "className")],
)
def generate_open_close_menu_callback():
    def open_close_menu(n, className):
        if n == 0:
            return "not_visible"
        if className == "visible":
            return "not_visible"
        else:
            return "visible"

    return open_close_menu


@app.callback(
    Output("indicator-graphic", "figure"),
    Input("xaxis-column", "value"),
    Input("yaxis-column", "value"),
    Input("btn_sidebar_lines", "n_clicks"),
    Input("btn_sidebar_scatter", "n_clicks"),
    Input("btn_sidebar_bar", "n_clicks"),
    Input("btn_sidebar_area", "n_clicks"),
    Input("btn_sidebar_box", "n_clicks"),
    Input("marker_size", "value"),
    Input("marker_style_dropdown", "value"),
    Input('colorpicker', 'value'),
    Input('opacity', 'value'),
    Input('border_width', 'value'),
    Input('colorpicker_marker_border', 'value')
)
def update_graph(
    xaxis_column_name,
    yaxis_column_name,
    n_clicks_line,
    n_clicks_scatter,
    n_clicks_bar,
    n_clicks_area,
    n_clicks_box,
    marker_size,
    marker_style,
    color,
    opacity,
    marker_border_width,
    marker_border_color
):
    dff = df.copy()
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if "btn_sidebar_lines" in changed_id:
        print("line triggered")
        fig = line_chart(dff, xaxis_column_name, yaxis_column_name)
    elif "btn_sidebar_scatter" in changed_id:
        if marker_size == "":
            marker_size = 5
        if opacity == "":
            opacity = 1.0
        if marker_border_width == "":
            marker_border_width = 0
        fig = default_graph(
            dff, xaxis_column_name, yaxis_column_name, float(marker_size), marker_style, color, float(opacity), float(marker_border_width), marker_border_color
        )
    elif "btn_sidebar_bar" in changed_id:
        fig = bar_chart(dff, xaxis_column_name, yaxis_column_name)
    elif "btn_sidebar_area" in changed_id:
        fig = area_chart(dff, xaxis_column_name, yaxis_column_name)
    elif "btn_sidebar_box" in changed_id:
        fig = box_plot(dff, xaxis_column_name, yaxis_column_name)
    else:
        if marker_size == "":
            marker_size = 5
        if opacity == "":
            opacity = 1.0
        if marker_border_width == "":
            marker_border_width = 0
        fig = default_graph(
            dff, xaxis_column_name, yaxis_column_name, float(marker_size), marker_style, color, float(opacity), float(marker_border_width), marker_border_color
        )
    print(yaxis_column_name)
    default_layout(fig)
    return fig


@app.callback(
    [Output("output-data-upload", "children"), Output("upload-data", "style")],
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]
        return children, {"display": "none"}


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find("{") + 1 : name_part.rfind("}")]

                value_part = value_part.strip()
                v0 = value_part[0]
                if v0 == value_part[-1] and v0 in ("'", '"', "`"):
                    value = value_part[1:-1].replace("\\" + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                return name, operator_type[0].strip(), value

    return [None] * 3


operators = [
    ["ge ", ">="],
    ["le ", "<="],
    ["lt ", "<"],
    ["gt ", ">"],
    ["ne ", "!="],
    ["eq ", "="],
    ["contains "],
    ["datestartswith "],
]


@app.callback(
    [
        Output("table-sorting-filtering", "data"),
        Output("table-sorting-filtering", "tooltip_data"),
    ],
    Input("table-sorting-filtering", "page_current"),
    Input("table-sorting-filtering", "page_size"),
    Input("table-sorting-filtering", "sort_by"),
    Input("table-sorting-filtering", "filter_query"),
)
def update_table(page_current, page_size, sort_by, filter):

    filtering_expressions = filter.split(" && ")
    dff = df.copy()
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == "contains":
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == "datestartswith":
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col["column_id"] for col in sort_by],
            ascending=[col["direction"] == "asc" for col in sort_by],
            inplace=False,
        )

    page = page_current
    size = page_size

    tooltip_data = [
        {
            column: {"value": str(value), "type": "markdown"}
            for column, value in row.items()
        }
        for row in dff.to_dict("records")
    ]

    return dff.iloc[page * size : (page + 1) * size].to_dict("records"), tooltip_data


##########################################Table filtering


@app.callback(
    Output("modal-centered", "is_open"),
    [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True, port=8000, host="127.0.0.1")