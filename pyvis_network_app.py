import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
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
    return 'parent' if simple_path[i] == edge.parent_fos_name else 'children'


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
select_all = st.checkbox('Select all paths: ', 'Yes')

input_cols = st.columns(2)
with input_cols[0]:
    st.markdown("<h2 style='text-align: center; color: white;'>From</h2>", unsafe_allow_html=True)
    selected_fos1 = st.selectbox('', [''] + st.session_state.all_foses, key=0).lower()

with input_cols[1]:
    st.markdown("<h2 style='text-align: center; color: white;'>To</h2>", unsafe_allow_html=True)
    selected_fos2= st.selectbox('', [''] + st.session_state.all_foses, key=1).lower()

# st.markdown("<h2 style='text-align: center; color: white;'>Choose nodes to go deeper</h2>", unsafe_allow_html=True)
# last_selected_foses = st.session_state.selected_foses
# selected_foses = st.multiselect('', st.session_state.all_foses,
#                                 default=st.session_state.selected_foses)
# st.session_state.rerun_idx += 1
# if st.session_state.rerun_idx % 2 == 0:
#     st.experimental_rerun()

# for fos in selected_foses:
#     if fos not in st.session_state.selected_foses:
#         st.session_state.selected_foses.append(fos)

# with open('selected_foses.json', 'w') as f:
#     json.dump(st.session_state.selected_foses, f)

if selected_fos1 and selected_fos2:
    G = nx.Graph(list(children_fos_df[['children_fos_name', 'parent_fos_name']].to_records(index=False)))
    if max_n == 'shortest path':
        simple_paths = nx.all_shortest_paths(G, source=selected_fos1, target=selected_fos2)
    else:
        simple_paths = nx.all_simple_paths(G, source=selected_fos2, target=selected_fos2, cutoff=max_n)

    labels_paths = {f'Length: {len(path)}. ' + ' -- '.join(path): path for path in simple_paths}
    
    if select_all:
        selected_paths = list(labels_paths.keys())
    else:
        selected_paths = st.multiselect('', [''] + list(labels_paths.keys()), key=2)


# results = {}
# for path in simple_paths:
#     result_entities = get_children(get_entity_by_name(request))
#     result_df = fos_df.loc[fos_df[fos_df.entity.isin(result_entities)].index].sort_values('rank').iloc[:max_n]
#     results[request] = result_df
# foses = [name for df in results.values() for name in df.name]

# for fos in foses:
#     if fos not in st.session_state.all_foses:
#         st.session_state.all_foses.append(fos)
    if selected_paths:
        G = nx.DiGraph()
        for path_label in selected_paths:
            simple_path = labels_paths[path_label]
            for i in range(len(simple_path)-1):
                fos1, fos2 = simple_path[i], simple_path[i+1]
                if get_edge_type(fos1, fos2) == 'parent':
                    G.add_edge(fos1, fos2)
                else:
                    G.add_edge(fos2, fos1)
#     if len(results[request]) == 0:
#         G.add_edge(request, request)

# results = {}
# for request in selected_foses:
#     result_entities = get_parents(get_entity_by_name(request))
#     result_df = fos_df.loc[fos_df[fos_df.entity.isin(result_entities)].index].sort_values('rank').iloc[:max_n]
#     results[request] = result_df
# foses = [name for df in results.values() for name in df.name]

# for fos in foses:
#     if fos not in st.session_state.all_foses:
#         st.session_state.all_foses.append(fos)

# for request in selected_foses:
#     for name in results[request].name:
#         G.add_edge(name, request)

        nt = Network(
            directed=True,
            height='1020px',
            width='100%',
            bgcolor='#222222',
            font_color='white'
        )
        nt.from_nx(G)
        for node in nt.nodes:
            if node['label'] in [selected_fos1, selected_fos2]:
    #             node['size'] = 20
                node['color'] = 'red'
    
        nt.repulsion(node_distance=420, central_gravity=0.3,
                     spring_length=110, spring_strength=0.2,
                     damping=0.95)
        
        nt.save_graph(f'html_files/pyvis_graph.html')
        HtmlFile = open(f'html_files/pyvis_graph.html', 'r', encoding='utf-8')
        components.html(HtmlFile.read(), height=1050)

# cols = st.columns(11)
# with cols[int(len(cols) / 2)]:
#     st.button('Go dipper!')

##############################################################################################################################
