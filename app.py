from typing import Dict, Any, List

import dash
import dash_bootstrap_components as dbc
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
from dash.dependencies import Input, Output, State, ALL, MATCH
from plotly import tools
import dash_table
from dash.exceptions import PreventUpdate
import collections
from plotly.validators.scatter.marker import SymbolValidator
import numpy as np
import operator as op
from plotly.subplots import make_subplots
import plotly
from dash.exceptions import PreventUpdate
from collections import namedtuple
import time
import plotly.express as px


external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(
    suppress_callback_exceptions=True,
)

app.css.append_css({"external_url": external_stylesheets})

##########################################Charts########################################################################

panels = {}


class Graph:
    def __init__(self, df: pd.DataFrame()):
        self.df = df
        self.traces = []
        self.fig = make_subplots(specs=[[{"secondary_y": True}]])
        self.traces_dict = {}

    def get_traces(self) -> list:
        return [trace["name"] for trace in self.fig.data]

    def add_trace(self, trace_name):
        pass

    def delete_trace(self, trace_name, update=False):
        # print(f'delete_trace trace name {trace_name}')
        current_traces = np.array(self.get_traces())
        # print(f'delete trace current traces{current_traces}')
        del_idx = list(np.where(current_traces == trace_name))[0]
        keep_data = [i for j, i in enumerate(current_traces) if j not in del_idx]
        new_data = [trace for trace in self.fig.data if trace["name"] in keep_data]
        # print(f'new data {new_data}')
        self.fig.data = new_data
        # if not update:
        #      del self.traces_dict[trace_name]

    def keep_active_traces(self, active_y_columns):
        traces = self.get_traces()
        # print(f'prints traces{traces}')
        no_longer_active = [trace for trace in traces if trace not in active_y_columns]
        # print(f'no_longer_active {no_longer_active}')
        for trace in no_longer_active:
            self.delete_trace(trace)


class Trace(Graph):
    def __init__(self, trace_name: str, trace_type: str):
        super().__init__(df)
        self.trace_name = trace_name
        self.trace_type = trace_type
        # traces_dict = Graph._traces_dict


class Scatter(Trace):
    """Represents a Scatter Graph trace."""

    def __init__(
            self,
            x_axis_column_name: str,
            y_axis_dict: dict,
            trace_name: str,
            trace_type: str = "Scatter",
    ) -> object:
        super().__init__(trace_name, trace_type)
        self.x_axis_column_name = x_axis_column_name
        self.y_axis_dict = y_axis_dict
        self.marker_symbol = "circle"
        self.marker_color = "black"
        self.marker_size = 5.0
        self.border_width = 0.0
        self.border_color = "black"
        self.opacity = 1.0
        # traces_dict = Graph._traces_dict

    def add_trace(self):
        traces = super().get_traces()
        column = self.y_axis_dict["name"]
        if column not in traces:
            t = go.Scatter(
                x=self.df[self.x_axis_column_name],
                y=self.df[column],
                mode="markers",
                marker=dict(
                    color=self.marker_color,
                    size=self.marker_size,
                    opacity=self.opacity,
                    line=dict(width=self.border_width, color=self.border_color),
                    symbol=self.marker_symbol,
                ),
                name=column,
            )
            self.fig.add_trace(t, secondary_y=self.y_axis_dict["dual"])


class Line(Trace):
    """Represents a Scatter Graph trace."""

    def __init__(
            self,
            x_axis_column_name: str,
            y_axis_dict: dict,
            trace_name: str,
            trace_type: str = "Line",
    ) -> object:
        super().__init__(trace_name, trace_type)
        self.x_axis_column_name = x_axis_column_name
        self.y_axis_dict = y_axis_dict
        self.marker_symbol = "circle"
        self.marker_size = 5.0
        self.line_color = "black"
        self.width = 2.0
        self.border_width = 0.0
        self.border_color = "black"
        self.opacity = 1.0
        self.mode = "lines"
        self.dash = None
        self.connectgaps = True

    def add_trace(self):
        traces = super().get_traces()
        column = self.y_axis_dict["name"]
        # self.traces_dict[column] = True
        if column not in traces:
            self.fig.add_trace(
                go.Scatter(
                    x=self.df[self.x_axis_column_name],
                    y=self.df[column],
                    mode=self.mode,
                    connectgaps=self.connectgaps,
                    opacity=self.opacity,
                    line=dict(
                        color=self.line_color,
                        width=self.width,
                        dash=self.dash,
                    ),
                    marker=dict(symbol=self.marker_symbol, size=self.marker_size),
                    name=column,
                ),
                secondary_y=self.y_axis_dict["dual"],
            )

class Bar(Trace):
    """Represents a Bar Graph trace."""

    def __init__(
        self,
        x_axis_column_name: str,
        y_axis_dict: dict,
        trace_name: str,
        trace_type: str = "Bar",
    ) -> object:
        super().__init__(trace_name, trace_type)
        self.x_axis_column_name = x_axis_column_name
        self.y_axis_dict = y_axis_dict
        self.text = None
        self.color = "blue"
        self.orientation = "v"

    def add_trace(self):
        traces = super().get_traces()
        column = self.y_axis_dict["name"]
        if column not in traces:
            x = self.x_axis_column_name
            y = column
            if self.orientation == "h":
                x = column
                y = self.x_axis_column_name

            fig = px.bar(
                self.df,
                x=x,
                y=y,
                orientation=self.orientation,
                text=self.text
                # color=self.color,
                # color_discrete_sequence=["blue"],
                # base=-self.df[column].values,
                # base="pop",
                # text=column,
                # textposition="outside",
                # texttemplate="%{text:.2s}",
                # marker_color="lightsalmon",
                # name=column,
            ).data[0]
            fig["marker"]["color"] = self.color
            self.fig.add_trace(
                fig,
                # secondary_y=False,
            )


def default_graph(
        df,
        xaxis_column_name,
        y_axis_dict,
        marker_size,
        marker_style,
        color,
        opacity,
        marker_border_width,
        marker_border_color,
):
    traces = [trace['name'] for trace in fig.data]
    print(y_axis_dict)
    for y in y_axis_dict:
        column = y['name']
        print(f'column: {column}')
        if len(column) != 0:
            for col in column:
                if col not in traces:
                    fig.add_trace(
                        go.Scatter(
                            x=df[xaxis_column_name[0]],
                            y=df[col],
                            mode="markers",
                            marker=dict(
                                color=color,
                                size=marker_size,
                                opacity=opacity,
                                line=dict(width=marker_border_width, color=marker_border_color),
                                symbol=marker_style,
                            ),
                            name=col,
                        ),
                        secondary_y=y['dual']
                    )
    return fig


def scatter_symbols():
    raw_symbols = SymbolValidator().values
    namestems = []
    namevariants = []
    symbols = []
    for i in range(0, len(raw_symbols), 3):
        name = raw_symbols[i + 2]
        symbols.append(raw_symbols[i])
        namestems.append(name.replace("-open", "").replace("-dot", ""))
        namevariants.append(name[len(namestems[-1]):])
    symbols = [name + variant for name, variant in zip(namestems, namevariants)]
    return [dict(zip(("label", "value"), symbol)) for symbol in zip(symbols, symbols)]


def scatter_conditional_dropdown_options():
    options = [
        "Marker Size",
        "Marker Symbol",
        "Marker Color",
        "Opacity",
        "Marker Border Width",
        "Marker Border Color",
    ]
    return [dict(zip(("label", "value"), option)) for option in zip(options, options)]


def line_conditional_dropdown_options():
    options = [
        #'Line Width',
        #'Line Color',
        #'Opacity',
        #'Line Mode',
        'Marker Symbol',
        'Marker Size',
        #'Dash',
        #'Connect Gaps'
    ]
    return [dict(zip(("label", "value"), option)) for option in zip(options, options)]


def line_mode_dropdown_options():
    options = [
        'lines',
        'lines+markers'
    ]
    return [dict(zip(("label", "value"), option)) for option in zip(options, options)]


def line_dash_dropdown_options():
    options = [
        'dash',
        'dot',
        'dashdot'
    ]
    return [dict(zip(("label", "value"), option)) for option in zip(options, options)]


def df_column_dropdown_options():
    cols = list(df.columns)
    return [dict(zip(("label", "value"), col)) for col in zip(cols, cols)]


def conditional_formatting_operators():
    conditional_operators = ["==", ">", "<", "!=", ">=", "<="]
    return [
        dict(zip(("label", "value"), operator))
        for operator in zip(conditional_operators, conditional_operators)
    ]


def conditional_change_to_options(option: str) -> object:
    if option in {"Marker Size", "Opacity", "Marker Border Width", 'Line Width', }:
        children = dbc.Input(
            bs_size="sm",
            id={"type": f"change_to", "index": option},
            # value='',
            style={
                "position": "sticky",
                "margin-left": "3px",
                "border": "none",
                "display": "inline",
                "width": "20%",
                "textAlign": "center",
                "margin-top": "8px",
            },
        )
        return children
    elif option in {"Marker Color", "Marker Border Color", 'Line Color'}:
        children = dbc.Input(
            type="color",
            id={"type": f"change_to", "index": option},
            value="#000000",
            style={"width": 20, "height": 20, "margin-top": "8px"},
        )
        return children
    elif option in {"Marker Symbol"}:
        children = dcc.Dropdown(
            id={"type": f"change_to", "index": option},
            options=scatter_symbols(),
            # value='',
            style={
                "width": "100px",
                "height": "8px",
                "vertical-align": "middle",
                "font-size": 10,
            },
        )
        return children
    elif option in {'Connect Gaps'}:
        options = [
                      {'label': 'True', 'value': True},
                      {'label': 'False', 'value': False},
                  ]
        children = dcc.Dropdown(
            id={"type": f"change_to", "index": option},
            options=options,
            style={
                "width": "100px",
                "height": "8px",
                "vertical-align": "middle",
                "font-size": 10,
            },
        )
        return children
    elif option in {'Dash'}:
        children = dcc.Dropdown(
            id={"type": f"change_to", "index": option},
            options= line_dash_dropdown_options(),
            value=None,
            style={
                "width": "100px",
                "height": "8px",
                "vertical-align": "middle",
                "font-size": 10,
            },
        )
        return children
    elif option in {'Line Mode'}:
        children = dcc.Dropdown(
            id={"type": f"change_to", "index": option},
            options= line_mode_dropdown_options(),
            style={
                "width": "100px",
                "height": "8px",
                "vertical-align": "middle",
                "font-size": 10,
            },
        )
        return children



def operator_filter(df, operator, original_value, new_value, col, condition):
    if (
            condition != []
            and new_value != []
            and col != []
            and condition not in ['', None]
    ):
        if condition[0].isnumeric():
            condition = float(condition)
        if new_value not in [None, ''] and new_value[0].isnumeric():
            new_value = float(new_value)
        print(new_value)
        print(type(new_value))
        ops = {
            ">": op.gt(df[col], condition),
            "<": op.lt(df[col], condition),
            ">=": op.ge(df[col], condition),
            "<=": op.le(df[col], condition),
            "==": op.eq(df[col], condition),
            "!=": op.ne(df[col], condition),
        }
        return np.where(ops[operator], new_value, original_value)
    else:
        return original_value


def operators_change(df, operator, original_value, new_value, col, condition):
    return operator_filter(df, operator, original_value, new_value, col, condition)


fig = make_subplots(specs=[[{"secondary_y": True}]])


def default_graph(
        df,
        xaxis_column_name,
        y_axis_dict,
        marker_size,
        marker_style,
        color,
        opacity,
        marker_border_width,
        marker_border_color,
):
    traces = [trace['name'] for trace in fig.data]
    print(y_axis_dict)
    for y in y_axis_dict:
        column = y['name']
        print(f'column: {column}')
        if len(column) != 0:
            for col in column:
                if col not in traces:
                    fig.add_trace(
                        go.Scatter(
                            x=df[xaxis_column_name[0]],
                            y=df[col],
                            mode="markers",
                            marker=dict(
                                color=color,
                                size=marker_size,
                                opacity=opacity,
                                line=dict(width=marker_border_width, color=marker_border_color),
                                symbol=marker_style,
                            ),
                            name=col,
                        ),
                        secondary_y=y['dual']
                    )
    return fig


def line_chart(
        df,
        xaxis_column_name,
        yaxis_column_name,
):
    # fig = go.Figure()
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
    # fig = go.Figure()
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
    # fig = go.Figure()
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

scatter_formatting_options = html.Div(
    [
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
                    id="scatter_marker_size",
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
                        id="scatter_marker_style_dropdown",
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
                        id="scatter_colorpicker",
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
                    id="scatter_opacity",
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
                    id="scatter_border_width",
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
                        id="scatter_colorpicker_marker_border",
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
    ],
    id='scatter_formatting_options',
    style={}
)

line_formatting_options = html.Div(
    [
        html.Div(
            dcc.Markdown("**Line Formatting**"),
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
                    "Line Width:",
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
                    placeholder="2",
                    bs_size="sm",
                    value=2,
                    id="line_width",
                    style={
                        "position": "sticky",
                        "margin-left": "3px",
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
        ),
        html.Div(
            children=[
                html.Div(
                    "Line Color:",
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
                        id="line_colorpicker",
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
                "padding-top": "0px",
            },
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
                    id="line_opacity",
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
        ),
        html.Div(
            children=[
                html.Div(
                    "Mode:",
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
                        id="line_mode_dropdown",
                        options=line_mode_dropdown_options(),
                        placeholder="lines",
                        value='lines',
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
                "padding-top": "10px",
            },
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
                        id="line_marker_style_dropdown",
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
                "padding-top": "20px",
            },
        ),
        html.Div(
            children=[
                html.Div(
                    "Marker Size:",
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
                    id="line_marker_size",
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
                "padding-top": "20px",
            },

        ),
        html.Div(
            children=[
                html.Div(
                    "Dash:",
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
                        id="line_dash_dropdown",
                        options=line_dash_dropdown_options(),
                        value=None,
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
                "padding-top": "20px",
            },
        ),
        html.Div(
            children=[
                html.Div(
                    "Connect Gaps:",
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
                        id="line_gaps_dropdown",
                        options=[
                            {'label': 'True', 'value': True},
                            {'label': 'False', 'value': False},
                        ],
                        value=False,
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
                "padding-top": "20px",
            },
        ),
        # html.Div(
        #     children=[
        #         html.Div(
        #             "Marker Border Width:",
        #             style={
        #                 "position": "relative",
        #                 "margin-left": "67px",
        #                 "top": "8px",
        #                 "padding": "3px",
        #                 "border": "none",
        #                 "color": "white",
        #                 "display": "inline",
        #                 "size": "10",
        #             },
        #         ),
        #         dbc.Input(
        #             placeholder="0",
        #             bs_size="sm",
        #             value=0,
        #             id="border_width",
        #             style={
        #                 "position": "absolute",
        #                 "margin-left": "3px",
        #                 # "padding": "3px",
        #                 "border": "none",
        #                 "display": "inline",
        #                 "width": "10%",
        #                 "textAlign": "center",
        #                 "margin-top": "11px",
        #             },
        #         ),
        #     ],
        #     style={
        #         "padding-top": "5px",
        #     },
        #     id="graph-options-8",
        # ),
        # html.Div(
        #     children=[
        #         html.Div(
        #             "Marker Border Color:",
        #             style={
        #                 "position": "relative",
        #                 "margin-left": "67px",
        #                 "top": "8px",
        #                 "padding": "3px",
        #                 "border": "none",
        #                 "color": "white",
        #                 "display": "inline",
        #                 "size": "10",
        #             },
        #         ),
        #         html.Div(
        #             dbc.Input(
        #                 type="color",
        #                 id="colorpicker_marker_border",
        #                 value="#000000",
        #                 style={"width": 20, "height": 20},
        #             ),
        #             style={
        #                 "position": "absolute",
        #                 "margin-left": "5px",
        #                 "margin-top": "8px",
        #                 "background": "",
        #                 "display": "inline",
        #             },
        #         ),
        #     ],
        #     style={
        #         "padding-top": "5px",
        #     },
        #     id="graph-options-9",
        # ),
    ],
    id='line_formatting_options',
    style={'display': 'none'}
)
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
                                    dcc.Dropdown(
                                        id="trace_dropdown",
                                        options=[],
                                        value='',
                                        placeholder='Select Trace to Edit',
                                        style={
                                            "width": "150px",
                                            "height": "8px",
                                            "vertical-align": "middle",
                                            "font-size": 10,
                                        },
                                    ),
                                    style={
                                        "position": "sticky",
                                        "margin-left": "70px",
                                        "margin-top": "3px",
                                        'padding-bottom': '35px'
                                        # 'z-index': '100'
                                    },
                                ),
                                html.Div(
                                    [
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
                                        scatter_formatting_options,
                                        line_formatting_options,
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
                                        html.Div(
                                            children=[
                                                html.Div(
                                                    "Change ",
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
                                                        id="conditional-change-options",
                                                        options=[],
                                                        value="",
                                                        style={
                                                            "width": "150px",
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
                                                "padding-top": "45px",
                                            },
                                            id="graph-options-10",
                                        ),
                                        html.Div(
                                            children=[
                                                html.Div(
                                                    "To ",
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
                                                    id="conditional-change-to",
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
                                                "padding-top": "20px",
                                            },
                                            id="graph-options-13",
                                        ),
                                        html.Div(
                                            children=[
                                                html.Div(
                                                    "Based on ",
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
                                                        id="conditional-change-columns",
                                                        options=[],
                                                        value='',
                                                        # value="circle",
                                                        style={
                                                            "width": "150px",
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
                                                "padding-top": "20px",
                                            },
                                            id="graph-options-11",
                                        ),
                                        html.Div(
                                            children=[
                                                html.Div(
                                                    "If values",
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
                                                        id="conditional-change-operators",
                                                        placeholder="",
                                                        value='',
                                                        options=conditional_formatting_operators(),
                                                        style={
                                                            "width": "50px",
                                                            "height": "8px",
                                                            "vertical-align": "middle",
                                                            "font-size": 15,
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
                                                dbc.Input(
                                                    bs_size="sm",
                                                    id="conditional-value",
                                                    value='',
                                                    placeholder="condition...",
                                                    style={
                                                        "position": "absolute",
                                                        "margin-left": "63px",
                                                        # "padding": "3px",
                                                        "border": "none",
                                                        "display": "inline",
                                                        "width": "30%",
                                                        "height": "30px",
                                                        "textAlign": "center",
                                                        "margin-top": "5px",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "padding-top": "20px",
                                            },
                                            id="graph-options-12",
                                        ),
                                    ],
                                    id='side_panels'
                                )
                            ],
                        )
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


def serve_layout():
    layout = html.Div(
        [
            dcc.Store(id="side_click"),
            dcc.Store(id="session", storage_type="session"),
            dcc.Location(id="url"),
            navbar,
            sidebar_,
            content,
            html.Div(id='panel_data_container')
        ]
    )
    return layout


app.layout = serve_layout()

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
            cur_nclick = "SHOW"

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
    global g
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            g = Graph(df)
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            g = Graph(df)
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
                                    dbc.FormGroup(
                                        [
                                            dbc.Label(
                                                "Dual Y Axis",
                                                className="inline-block chart-title",
                                                style={"color": "white"},
                                            ),
                                            html.Div(
                                                html.Label(
                                                    children=[
                                                        dcc.Input(
                                                            type="checkbox",
                                                            value=True,
                                                            id="dual-y-slider",
                                                        ),
                                                        html.Span(
                                                            className="slider round"
                                                        ),
                                                    ],
                                                    className="switch",
                                                    style={"margin-left": "5px"},
                                                ),
                                                className="inline-block chart-title",
                                                id="dual-y-slider-container",
                                                n_clicks=0

                                            ),
                                        ]
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
                placeholder="Select X Axis",
                multi=True,
                value=[],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="yaxis-column",
                            options=[{"value": x, "label": x} for x in df],
                            placeholder="Select Y Axis",
                            multi=True,
                            value=[],
                            style={"width": "100%"},
                        )
                    ),
                ]
            ),
            dcc.Dropdown(
                id="secondary-yaxis-column",
                options=[{"value": x, "label": x} for x in df],
                placeholder="Select Secondary Y Axis",
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


def normalize_n_clicks(n_clicks):
    if n_clicks == 0:
        return n_clicks
    else:
        n_clicks = int(n_clicks / 2)
        return n_clicks


def boolean_n_clicks(n_clicks):
    if n_clicks % 2 == 0:
        return False
    else:
        return True


@app.callback(
    Output("secondary-yaxis-column", "style"),
    Input("dual-y-slider-container", "n_clicks"),
)
def generate_dual_y_axis_dropdown(n_clicks):
    n_clicks = normalize_n_clicks(n_clicks)
    if n_clicks % 2 == 0:
        return {'display': 'none'}
    else:
        return {}


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


def change_to_formatting(
        marker_size,
        marker_style,
        color,
        opacity,
        marker_border_width,
        marker_border_color,
        change_option,
        new_option,
):
    options_dict = {
        "marker_size": float(marker_size),
        "marker_symbol": marker_style,
        "color": color,
        "opacity": float(opacity),
        "marker_border_width": float(marker_border_width),
        "marker_border_color": marker_border_color,
    }
    if change_option == "Marker Size":
        options_dict["marker_size"] = new_option
    elif change_option == "Marker Symbol":
        options_dict["marker_symbol"] = new_option
    elif change_option == "Marker Color":
        options_dict["color"] = new_option
    elif change_option == "Opacity":
        options_dict["opacity"] = new_option
    elif change_option == "Marker Border Width":
        options_dict["marker_border_width"] = new_option
    else:
        options_dict["marker_border_color"] = new_option

    return (
        options_dict["marker_size"],
        options_dict["marker_symbol"],
        options_dict["color"],
        options_dict["opacity"],
        options_dict["marker_border_width"],
        options_dict["marker_border_color"],
    )


options = [
    "Marker Size",
    "Opacity",
    "Marker Border Width",
    "Marker Color",
    "Marker Border Color",
    "Marker Symbol",
]


def trace_component(trace_name, component_to_update, updated_value):
    if component_to_update == 'Marker Symbol':
        def update(trace):
            trace['marker']['symbol'] = updated_value if trace.name == trace_name else ()

    return update


def update_trace(trace_name, component_to_update, updated_value):
    fig.for_each_trace(
        trace_component(trace_name, component_to_update, updated_value)
    )


def clear_trace(trace_name):
    # for i, d in enumerate(fig.data):
    #     if d['name'] == trace_name:
    #         print(d, i)
    #         data_list = list(fig.data)
    #         data_list.pop(i)
    #         fig.data = data_list
    traces = np.array([trace['name'] for trace in fig.data])
    del_idx = list(np.where(traces == trace_name))[0]
    keep_data = [i for j, i in enumerate(traces) if j not in del_idx]
    new_data = [trace for trace in fig.data if trace['name'] in keep_data]
    fig.data = new_data


def keep_active_traces(active_y_columns):
    traces = [trace['name'] for trace in fig.data]
    no_longer_active = [trace for trace in traces if trace not in active_y_columns]
    # print(f'no longer active {no_longer_active}')
    for trace in no_longer_active:
        clear_trace(trace)


component_dict = {
    'marker_style_dropdown': 'Marker Symbol',
    'marker_size': 'Marker Size',
    'marker_style': 'Marker Style'

}


def update_cycle(active):
    active.fig.data = []
    active.add_trace()
    g.fig.add_trace(active.fig.data[0])


def serve_scatter(x_axis_column, y_axis_columns, dual=False):
    g.keep_active_traces(y_axis_columns)
    for y in y_axis_columns:
        if y not in g.get_traces():
            scatter = Scatter(x_axis_column[0], {'name': y, 'dual': dual}, y)
            scatter.add_trace()
            g.fig.add_trace(scatter.fig.data[0])
            g.traces_dict[scatter.trace_name] = {'trace': scatter,
                                                 'settings': {'Marker Size': scatter.marker_size,
                                                              'Marker Symbol': scatter.marker_symbol,
                                                              'Marker Color': scatter.marker_color,
                                                              'Opacity': scatter.opacity,
                                                              'Marker Border Width': scatter.border_width,
                                                              'Marker Border Color': scatter.border_color,
                                                              'Change': '',
                                                              'To': [],
                                                              'Column': '',
                                                              'Operator': '',
                                                              'Condition': ''

                                                              }
                                                 }


def serve_line(x_axis_column, y_axis_columns, trace, dual=False):
    g.keep_active_traces(y_axis_columns)
    g.delete_trace(trace)
    for y in y_axis_columns:
        if y not in g.get_traces():
            line = Line(x_axis_column[0], {'name': trace, 'dual': dual}, trace)
            line.add_trace()
            g.fig.add_trace(line.fig.data[0])
            g.traces_dict[line.trace_name] = {'trace': line,
                                              'settings': {'Line Width': line.width,
                                                           'Marker Symbol': line.marker_symbol,
                                                           'Marker Size': line.marker_size,
                                                           'Line Color': line.line_color,
                                                           'Opacity': line.opacity,
                                                           'Border Width': line.border_width,
                                                           'Border Color': line.border_color,
                                                           'Mode': line.mode,
                                                           'Dash': line.dash,
                                                           'Connect Gaps': line.connectgaps,
                                                           'Change': '',
                                                           'To': [],
                                                           'Column': '',
                                                           'Operator': '',
                                                           'Condition': ''

                                                           }
                                              }

def serve_bar(x_axis_column, y_axis_columns, trace, dual=False):
    g.keep_active_traces(y_axis_columns)
    g.delete_trace(trace)
    for y in y_axis_columns:
        if y not in g.get_traces():
            bar = Bar(x_axis_column[0], {'name': trace, 'dual': dual}, trace)
            bar.add_trace()
            g.fig.add_trace(bar.fig.data[0])
            # g.traces_dict[bar.trace_name] = {'trace': bar,
            #                                   'settings': {'Line Width': line.width,
            #                                                'Marker Symbol': line.marker_symbol,
            #                                                'Marker Size': line.marker_size,
            #                                                'Line Color': line.line_color,
            #                                                'Opacity': line.opacity,
            #                                                'Border Width': line.border_width,
            #                                                'Border Color': line.border_color,
            #                                                'Mode': line.mode,
            #                                                'Dash': line.dash,
            #                                                'Connect Gaps': line.connectgaps,
            #                                                'Change': '',
            #                                                'To': [],
            #                                                'Column': '',
            #                                                'Operator': '',
            #                                                'Condition': ''
            #
            #                                                }
            #                                   }


def edit_scatter_options(changed_id: str, trace: str, active: object, settings: object, scatter_options: dict):
    if 'scatter_marker_style_dropdown' in changed_id:
        g.delete_trace(trace, True)
        active.marker_symbol = scatter_options['Marker Symbol']
        update_cycle(active)
        settings['Marker Symbol'] = scatter_options['Marker Symbol']
    elif 'scatter_colorpicker' in changed_id:
        g.delete_trace(trace, True)
        active.marker_color = scatter_options['Marker Color']
        update_cycle(active)
        settings['Marker Color'] = scatter_options['Marker Color']
    elif 'scatter_marker_size' in changed_id:
        g.delete_trace(trace, True)
        active.marker_size = float(scatter_options['Marker Size'])
        update_cycle(active)
        settings['Marker Size'] = float(scatter_options['Marker Size'])
    elif 'scatter_opacity' in changed_id:
        g.delete_trace(trace, True)
        active.opacity = float(scatter_options['Opacity'])
        update_cycle(active)
        settings['Opacity'] = float(scatter_options['Opacity'])
    elif 'scatter_border_width' in changed_id:
        g.delete_trace(trace, True)
        active.border_width = float(scatter_options['Marker Border Width'])
        update_cycle(active)
        settings['Marker Border Width'] = float(scatter_options['Marker Border Width'])
    elif 'scatter_colorpicker_marker_border' in changed_id:
        g.delete_trace(trace, True)
        active.border_color = scatter_options['Marker Border Color']
        update_cycle(active)
        settings['Marker Border Width'] = scatter_options['Marker Border Color']


def scatter_conditional_options(active: object, trace: str, conditional_arguments: object,
                                scatter_options: object, all_y_columns: list):
    # Need to refactor this function, too much happening in one function, split into multiple smaller or simplify operators_change so that there is less repitition overall.
    option = conditional_arguments.change_option
    new_formatting = operators_change(conditional_arguments.dff, conditional_arguments.operator,
                                      scatter_options[option], conditional_arguments.change_to[0],
                                      conditional_arguments.col, conditional_arguments.condition)

    g.delete_trace(trace, True)
    if option == 'Marker Symbol':
        active.marker_symbol = new_formatting
    elif option == 'Marker Color':
        active.marker_color = new_formatting
    elif option == 'Marker Size':
        active.marker_size = new_formatting
    elif option == 'Opacity':
        active.opacity = new_formatting
    elif option == 'Marker Border Width':
        active.border_width = new_formatting
    elif option == 'Marker Border Color':
        active.border_color = new_formatting
    update_cycle(active)

    for y in all_y_columns:
        if trace not in ['', None] and y not in g.get_traces():
            new_trace = y
        else:
            new_trace = None

        if trace not in ['', None, new_trace]:
            g.traces_dict[trace]['settings'] = {'Marker Size': float(scatter_options['Marker Size']),
                        'Marker Symbol': scatter_options['Marker Symbol'],
                        'Marker Color': scatter_options['Marker Color'],
                        'Opacity': float(scatter_options['Opacity']),
                        'Marker Border Width': float(
                            scatter_options['Marker Border Width']),
                        'Marker Border Color': scatter_options['Marker Border Color'],
                        'Change': conditional_arguments.change_option,
                        'To': conditional_arguments.change_to,
                        'Column': conditional_arguments.col,
                        'Operator': conditional_arguments.operator,
                        'Condition': conditional_arguments.condition
                        }


def edit_line_options(changed_id: str, trace: str, active: object, settings: object, line_options: dict):
    if 'line_width' in changed_id:
        g.delete_trace(trace, True)
        active.width = float(line_options['Line Width'])
        update_cycle(active)
        settings['Line Width'] = float(line_options['Line Width'])
    elif 'line_colorpicker' in changed_id:
        g.delete_trace(trace, True)
        active.line_color = line_options['Line Color']
        update_cycle(active)
        settings['Line Color'] = line_options['Line Color']
    elif 'line_mode_dropdown' in changed_id:
        g.delete_trace(trace, True)
        active.mode = line_options['Line Mode']
        update_cycle(active)
        settings['Mode'] = line_options['Line Mode']
    elif 'line_opacity' in changed_id:
        g.delete_trace(trace, True)
        active.opacity = float(line_options['Opacity'])
        update_cycle(active)
        settings['Opacity'] = float(line_options['Opacity'])
    elif 'line_marker_style_dropdown' in changed_id:
        g.delete_trace(trace, True)
        active.marker_symbol = line_options['Marker Symbol']
        update_cycle(active)
        settings['Marker Symbol'] = line_options['Marker Symbol']
    elif 'line_marker_size' in changed_id:
        g.delete_trace(trace, True)
        active.marker_size = float(line_options['Marker Size'])
        update_cycle(active)
        settings['Marker Size'] = float(line_options['Marker Size'])
    elif 'line_dash_dropdown' in changed_id:
        g.delete_trace(trace, True)
        active.dash = line_options['Dash']
        update_cycle(active)
        settings['Dash'] = line_options['Dash']
    elif 'line_gaps_dropdown' in changed_id:
        g.delete_trace(trace, True)
        active.connectgaps = line_options['Line Gaps']
        update_cycle(active)
        settings['Connect Gaps'] = line_options['Line Gaps']

def line_conditional_options(active: object, trace: str, conditional_arguments: object,
                                line_options: object, all_y_columns: list):
    # Need to refactor this function, too much happening in one function, split into multiple smaller or simplify operators_change so that there is less repitition overall.
    option = conditional_arguments.change_option
    new_formatting = operators_change(conditional_arguments.dff, conditional_arguments.operator,
                                      line_options[option], conditional_arguments.change_to[0],
                                      conditional_arguments.col, conditional_arguments.condition)

    g.delete_trace(trace, True)
    if option == 'Line Width':
        active.width = new_formatting
    elif option == 'Line Color':
        active.line_color = new_formatting
    elif option == 'Opacity':
        active.opacity = new_formatting
    elif option == 'Line Mode':
        active.mode = new_formatting
    elif option == 'Marker Symbol':
        active.marker_symbol = new_formatting
    elif option == 'Marker Size':
        active.marker_size = new_formatting
    elif option == 'Dash':
        active.dash = new_formatting
    elif option == 'Line Gaps':
        active.connectgaps = new_formatting
    update_cycle(active)

    for y in all_y_columns:
        if trace not in ['', None] and y not in g.get_traces():
            new_trace = y
        else:
            new_trace = None

        if trace not in ['', None, new_trace]:
            g.traces_dict[trace]['settings'] = {
                                                'Line Width': line_options['Line Width'],
                                               'Marker Symbol': line_options['Marker Symbol'],
                                               'Marker Size': line_options['Marker Size'],
                                               'Line Color': line_options['Line Color'],
                                               'Opacity': line_options['Opacity'],
                                               #'Border Width': line_options[''],
                                               #'Border Color': line.border_color,
                                               'Mode': line_options['Line Mode'],
                                               'Dash': line_options['Dash'],
                                               'Connect Gaps': line_options['Line Gaps'],
                                                'Change': conditional_arguments.change_option,
                                                'To': conditional_arguments.change_to,
                                                'Column': conditional_arguments.col,
                                                'Operator': conditional_arguments.operator,
                                                'Condition': conditional_arguments.condition

                                               }

@app.callback(
    Output("indicator-graphic", "figure"),
    Output('trace_dropdown', 'options'),
    Input("xaxis-column", "value"),
    Input("yaxis-column", "value"),
    # Graph option button inputs
    Input(f"btn_sidebar_lines", "n_clicks"),
    Input(f"btn_sidebar_scatter", "n_clicks"),
    Input(f"btn_sidebar_bar", "n_clicks"),
    Input(f"btn_sidebar_area", "n_clicks"),
    Input(f"btn_sidebar_box", "n_clicks"),
    # Scatter Inputs
    Input(f"scatter_marker_size", "value"),
    Input(f"scatter_marker_style_dropdown", "value"),
    Input(f"scatter_colorpicker", "value"),
    Input(f"scatter_opacity", "value"),
    Input(f"scatter_border_width", "value"),
    Input(f"scatter_colorpicker_marker_border", "value"),
    # Line Graph Inputs
    Input("line_width", "value"),
    Input("line_colorpicker", "value"),
    Input("line_opacity", "value"),
    Input("line_mode_dropdown", "value"),
    Input("line_marker_style_dropdown", "value"),
    Input('line_marker_size', 'value'),
    Input("line_dash_dropdown", "value"),
    Input("line_gaps_dropdown", "value"),

    # Conditional Formatting Inputs
    Input(f"conditional-change-options", "value"),
    Input({"type": "change_to", "index": ALL}, "value"),
    Input(f"conditional-change-operators", "value"),
    Input(f"conditional-change-columns", "value"),
    Input(f"conditional-value", "value"),

    Input(f"dual-y-slider-container", 'n_clicks'),
    Input(f"secondary-yaxis-column", 'value'),
    Input(f"trace_dropdown", 'value')
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
        marker_border_color,
        line_width,
        line_color,
        line_opacity,
        line_mode,
        line_marker_style,
        line_marker_size,
        line_dash,
        line_gaps,
        change_option,
        change_to,
        operator,
        col,
        condition,
        secondary_y_clicks,
        secondary_yaxis_columns,
        trace
):
    y_axis_dict = [
        dict(zip(("name", "dual"), option))
        for option in zip((yaxis_column_name, secondary_yaxis_columns), (False, True))
    ]
    all_y_columns = list(yaxis_column_name)
    all_y_columns.extend(secondary_yaxis_columns)

    trace_options = [dict(zip(("label", "value"), trace)) for trace in zip(all_y_columns, all_y_columns)]

    scatter_options = {
        "Marker Size": marker_size,
        "Marker Symbol": marker_style,
        "Marker Color": color,
        "Opacity": opacity,
        "Marker Border Width": marker_border_width,
        "Marker Border Color": marker_border_color,
    }
    line_options = {
        'Line Width': line_width,
        'Line Color': line_color,
        'Opacity': line_opacity,
        'Line Mode': line_mode,
        'Marker Symbol': line_marker_style,
        "Marker Size": line_marker_size,
        'Dash': line_dash,
        'Line Gaps': line_gaps
    }

    dff = df.copy()

    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]

    ####################################################################################################################
    # Edit Traces (no conditional)

    if trace not in ['', None]:
        active = g.traces_dict[trace]['trace']
        settings = g.traces_dict[trace]['settings']
        if active.trace_type == 'Scatter':
            edit_scatter_options(changed_id, trace, active, settings, scatter_options)
        elif active.trace_type == 'Line':
            edit_line_options(changed_id, trace, active, settings, line_options)
    ####################################################################################################################

    ####################################################################################################################
    if trace not in ['', None]:
        active = g.traces_dict[trace]['trace']
    # Conditional Editing
    if operator not in [None, ''] and col not in [None, ''] and condition not in ['', None] and trace not in ['',
                                                                                                              None] and change_to not in [
        None, []]:
        print(f'change_to {change_to}')
        active = g.traces_dict[trace]['trace']
        settings = g.traces_dict[trace]['settings']
        ConditionalArguments = namedtuple('ConditionalArguments',
                                          ['change_option', 'dff', 'operator', 'change_to', 'col', 'condition'])
        conditional_arguments = ConditionalArguments(change_option, dff, operator, change_to, col, condition)
        if active.trace_type == 'Scatter':
            scatter_conditional_options(active, trace, conditional_arguments, scatter_options, all_y_columns)
        elif active.trace_type == 'Line':
            line_conditional_options(active, trace, conditional_arguments, line_options, all_y_columns)

    ####################################################################################################################

    if "btn_sidebar_lines" in changed_id and len(xaxis_column_name) > 0 and trace not in ['', None]:
        ####################################################################################################################
        if trace in yaxis_column_name:
            serve_line(xaxis_column_name, all_y_columns, trace, dual=False)
        elif trace in secondary_yaxis_columns:
            serve_line(xaxis_column_name, all_y_columns, trace, dual=True)

    if "btn_sidebar_bar" in changed_id and len(xaxis_column_name) > 0 and trace not in ['', None]:
        ####################################################################################################################
        if trace in yaxis_column_name:
            serve_bar(xaxis_column_name, all_y_columns, trace, dual=False)
        elif trace in secondary_yaxis_columns:
            serve_bar(xaxis_column_name, all_y_columns, trace, dual=True)

    elif "btn_sidebar_scatter" in changed_id and len(xaxis_column_name) > 0 and trace not in ['', None]:
        print('scatter button clicked')
        if trace in yaxis_column_name:
            g.delete_trace(trace)
            serve_scatter(xaxis_column_name, all_y_columns, dual=False)
        elif trace in secondary_yaxis_columns:
            g.delete_trace(trace)
            serve_scatter(xaxis_column_name, all_y_columns, dual=True)

    elif "btn_sidebar_bar" in changed_id:
        fig = bar_chart(dff, xaxis_column_name, yaxis_column_name)
    elif "btn_sidebar_area" in changed_id:
        fig = area_chart(dff, xaxis_column_name, yaxis_column_name)
    elif "btn_sidebar_box" in changed_id:
        fig = box_plot(dff, xaxis_column_name, yaxis_column_name)

        # Secondary Y Axis default graph
    elif 'secondary-yaxis-column' in changed_id and len(xaxis_column_name) > 0:
        print('secondary y scatter')
        serve_scatter(xaxis_column_name, all_y_columns, dual=True)
        # Normal Y Axis default graph
    elif 'yaxis-column' in changed_id and len(xaxis_column_name) > 0:
        print('normal y scatter')
        print(changed_id)
        serve_scatter(xaxis_column_name, all_y_columns, dual=False)

    return g.fig, trace_options


# @app.callback(
#     Output('side_panels', 'children'),
#     Input('trace_dropdown', 'value')
# )
# def display_side_panel(trace):
#     if (trace != '') and (trace != None):
#         print('returning panelssssssss')
#         return panels[trace]
#     else:
#         return scatter_panel


# @app.callback(
#     Output('scatter_formatting_options', 'style'),
#     Input('btn_sidebar_scatter', 'value'),
#     State('trace_dropdown', 'value')
# )
# def serve_scatter_formatting_options(trace):
#     if g in globals() and g.traces_dict[trace]['trace'].trace_type == "Scatter":
#         return {}
#     else:
#         return {'display': 'none'}

@app.callback(
    Output('scatter_formatting_options', 'style'),
    Output('line_formatting_options', 'style'),
    Input('btn_sidebar_scatter', 'n_clicks'),
    Input('btn_sidebar_lines', 'n_clicks'),
    Input('trace_dropdown', 'value')
)
def serve_graph_formatting_options(scatter_nclicks, lines_nclicks, trace):
    if trace in ['', None]:
        raise PreventUpdate
    time.sleep(0.05)
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    trace_object = g.traces_dict[trace]
    show = {'display': "block"}
    hide = {'display': 'none'}
    if trace_object['trace'].trace_type == "Line" or 'lines' in changed_id:
        return hide, show
    elif trace_object['trace'].trace_type == "Scatter" or 'scatter' in changed_id:
        return show, hide
    return show, hide


# @app.callback(
#     [
#         # Scatter Outputs
#         Output(f"scatter_marker_size", "value"),
#         Output(f"scatter_marker_style_dropdown", "value"),
#         Output(f"scatter_colorpicker", "value"),
#         Output(f"scatter_opacity", "value"),
#         Output(f"scatter_border_width", "value"),
#         Output(f"scatter_colorpicker_marker_border", "value"),
#
#         #Conditional Outputs
#         Output(f"conditional-change-options", "value"),
#         Output(f"conditional-change-operators", "value"),
#         Output(f"conditional-change-columns", "value"),
#         Output(f"conditional-value", "value"),
#     ],
#     Input(f"trace_dropdown", 'value')
# )
# def update_scatter_panel_data(trace):
#     if trace in ['', None]:
#         raise PreventUpdate
#     trace_object = g.traces_dict[trace]
#     if trace_object['trace'].trace_type == "Scatter":
#         settings = trace_object['settings']
#         return [settings['Marker Size'], settings['Marker Symbol'], settings['Marker Color'], settings['Opacity'],
#                 settings[
#                     'Marker Border Width'], settings['Marker Border Color'], settings['Change'], settings[
#                     'Operator'], settings['Column'], settings['Condition']]

@app.callback(
    [
        # Scatter Outputs
        Output(f"scatter_marker_size", "value"),
        Output(f"scatter_marker_style_dropdown", "value"),
        Output(f"scatter_colorpicker", "value"),
        Output(f"scatter_opacity", "value"),
        Output(f"scatter_border_width", "value"),
        Output(f"scatter_colorpicker_marker_border", "value"),

    ],
    Input(f"trace_dropdown", 'value')
)
def update_scatter_panel_data(trace):
    if trace in ['', None]:
        raise PreventUpdate
    trace_object = g.traces_dict[trace]
    if trace_object['trace'].trace_type != "Scatter":
        raise PreventUpdate
    settings = trace_object['settings']
    return [settings['Marker Size'], settings['Marker Symbol'], settings['Marker Color'], settings['Opacity'],
            settings['Marker Border Width'], settings['Marker Border Color']]


@app.callback(
    [
        # Line Outputs
        Output("line_width", "value"),
        Output("line_colorpicker", "value"),
        Output("line_opacity", "value"),
        Output("line_mode_dropdown", "value"),
        Output("line_marker_style_dropdown", "value"),
        Output('line_marker_size', 'value'),
        Output("line_dash_dropdown", "value"),
        Output("line_gaps_dropdown", "value"),

    ],
    Input(f"trace_dropdown", 'value')
)
def update_line_panel_data(trace):
    if trace in ['', None]:
        raise PreventUpdate
    trace_object = g.traces_dict[trace]
    if trace_object['trace'].trace_type != "Line":
        raise PreventUpdate
    settings = trace_object['settings']
    return [settings['Line Width'], settings['Line Color'], settings['Opacity'], settings['Mode'],
            settings['Marker Symbol'], settings['Marker Size'],settings['Dash'],settings['Connect Gaps']]



@app.callback(
    [
        #Conditional Outputs
        Output(f"conditional-change-options", "value"),
        Output(f"conditional-change-operators", "value"),
        Output(f"conditional-change-columns", "value"),
        Output(f"conditional-value", "value"),
    ],
    Input(f"trace_dropdown", 'value')
)
def update_conditional_panel_data(trace):
    if trace in ['', None]:
        raise PreventUpdate
    trace_object = g.traces_dict[trace]
    settings = trace_object['settings']
    return [settings['Change'], settings['Operator'], settings['Column'], settings['Condition']]


@app.callback(
    Output({"type": "change_to", "index": ALL}, "value"),
    Input(f"trace_dropdown", 'value')
)
def update_change_to(trace):
    if trace in ['', None]:
        raise PreventUpdate
    settings = g.traces_dict[trace]['settings']
    # print(f'trace check {trace}')
    # print(f'trace To {settings["To"]}')
    if len(settings['To']) == 0:
        return dash.no_update
    else:
        # print(f'settings[To] {settings["To"]}')
        return settings['To']


@app.callback(
    Output('conditional-change-options', 'options'),
    Input('btn_sidebar_scatter', 'n_clicks'),
    Input('btn_sidebar_lines', 'n_clicks'),
    Input('trace_dropdown', 'value')
)
def update_conditional_change_options(scatter_btn, line_btn, trace):
    if trace in ['', None]:
        raise PreventUpdate
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    trace_object = g.traces_dict[trace]
    if trace_object['trace'].trace_type == 'Line' or 'btn_sidebar_lines' in changed_id:
        return line_conditional_dropdown_options()
    elif trace_object['trace'].trace_type == "Scatter" or 'btn_sidebar_scatter' in changed_id:
        return scatter_conditional_dropdown_options()

    return []


@app.callback(
    Output("conditional-change-columns", "options"),
    Input("output-data-upload", "children"),
)
def update_conditional_cols(contents):
    return df_column_dropdown_options()


@app.callback(
    Output("conditional-change-to", "children"),
    Input("conditional-change-options", "value"),
    State('trace_dropdown', 'value')
)
def update_change_to_options(option, trace):
    if trace in ['', None]:
        raise PreventUpdate
    trace_object = g.traces_dict[trace]
    # if trace_object['trace'].trace_type == "Scatter":
    return conditional_change_to_options(option)


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
    else:
        raise PreventUpdate


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find("{") + 1: name_part.rfind("}")]

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

    return dff.iloc[page * size: (page + 1) * size].to_dict("records"), tooltip_data


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
    app.run_server(debug=True, port=8000, host="127.0.0.1", dev_tools_props_check=False)
