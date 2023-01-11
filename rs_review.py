import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
# from st_draggable_list import DraggableList

# import numpy as np
# import os
# from sklearn import metrics
import plotly.express as px
# import json

st.set_page_config(
    page_title="Chewy Related Search Opportunities",
    page_icon="✅",
    layout="wide",
)

# Load data
df = pd.read_csv('related_search_full_run.csv')
df['H1_BC1'] = df['H1 Breadcrumb Structure'].apply(lambda x: x.split("->")[0] if len(x.split("->")) > 0 else '')
df['H1_BC2'] = df['H1 Breadcrumb Structure'].apply(lambda x: x.split("->")[1] if len(x.split("->")) > 1 else '')
df['H1_BC3'] = df['H1 Breadcrumb Structure'].apply(lambda x: x.split("->")[2] if len(x.split("->")) > 2 else '')
df['H1_BC4'] = df['H1 Breadcrumb Structure'].apply(lambda x: x.split("->")[3] if len(x.split("->")) > 3 else '')
df['H1_BC5'] = df['H1 Breadcrumb Structure'].apply(lambda x: x.split("->")[4] if len(x.split("->")) > 4 else '')
df['Edited Related H1'] = df['anchor_text']
df['new_rank'] = df['Ranking']
# df.drop(columns=['Unnamed: 0'], inplace=True)

# Create a list of all the columns
cols = df.columns.tolist()


# Collects user input features into dataframe
def user_input_features():
    # sidebar instructions
    st.sidebar.header('H1 Filter')
    filter_msg1 = '''<p style="color:Grey; font-size: 12px;">You can apply filters to narrow down the H1s. You have to 
        select a H1 after applying filters. If you want to see all the H1s, leave all the filters blank. </p>'''
    filter_msg2 = '''<p style="color:Grey; font-size: 12px;"> (Note: In Breadcrumb filter, the following select 
    options will be determined by the previous selections.) </p>'''
    st.sidebar.markdown(filter_msg1, unsafe_allow_html=True)
    st.sidebar.markdown(filter_msg2, unsafe_allow_html=True)

    # keyword filter
    keyword = st.sidebar.text_input(label="Keyword", placeholder="Search by Keywords...")
    if keyword:
        kw_df = df[df['H1'].apply(lambda x: keyword.lower() in x.lower())]
    else:
        kw_df = df
    # category filter
    category = []
    breadcrumb_1 = st.sidebar.selectbox(label="Breadcrumb 1",
                                        options=["Choose ..."] + sorted(kw_df['H1_BC1'].unique().tolist()))
    if breadcrumb_1 and breadcrumb_1 != "Choose ...":
        category.append(breadcrumb_1)
        df_breadcrumb_1 = kw_df[kw_df['H1_BC1'] == breadcrumb_1]
        bc2_list = df_breadcrumb_1['H1_BC2'].unique().tolist()
        if '' in bc2_list:
            bc2_list.remove('')
        bc2_list = ["Choose ..."] + sorted(list(set(bc2_list)))
        if bc2_list != ['Choose ...']:
            breadcrumb_2 = st.sidebar.selectbox(label="Breadcrumb 2", options=bc2_list)
        else:
            breadcrumb_2 = st.sidebar.selectbox(disabled=True, options=bc2_list, label="Breadcrumb 2")
        if breadcrumb_2 and breadcrumb_2 != 'Choose ...':
            category.append(breadcrumb_2)
            df_breadcrumb_2 = df_breadcrumb_1[df_breadcrumb_1['H1_BC2'] == breadcrumb_2]
            bc3_list = df_breadcrumb_2['H1_BC3'].unique().tolist()
            if '' in bc3_list:
                bc3_list.remove('')
            bc3_list = ["Choose ..."] + sorted(list(set(bc3_list)))
            if bc3_list != ['Choose ...']:
                breadcrumb_3 = st.sidebar.selectbox(label="Breadcrumb 3", options=bc3_list)
            else:
                breadcrumb_3 = st.sidebar.selectbox(disabled=True, options=bc3_list, label="Breadcrumb 3")
            if breadcrumb_3 and breadcrumb_3 != 'Choose ...':
                category.append(breadcrumb_3)
                df_breadcrumb_3 = df_breadcrumb_2[df_breadcrumb_2['H1_BC3'] == breadcrumb_3]
                bc4_list = df_breadcrumb_3['H1_BC4'].unique().tolist()
                if '' in bc4_list:
                    bc4_list.remove('')
                bc4_list = ["Choose ..."] + sorted(list(set(bc4_list)))
                if bc4_list != ['Choose ...']:
                    breadcrumb_4 = st.sidebar.selectbox(label="Breadcrumb 4", options=bc4_list)
                else:
                    breadcrumb_4 = st.sidebar.selectbox(disabled=True, label="Breadcrumb 4", options=bc4_list)

                if breadcrumb_4 and breadcrumb_4 != 'Choose ...':
                    category.append(breadcrumb_4)
                    df_breadcrumb_4 = df_breadcrumb_3[df_breadcrumb_3['H1_BC4'] == breadcrumb_4]
                    bc5_list = df_breadcrumb_4['H1_BC5'].unique().tolist()
                    if '' in bc5_list:
                        bc5_list.remove('')
                    bc5_list = ["Choose ..."] + sorted(list(set(bc5_list)))
                    if bc5_list != ['Choose ...']:
                        breadcrumb_5 = st.sidebar.selectbox(label="Breadcrumb 5", options=bc5_list)
                    else:
                        breadcrumb_5 = st.sidebar.selectbox(disabled=True, options=bc5_list, label="Breadcrumb 5")
                    if breadcrumb_5 and breadcrumb_5 != 'Choose ...':
                        category.append(breadcrumb_5)
                        df_breadcrumb_5 = df_breadcrumb_4[df_breadcrumb_4['H1_BC5'] == breadcrumb_5]
                        data = df_breadcrumb_5
                    else:
                        data = df_breadcrumb_4
                else:
                    data = df_breadcrumb_3
            else:
                data = df_breadcrumb_2
        else:
            data = df_breadcrumb_1
    else:
        data = kw_df
    return keyword, category, [], data

filter_bar = user_input_features()
keyword_filter = filter_bar[0]
breadcrumb_filter = filter_bar[1]
h1_selected = filter_bar[2]
filtered_data = filter_bar[3]


def make_grid(cols, rows):
    grid = [0] * cols
    for i in range(cols):
        with st.container():
            grid[i] = st.columns(rows)
    return grid

page_length = 12
# Content of the page
# home page (display two plots)
if 'show' not in st.session_state:
    st.session_state.show = False
if "selected_h1" not in st.session_state:
    st.session_state.selected_h1 = ""
#
# def c():
#     st.session_state.show = True
#
# b1 = st.button("Show More", on_click=c)
# if st.session_state.show == False:
#     print('check')

if breadcrumb_filter == [] and keyword_filter == "":
    st.subheader("Overview Status of the Related Search Results")
    a = df.drop_duplicates(subset=['H1'])
    st.write(px.pie(a, names='H1_BC1'))
    x = df['H1'].value_counts().to_frame()
    st.write(px.histogram(x, x="H1"))


# after applied filter
else:
    kw_select = keyword_filter if keyword_filter else "None"
    st.caption(f"You have selected following filters:")
    st.caption(f"Keyword: **{kw_select}**, Breadcrumb: **{'->'.join(breadcrumb_filter)}**")
    # h1s = filtered_data['H1'].unique().tolist()
    h1s = filtered_data['H1'].unique().tolist()
    # print("fjdaofnasdkfnasdfkafnakdlfanfladn")
    st.caption(f"There are **{len(h1s)}** H1s in total.")
    page_bar = st.selectbox(label="Page", options=[i for i in range(1, len(h1s) // page_length + 2)])
    # print(h1s, page_bar, range(1, len(h1s) // page_length + 1))
    h1_list_on_page = h1s[(page_bar - 1) * page_length: page_bar * page_length]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        a = [st.button(label=h1_list_on_page[i]) for i in range(0, len(h1_list_on_page), 4)]
    with col2:
        b = [st.button(label=h1_list_on_page[i]) for i in range(1, len(h1_list_on_page), 4)]
    with col3:
        c = [st.button(label=h1_list_on_page[i]) for i in range(2, len(h1_list_on_page), 4)]
    with col4:
        d = [st.button(label=h1_list_on_page[i]) for i in range(3, len(h1_list_on_page), 4)]
    h1_button_on_page = a + b + c + d
    h1_1 = h1_button_on_page[0: len(h1_button_on_page): 3]
    h1_2 = h1_button_on_page[1: len(h1_button_on_page): 3]
    h1_3 = h1_button_on_page[2: len(h1_button_on_page): 3]
    h1_button_on_page = h1_1 + h1_2 + h1_3
    # h1_button_on_page = [st.button(label=h1) for h1 in h1_list_on_page]
    print(h1_button_on_page)
    if True in h1_button_on_page:
        h1_selected = h1_list_on_page[h1_button_on_page.index(True)]
        st.session_state.selected_h1 = h1_selected
        st.session_state.show = True
        print(st.session_state.selected_h1, st.session_state.show)

    if st.session_state.show:
        print(st.session_state.selected_h1)
        st.subheader(f"Selected H1: {st.session_state.selected_h1}")
        st.write(filtered_data[filtered_data['H1'] == st.session_state.selected_h1]['H1 URL'].values[0])
        for i, row in filtered_data[filtered_data['H1'] == st.session_state.selected_h1].sort_values(by=['new_rank']).reset_index().iterrows():
            # print('this is running!!!', filtered_data['new_rank'].unique().tolist())
            label = f"{i + 1} - {row['anchor_text']}"
            with st.expander(label=label, expanded=False):
                url = row['Related Search URL']
                breadcrumb = [row['Related Breadcrumb Depth 1'], row['Related Breadcrumb Depth 2'],
                              row['Related Breadcrumb Depth 3'], row['Related Breadcrumb Depth 4'],
                              row['Related Breadcrumb Depth 5']]
                breadcrumb = [x for x in breadcrumb if str(x) != 'nan']
                mygrid = make_grid(2, 2)
                mygrid[0][0].write(f"- Breadcrumb: {' -> '.join(breadcrumb)}")
                mygrid[0][1].write(f"- Similarity: {row['Similarity']}")
                mygrid[1][0].write(f"- Related URL: {url}")
                mygrid[1][1].write(f"- Page Type: {row['page_type']}")
                edit_anchor_text = st.text_input(label="Edit Anchor Text", value=row['anchor_text'])
                if edit_anchor_text:
                    tmp_idx = df[(df['H1'] == st.session_state.selected_h1) & (df['Related H1'] == row['Related H1'])].index[0]
                    df.loc[tmp_idx, 'Edited Related H1'] = edit_anchor_text
                    df.to_csv('related_search_full_run.csv', index=False)
        print('check check here!!!')
        # st.caption("If you want to re-rank the anchor texts, please drag and drop the anchor texts in the order you want.")
        # tmp_anchor_text = filtered_data[filtered_data['H1'] == st.session_state.selected_h1]['anchor_text'].unique().tolist()
        # tmp_data = []
        # for i, anchor_text in enumerate(tmp_anchor_text):
        #     tmp_dict = {'id': anchor_text, 'order': i + 1, 'name': anchor_text}
        #     tmp_data.append(tmp_dict)
        # anchor_text_list = DraggableList(tmp_data)
        # if anchor_text_list:
        #     for order in anchor_text_list:
        #         tmp_idx = df[(df['H1'] == st.session_state.selected_h1) & (df['anchor_text'] == order['name'])].index[0]
        #         df.loc[tmp_idx, "new_rank"] = order['order'] + 1
        #         df.to_csv('related_search_full_run.csv', index=False)
    else:
        viz_1_data = filtered_data.copy()
        viz_1_data.drop_duplicates(subset=['H1'], inplace=True)
        viz_1_data['Related Breadcrumb Structure'] = viz_1_data[
            ['Related Breadcrumb Depth 1', 'Related Breadcrumb Depth 2', 'Related Breadcrumb Depth 3',
             'Related Breadcrumb Depth 4', 'Related Breadcrumb Depth 5', 'Related Breadcrumb Depth 6']].values.tolist()
        viz_1_data['Related Breadcrumb Structure'] = viz_1_data['Related Breadcrumb Structure'].apply(
            lambda z: '->'.join([bc for bc in z if str(bc) != 'nan']))
        viz_1_data = viz_1_data.groupby(['Related Breadcrumb Structure'])['H1'].count().reset_index()
        st.write(px.bar(viz_1_data, x='Related Breadcrumb Structure', y='H1'))
st.sidebar.download_button('Download Current Dataframe', df.to_csv(), 'related-search-full-run.csv')
