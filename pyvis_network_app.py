import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import json
import networkx as nx
from pyvis.network import Network

st.set_page_config(layout="wide")

# Read dataset (CSV)
# df_interact = pd.read_csv('data/processed_drug_interactions.csv')

# # Set header title
# st.title('Network Graph Visualization of Drug-Drug Interactions')

# # Define list of selection options and sort alphabetically
# drug_list = ['Metformin', 'Glipizide', 'Lisinopril', 'Simvastatin',
#             'Warfarin', 'Aspirin', 'Losartan', 'Ibuprofen']
# drug_list.sort()

# # Implement multiselect dropdown menu for option selection (returns a list)
# selected_drugs = st.multiselect('Select drug(s) to visualize', drug_list)

# # Set info message on initial site load
# if len(selected_drugs) == 0:
#     st.text('Choose at least 1 drug to start')

# # Create network graph when user selects >= 1 item
# else:
#     df_select = df_interact.loc[df_interact['drug_1_name'].isin(selected_drugs) | \
#                                 df_interact['drug_2_name'].isin(selected_drugs)]
#     df_select = df_select.reset_index(drop=True)

#     # Create networkx graph object from pandas dataframe
#     G = nx.from_pandas_edgelist(df_select, 'drug_1_name', 'drug_2_name', 'weight')

#     # Initiate PyVis network object
#     drug_net = Network(
#                        height='400px',
#                        width='100%',
#                        bgcolor='#222222',
#                        font_color='white'
#                       )

#     # Take Networkx graph and translate it to a PyVis graph format
#     drug_net.from_nx(G)

#     # Generate network with specific layout settings
#     drug_net.repulsion(
#                         node_distance=420,
#                         central_gravity=0.33,
#                         spring_length=110,
#                         spring_strength=0.10,
#                         damping=0.95
#                        )

#     # Save and read graph as HTML file (on Streamlit Sharing)
#     try:
#         path = '/tmp'
#         drug_net.save_graph(f'{path}/pyvis_graph.html')
#         HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

#     # Save and read graph as HTML file (locally)
#     except:
#         path = '/html_files'
#         drug_net.save_graph(f'{path}/pyvis_graph.html')
#         HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

# #     Load HTML file in HTML component for display on Streamlit page
#     components.html(HtmlFile.read(), height=435)

# # Footer
# st.markdown(
#     """
#     <br>
#     <h6><a href="https://github.com/kennethleungty/Pyvis-Network-Graph-Streamlit" target="_blank">GitHub Repo</a></h6>
#     <h6><a href="https://kennethleungty.medium.com" target="_blank">Medium article</a></h6>
#     <h6>Disclaimer: This app is NOT intended to provide any form of medical advice or recommendations. Please consult your doctor or pharmacist for professional advice relating to any drug therapy.</h6>
#     """, unsafe_allow_html=True
#     )

##############################################################################################################################
fos_df = pd.read_csv('data/fos_df.csv')
fos_df.dropna(inplace=True)
fos_df.name = fos_df.name.apply(str.lower)
children_fos_df1 = pd.read_csv('data/children_fos_df_part1.csv')
children_fos_df2 = pd.read_csv('data/children_fos_df_part2.csv')
children_fos_df = pd.concat([children_fos_df1, children_fos_df2], ignore_index=True)


if 'all_foses' not in st.session_state:
    st.session_state['all_foses'] = []

if 'selected_foses' not in st.session_state:
    st.session_state['selected_foses'] = []
    
if 'text_input' not in st.session_state:
    st.session_state['text_input'] = ''
    
if 'rerun_idx' not in st.session_state:
    st.session_state['rerun_idx'] = 0


def get_entity_by_name(fos_name):
    return fos_df[fos_df.prep_name == fos_name.lower()].entity.values[0]


def get_edge_type(fos1, fos2):
    edge = children_fos_df[
        (
            (children_fos_df.children_fos_name == fos1)
            &
            (children_fos_df.parent_fos_name == fos2)
        )
        |
        (
            (children_fos_df.children_fos_name == fos2)
            &
            (children_fos_df.parent_fos_name == fos1)
        )
        ].iloc[0]
    return 'parent' if fos1 == edge.parent_fos_name else 'children'


def get_connection_power(name1, name2):
    entity1 = get_entity_by_name(name1)
    entity2 = get_entity_by_name(name2)
    df1 = children_fos_df[(children_fos_df.parent_fos == entity1) & (children_fos_df.children_fos == entity2)]
    if len(df1):
        return df1.iloc[0].connection_power
    else:
        df2 = children_fos_df[(children_fos_df.parent_fos == entity2) & (children_fos_df.children_fos == entity1)]
        if len(df2):
            return df2.iloc[0].connection_power


def check_simple_path(simple_path):
    chain = []
    for i in range(len(simple_path)-1):
        fos1, fos2 = simple_path[i], simple_path[i+1]
        chain.append({'fos1': fos1, 'fos2': fos2, 'edge_type': get_edge_type(fos1, fos2)})

    left_end = chain[0]['fos1']
    for edge in chain:
        if edge['edge_type'] == 'parent':
            left_end = edge['fos2']
        else:
            break
    right_end = chain[-1]['fos2']
    for edge in chain[::-1]:
        if edge['edge_type'] == 'children':
            right_end = edge['fos1']
        else:
            break
#     st.markdown(str(chain) + ' | ' + str(left_end == right_end))
    return left_end == right_end


st.markdown("<h2 style='text-align: center; color: white;'>Enter your query</h2>", unsafe_allow_html=True)

text_request = set(st.text_input('').lower().split())

if text_request != st.session_state['text_input']:
    st.session_state['text_input'] = text_request
    st.session_state['all_foses'] = []
    st.session_state['selected_foses'] = []

fos_df['match_len'] = fos_df.prep_name.apply(lambda name: len(set(name.split()) & text_request))
foses = fos_df[fos_df['match_len'] > 0].sort_values('match_len', ascending=False).name.values.tolist()

for fos in foses:
    if fos not in st.session_state.all_foses:
        st.session_state.all_foses.append(fos)
        
max_n = st.selectbox('Choose max length of a path', ['shortest path'] + list(range(1, 11)))
select_paths_type = st.selectbox('Select paths type:', ['all paths', 'only downstream edges', 'manual'])
log_degree = st.selectbox('Choose degree of logarithm', list(range(1, 10)), index=1)
fos_df['log_power'] = fos_df.power.apply(lambda power: math.log(power, log_degree))
power_dict = dict(fos_df[['name', 'log_power']].to_records(index=False))

input_cols = st.columns(2)
with input_cols[0]:
    st.markdown("<h2 style='text-align: center; color: white;'>From</h2>", unsafe_allow_html=True)
    selected_fos1 = st.selectbox('', [''] + st.session_state.all_foses, key=0).lower()

with input_cols[1]:
    st.markdown("<h2 style='text-align: center; color: white;'>To</h2>", unsafe_allow_html=True)
    selected_fos2 = st.selectbox('', [''] + [fos for fos in st.session_state.all_foses if fos != selected_fos1], key=1).lower()


if selected_fos1 and selected_fos2:
    G = nx.Graph(list(children_fos_df[['children_fos_name', 'parent_fos_name']].to_records(index=False)))
    if max_n == 'shortest path':
        simple_paths = nx.all_shortest_paths(G, source=selected_fos1, target=selected_fos2)
    else:
        simple_paths = nx.all_simple_paths(G, source=selected_fos2, target=selected_fos2, cutoff=max_n)

    labels_paths = {f'Length: {len(path)}. ' + ' -- '.join(path): path for path in simple_paths}
    labels_paths = {k + ' || Downstream' if check_simple_path(path) else k: path for k, path in labels_paths.items()}

    if select_paths_type in ['all paths', 'only downstream edges']:
        selected_paths = list(labels_paths.keys())
    else:
        selected_paths = st.multiselect('', [''] + list(labels_paths.keys()), key=2)

    if selected_paths:
        G = nx.DiGraph()
        for path_label in selected_paths:
            simple_path = labels_paths[path_label]
            if select_paths_type == 'only downstream edges':
                if not check_simple_path(simple_path):
                    continue
            for i in range(len(simple_path)-1):
                fos1, fos2 = simple_path[i], simple_path[i+1]
                edge_type = get_edge_type(fos1, fos2)
                if edge_type == 'parent':
                    G.add_edge(fos1, fos2, label=round(get_connection_power(fos1, fos2), 2))
                else:
                    G.add_edge(fos2, fos1, label=round(get_connection_power(fos2, fos1), 2))

        nt = Network(
            directed=True,
            height='1020px',
            width='100%',
            bgcolor='#222222',
            font_color='white'
        )
        nx.set_node_attributes(G, power_dict, 'size')
        nt.from_nx(G)
        for node in nt.nodes:
            if node['label'] in [selected_fos1, selected_fos2]:
                node['color'] = 'red'


        nt.repulsion(node_distance=420, central_gravity=0.3,
                     spring_length=110, spring_strength=0.2,
                     damping=0.95)
        
        nt.save_graph(f'html_files/pyvis_graph.html')
        HtmlFile = open(f'html_files/pyvis_graph.html', 'r', encoding='utf-8')
        components.html(HtmlFile.read(), height=1050)

##############################################################################################################################
