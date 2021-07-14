from logging import disable
import dash_html_components as html

from dash_core_components.Dropdown import Dropdown
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import dash
import psycopg2 
import dash_table
import datetime
import dash_core_components as dcc

import base64
import datetime
import io





conn = psycopg2.connect("host='63.48.7.23' port='5432' dbname='kpi' user='kpi' password='Welcome!'")

print('Opened database successfully')
cur = conn.cursor()
 

# cur.execute("SELECT * from icmms_mo LIMIT 10")
# print(cur.fetchall())


# To fetch data for total column for January 1st 
cur.execute("SELECT total, \"Date\" FROM icmms_mo where \"Date\"::text like '%-01-01'")
rows = cur.fetchall()

u = pd.DataFrame(rows, columns=['t','v'])
fig_line = px.line(data_frame= u, y = 't', x = 'v', title='Total ICMMS_MO for last 10 years on January 1st')
# fig_line.show()

# To fetch data for Christmas day from ICMMS_MO database
cur.execute("SELECT total, \"Date\" FROM icmms_mo where \"Date\"::text like '%-12-25'")
lines = cur.fetchall()

a = pd.DataFrame(lines, columns=['b','c'])
fig_lines = px.line(data_frame= a, y = 'b', x = 'c', title='Total ICMMS_MO for last 10 years on Christmas')
# fig_lines.show()



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.H1("KPI's for Holiday Capacity reporting"),

    dcc.Dropdown(
    id = 'holidayselector',
    options=[
        {'label': 'New Year\'s', 'value': 'NY'},
        {'label': 'Christmas', 'value': 'b'},
        {'label': 'Independence', 'value': 'IN'},
        {'label': 'Valentine\'s', 'value': 'VAL'}
    ],
    value=['NY', 'b','IN','VAL'],
    placeholder= 'Please select...',
    
    ) ,
#    dcc.Graph(id = 'newyears', figure  =  px.line(data_frame= u, y = 't', x = 'v', 
#    title='Total messages for last 10 years on January 1st')),

   dcc.Graph(id ='christmas'),
   
#    To import CSV files into dashboard
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    
]
)

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified')            
              )

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


#callback for christmas
@app.callback( dash.dependencies.Output(component_id ='christmas',component_property='figure'),
              [ dash.dependencies.Input(component_id ='holidayselector',component_property='b')]

)  
def update_graph(holidayselector):
    print('hello')
    print(a.info())  
    dff=a,

    linegraph = px.line(
        a,
         y = 'b', x = 'c', title='Total ICMMS_MO for last 10 years on Christmas'
   )

    return(linegraph)
    


if __name__ == '__main__':
    app.run_server()