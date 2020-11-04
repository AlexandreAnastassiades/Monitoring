# pylint: disable-all
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output,State
from app import *
from appbase import app
from collections import deque
X=deque(maxlen=10)
X.append(0)
Y=deque(maxlen=10)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
liste_cont =[]
liste_serv_up=[]
SERVERS.append("34.237.227.172")
for i in range(len(SERVERS)):
    if test_connexion(SERVERS[i],LOGIN_SERVER_ONE,PASS_SERVER_ONE):
        cpu_name,cpu_cores, cpu_cache=get_cpu_name(SERVERS[i], LOGIN_SERVER_ONE, PASS_SERVER_ONE)
        acceuil = dbc.Container(
            [
                dbc.Row(
                    [

                        dbc.Col(
                            [
                                dcc.Link('Machine '+str(i+1), href='/appvisu'+str(i)),
                                html.H2('Serveur '+SERVERS[i]+' en marche'),
                                html.H3('Modele du CPU: '+cpu_name, id ="name_CPU"),
                                html.H3('Nombre de coeurs: '+cpu_cores, id ="cpu_cores"),
                                html.H3('Taille du cache: '+cpu_cache,"cpu_cache")
                            ],
                            md=6,
                        ),
                    ]
                )
            ],
            className="mt-4",
        )
        liste_cont.append(acceuil)
        liste_serv_up.append(i)
    else:
        acceuil = dbc.Container(
            [
                dbc.Row(
                    [

                        dbc.Col(
                            [
                                html.H2('Serveur '+SERVERS[i]+' arrété (machine '+str(i+1)+')')
                            ],
                            md=6,
                        ),
                    ]
                )
            ],
            className="mt-4",
        )
        liste_cont.append(acceuil)

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/appAccueil':
        return liste_cont
    else:
        for j in range(len(SERVERS)):
            if pathname == '/appvisu'+str(j):
                return [navbar,liste_aff_serv[j]]


liste_aff_serv = [i for i in range(len(SERVERS))]

navbar =  dbc.NavbarSimple(
    dcc.Link('Accueil', href='/appAccueil'),
    brand="Demo",
    brand_href="#",
    sticky="top",
)

for serv in liste_serv_up:

    cpu_name,cpu_cores, cpu_cache=get_cpu_name(SERVERS[serv], LOGIN_SERVER_ONE, PASS_SERVER_ONE)

    mem_total, mem_free, mem_available=get_ram_data(SERVERS[serv], LOGIN_SERVER_ONE, PASS_SERVER_ONE)

    error,working,total = get_access_log_data_error_pages(SERVERS[serv], LOGIN_SERVER_ONE, PASS_SERVER_ONE)

    dict_connex_hour = get_connexion_per_hour(SERVERS[serv], LOGIN_SERVER_ONE, PASS_SERVER_ONE)
    liste_nb_connex=[]
    liste_hour_connex=[]
    for key in dict_connex_hour.keys():
        liste_hour_connex.append(key)
    for valeur in dict_connex_hour.values():
        liste_nb_connex.append(valeur)
    dict_connex_hour_404=get_connexion_404_per_hour(SERVERS[serv], LOGIN_SERVER_ONE, PASS_SERVER_ONE)
    liste_nb_connex_404=[]
    liste_hour_connex_404=[]
    for key in dict_connex_hour_404.keys():
        liste_hour_connex_404.append(key)
    for valeur in dict_connex_hour_404.values():
        liste_nb_connex_404.append(valeur)

    dict_connex_hour_404 = get_connexion_404_rate_per_hour(SERVERS[serv], LOGIN_SERVER_ONE, PASS_SERVER_ONE)
    liste_nb_connex_404=[]
    liste_hour_connex_404=[]
    for key in dict_connex_hour_404.keys():
        liste_hour_connex_404.append(key)
    for valeur in dict_connex_hour_404.values():
        liste_nb_connex_404.append(valeur)

    body = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2('Utilisation CPU'),
                            html.H3('Modele du CPU: '+cpu_name, id ="name_CPU"),
                            html.H3('Nombre de coeurs: '+cpu_cores, id ="cpu_cores"),
                            html.H3('Taille du cache: '+cpu_cache,"cpu_cache"),
                            dcc.Graph(id='graphCPU',animate=True),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.H2('Utilisation RAM'),
                            html.H3('Memoire totale: '+str(mem_total)+'kB', id="mem_tot"),
                            dcc.Graph(id='graphRAM',figure={'data':[{'values':[mem_free,mem_total],'type':'pie'}]}),
                            dcc.Interval(id='graph-update',interval=5*1000,n_intervals=0)
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.H2('Erreurs 404'),
                            dcc.Graph(id='graph404',figure={"data": [{"x": ["Erreur 404", "Existing", "Total"], "y": [error,working,total],'type':'bar','name':'requète par heure'}]}),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.H2('Connection'),
                            dcc.Graph(id='graphConnection',figure={"data": [{"x": liste_hour_connex, "y": liste_nb_connex},{"x": liste_hour_connex_404, "y": liste_nb_connex_404,'name':"réponses 404 par heure"}]}),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.H2('Connection'),
                            dcc.Graph(id='graphConnection404',figure={"data":[{"x": liste_hour_connex_404, "y": liste_nb_connex_404,'name':"ratio 404 par heure"}]}),
                        ],
                        md=6,
                    ),
                ]
            )
        ],
        className="mt-4",
    )
    liste_aff_serv[serv]=body



layout = html.Div([navbar])
@app.callback(
    Output(component_id='graphCPU', component_property='figure'),
    [Input(component_id='graph-update', component_property='n_intervals')]
)
def update_output_divCPU(i):
    X.append(X[-1]+1)
    Y.append(get_processor_used(SERVERS[serv], LOGIN_SERVER_ONE, PASS_SERVER_ONE))
    goLayout=plotly.graph_objs.Layout(xaxis=dict(range=[min(X),max(X)]),yaxis=dict(range=[0,100]),title="Utilisation du CPU")
    data=plotly.graph_objs.Scatter(x=list(X), y=list(Y), name='Scatter', mode= 'lines+markers')
    return{'data':[data],'layout':goLayout}

@app.callback(
    Output(component_id='graphRAM', component_property='figure'),
    [Input(component_id='graph-update', component_property='n_intervals')]
)
def update_output_divRAM(i):
    mem_total, mem_free, mem_available=get_ram_data(SERVERS[serv], LOGIN_SERVER_ONE, PASS_SERVER_ONE)
    return{'data':[{'values':[mem_free,mem_total-mem_free],'labels':['Memoire libre','Memoire utilisee'],'type':'pie'}],'layout':{'title':"Utilisation de la RAM"}}

if __name__ == '__main__':
    app.run_server(host="0.0.0.0",debug=True,port=8050)