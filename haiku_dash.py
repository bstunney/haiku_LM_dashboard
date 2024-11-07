

from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.subplots import make_subplots
import time
import base64

import haiku_app

def haikus(word):
    return ["this is the first line", "Here is placed the second line", "The third Line is here"]

def main():


    # make app
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    # stylesheet with the .dbc class
    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
    app = Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL, dbc.themes.BOOTSTRAP, dbc_css])

    channel_input = dcc.Input(
        id="input-value",
        type="text",
        value="",
        size="lg",
        style={"font-size": "1.6rem", "margin-top": ".5px"},
        className="mb-3"
    )
    button = dbc.Button(
        id="search-button",
        children="Search",
        n_clicks=0,
        size="lg",
        style={"font-size": "1.2rem", "margin-left": "12px", "margin-top": "-8px"},
        color="primary",
        className="me-1",
    )

    header = html.H1("NN and N-Gram Haiku Generator",
                     style={"margin-top": "50px"})

    caption = html.H6("Generate Haikus by Topic",
                      style={"margin-top": "10px"})

    five1 = html.H6(id= "firstline",
                    children="11111111",
                      style={"margin-top": "10px"})

    seven1 = html.H6(id= "secondline",
                    children="2222222222",
                      style={"margin-top": "10px"})

    five2 = html.H6(id= "thirdline",
                    children="33333333333",
                      style={"margin-top": "10px"})



    img = html.Img(id= "image", src="")

    collapse1 = html.Div(
        [
            dbc.Collapse(
                dbc.Card(dbc.CardBody([five1, html.Div(className='gap'), seven1, html.Div(className='gap'), five2
                                       , html.Div(className='gap'), img])),
                id="collapse1",
                is_open=True,
            ),
        ]
    )



    app.layout = dbc.Container(
        [

        # top line of Dash
        dbc.Row([
            dbc.Col(
                # YouTube Channel Profanity Rating
                [header,caption, channel_input, button, collapse1],
                #[collapse, header, caption, channel_input, button, html.Div(className='gap'),
                 #search_results],
                lg=6
            )
        ],
            justify = "center",
            style = dict(textAlign="center"),
            className="d-flex justify-content-center",
        ),],
        className="p-4",
        fluid = True)

    @app.callback(
        Output("search-button", "style"),
        Input("input-value", "value"),
    )
    def change_button_color(channel_input):
        if channel_input != "":
            return {"font-size": "1.2rem", "margin-left": "12px", "margin-top": "-8px", "background-color": "red"}
        else:
            return {"font-size": "1.2rem", "margin-left": "12px", "margin-top": "-8px", 'background-color': 'gray'}

    @app.callback(
        Output("search-button", "n_clicks"),
        Output('firstline', 'children'),
        Output('secondline', 'children'),
        Output('thirdline', 'children'),
        Output('image', 'src'),
        Input("search-button", "n_clicks"),
        Input("input-value", "value"),
    )

    def init_countdown_store(n_clicks, search_results):

        lines = ["", "", ""]
        imgsrc = ""
        #df = pd.DataFrame(biglst, columns=['Name', "Description", "ID"])
        if n_clicks > 0:
            lines = haiku_app.return_haikus(search_results)[0]

            haiku_app.get_image(lines[0]+ lines[1]+ lines[2])
            test_base64 = base64.b64encode(open("image.png", 'rb').read()).decode('ascii')
            imgsrc = 'data:image/png;base64,{}'.format(test_base64)
            # df['ID'] = df['ID'].str.slice(0, 3)
        return 0, lines[0], lines[1], lines[2], imgsrc
        #else:
        #    return lines[0], lines[1], lines[2], 0

    """
    @app.callback(Output('collapse1', 'is_open'),
                  Output('five1', 'children'),
                  Output('seven1', 'children'),
                  Output('five2', 'children'),
                  Input('search-button', 'n_clicks'),
                  [State('collapse1', 'is_open')])
    def toggle_collapse1(n,  is_open1):

        if n > 0:
            
            num_phrases, prop_phrases = badwords.get_channel_stats(data[derived_virtual_selected_rows[0]]['ID'])
            num = "Average Number of Explicit Words/Phrases Used per Video: " + str(num_phrases)
            prop = "Average Percentage of Explicit Words/Phrases per Video: " + str(
                round(prop_phrases * 100, 2)) + "%"
            return not is_open1, not is_open2, data[derived_virtual_selected_rows[0]]['Name'], num, prop, \
                   "Search Channels", None, 0
        else:
            return is_open1, "", "", ""
    """


    # run server
    app.run_server(debug=True)

if __name__ == "__main__":
    main()