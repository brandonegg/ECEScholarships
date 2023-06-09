# pylint: disable=too-many-nested-blocks, too-many-branches
"""
Home: Primary page for viewing student data, leaving reviews, and exporting selections
"""
import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import (
    JsCode,
    GridOptionsBuilder,
    AgGrid,
    ColumnsAutoSizeMode,
    GridUpdateMode,
)

from scholarship_app.utils.html import redirect
from scholarship_app.managers.sharepoint.sharepoint_session import SharepointSession
from scholarship_app.utils.scholarship_management import groups_string_to_list
from scholarship_app.utils.output import get_appdata_path
from scholarship_app.managers.sharepoint.file_versioning import DataManager, DataType
from scholarship_app.sessions.session_manager import SessionManager
from scholarship_app.components.home.graphing import distribution_graph_expander
from scholarship_app.components.home.statistics import main_data_statistics
from scholarship_app.components.home.review import submit_review_expander

# Default setting for Streamlit page
st.set_page_config(layout="wide")

SHAREPOINT = SharepointSession(st.session_state)
if not SHAREPOINT.is_signed_in():
    redirect("/Account")

MAIN_DATA = DataManager(st.session_state, DataType.MAIN, SHAREPOINT)
SESSION = SessionManager(st.session_state, "home", "download")

js = JsCode(
    """
 function(event) {
    const api = event.api; 
     window.addEventListener('clear.rows', (e) => {
         api.deselectAll(); 
     });    
 }
 """
)
jscode = JsCode(
    """
            function(params) {
                if (params.data.Review === 'Yes') {
                    return {
                        'color': 'white',
                        'backgroundColor': '#017252'
                    }
                }
                if (params.data.Review === 'No') {
                    return {
                        'color': 'white',
                        'backgroundColor': '#8E0303'
                    }
                }
                if (params.data.Review === 'Maybe') {
                    return {
                        'color': 'white',
                        'backgroundColor': '#A2A200'
                    }
                }
            };
            """
)

# Start of displayed page
st.title("Home")
st.header("Review Applicants")


def error_view():
    """
    Displays no data error
    """
    if MAIN_DATA.retrieve_master() is not None:
        SESSION.set_view("download")
    st.error(
        "Unable to reference master sheet in sharepoint. You must import data first"
    )


def downloading_data_view():
    """
    The downloading data view which also initializes the homepage session with necessary data.
    """
    with st.spinner("Downloading Data..."):
        master_sheet = MAIN_DATA.retrieve_master()

        if "students" not in st.session_state and not master_sheet is None:
            st.session_state.students = master_sheet

        if "scholarships" not in st.session_state:
            SHAREPOINT.download("/data/Scholarships.xlsx", "/data/")
            st.session_state.scholarships = pd.read_excel(
                get_appdata_path("/data/Scholarships.xlsx")
            )

        if "user_recommendations" not in st.session_state:
            try:
                SHAREPOINT.download(
                    f"/data/{SHAREPOINT.get_hawk_id()}_Reviews.xlsx", "/data/"
                )
            except:
                new_file = pd.DataFrame(
                    columns=["UID", "Scholarship", "Rating", "Additional Feedback"]
                )
                new_file.to_excel(
                    get_appdata_path(f"/data/{SHAREPOINT.get_hawk_id()}_Reviews.xlsx"),
                    index=False,
                )
                SHAREPOINT.upload(
                    f"/data/{SHAREPOINT.get_hawk_id()}_Reviews.xlsx", "/data/"
                )
            st.session_state.user_recommendations = pd.read_excel(
                get_appdata_path(f"/data/{SHAREPOINT.get_hawk_id()}_Reviews.xlsx")
            )

    SESSION.set_view("main")


def compute_reviews(
    current_data, user_recommendations, current_scholarship, scholarships
):
    """
    Compute the selected reviews for current scholarship???
    """
    current_data_reviews = []
    for index, row in current_data.iterrows():
        student_recommendation = user_recommendations.loc[
            (user_recommendations["UID"] == row["UID"])
            & (user_recommendations["Scholarship"] == current_scholarship)
        ]
        if len(student_recommendation) > 0:
            current_data_reviews.append(student_recommendation["Rating"].iloc[0])
        else:
            current_data_reviews.append("N/A")
    current_data["Review"] = current_data_reviews

    # Filtering current data with scholarship criteria
    criteria = scholarships.loc[scholarships["Name"] == current_scholarship]
    groups_columns = []
    criteria_no_groups = []
    for column in criteria.columns.tolist():
        if column[0:5] == "Group":
            if (
                isinstance(criteria[column].iloc[0], str)
                and criteria[column].iloc[0].startswith("[")
                and criteria[column].iloc[0].endswith("]")
            ):
                groups_columns.append(groups_string_to_list(criteria[column].iloc[0]))
        elif column not in ["Name", "Total Amount", "Value"]:
            criteria_no_groups.append(column)
    for criterion in criteria_no_groups:
        if criterion in current_data.columns.tolist():
            try:
                value = float(criteria[criterion])
                in_group = False
                for group in groups_columns:
                    if criterion in group:
                        in_group = True
                        met_criteria = False
                        for index, student in current_data.iterrows():
                            for group_c in group:
                                if student[group_c] >= value:
                                    met_criteria = True
                            if met_criteria == False:
                                current_data.drop(index)
                if in_group == False:
                    current_data.drop(
                        current_data.loc[current_data[criterion] < value].index,
                        inplace=True,
                    )
            except ValueError:
                value = criteria[criterion]
                in_group = False
                for group in groups_columns:
                    if criterion in group:
                        in_group = True
                        met_criteria = False
                        for index, student in current_data.iterrows():
                            for group_c in group:
                                if student[group_c] >= value:
                                    met_criteria = True
                            if met_criteria == False:
                                current_data.drop(index)
                if in_group == False:
                    current_data.drop(
                        current_data.loc[current_data[criterion] != value].index,
                        inplace=True,
                    )


def main_view():
    """
    Main view shown when data is downloaded
    """
    if "students" not in st.session_state:
        SESSION.set_view("error")

    students = st.session_state.students
    current_data = students.copy()

    user_recommendations = st.session_state.user_recommendations
    scholarships = st.session_state.scholarships

    # Selecting a scholarship to use for filtering and reviews
    current_scholarship = st.selectbox(
        "Which scholarship would you like to consider?",
        np.append(["None"], scholarships["Name"].values),
    )
    if current_scholarship != "None":
        # Adding previos reviews to current data
        compute_reviews(
            current_data, user_recommendations, current_scholarship, scholarships
        )

    # Configuring options for table functionality
    current_data.insert(0, "Select All", None)
    graph_data = GridOptionsBuilder.from_dataframe(current_data)
    graph_data.configure_pagination(enabled=True)  # Add pagination
    graph_data.configure_side_bar()  # Add a sidebar
    graph_data.configure_default_column(editable=False, groupable=True)
    graph_data.configure_selection(
        selection_mode="multiple", use_checkbox=True
    )  # Enable multi-row selection
    graph_data.configure_column("Select All", headerCheckboxSelection=True)
    graph_data.configure_grid_options(onFirstDataRendered=js)
    graph_data.configure_column(
        "Describe any relevant life experience related to engineering. ",
        onCellClicked=JsCode(
            "function(params) { alert(params.node.data['Describe any relevant life experience related to engineering. ']); };"
        ),
    )
    gridoptions = graph_data.build()
    gridoptions["getRowStyle"] = jscode
    custom_css = {}

    # Building the table
    grid_table = AgGrid(
        current_data,
        gridOptions=gridoptions,
        theme="balham",
        custom_css=custom_css,
        height=700,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
    )

    # Displaying statistics about main data frame
    main_data_statistics(current_data, students, grid_table)

    # Actions for user to take on main data frame
    with st.container():
        col1, col2, col3 = st.columns(3)

        # Submitting recommendations for scholarhsips
        with col1:
            submit_review_expander(
                current_scholarship, user_recommendations, grid_table, SHAREPOINT
            )

        # Viewing graphs of student distributions
        with col2:
            distribution_graph_expander(current_data, grid_table)

        with col3:
            if st.button("Export Current Table"):
                grid_table["data"].to_excel(
                    get_appdata_path("./data/Exported_Data.xlsx")
                )
                st.success("Exported data to /data as Exported_Data.xlsx")


if SESSION.view == "main":
    main_view()
elif SESSION.view == "error":
    error_view()
else:
    downloading_data_view()
