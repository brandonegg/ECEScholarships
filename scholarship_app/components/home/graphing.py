"""
Graphing utility for homepage
"""
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import streamlit as st


def dynamic_fig(var_df, x_axis, y_axis, options=None, highlights=None):
    """
    Function to generate dynamic graph of student data
    """
    fig, _ = plt.subplots()
    var_xs = var_df[x_axis][var_df[x_axis] != 0][var_df[y_axis] != 0]
    var_ys = var_df[y_axis][var_df[x_axis] != 0][var_df[y_axis] != 0]
    weighted_bins = np.zeros((len(var_xs), 3))
    for i in var_xs.index:
        found = False
        for j in range(weighted_bins.shape[0]):
            if found:
                continue
            if weighted_bins[j][0] == 0 or (
                weighted_bins[j][0] == var_xs[i] and weighted_bins[j][1] == var_ys[i]
            ):
                weighted_bins[j][0] = var_xs[i]
                weighted_bins[j][1] = var_ys[i]
                weighted_bins[j][2] += 1
                found = True
    weighted_bins = weighted_bins[~np.all(weighted_bins == 0, axis=1)]
    for wbin in weighted_bins:
        if options[1]:
            wbin[-1] = wbin[-1] - (np.min(weighted_bins[:, 2]) - 1)
        else:
            wbin[-1] = 1
        if wbin[-1] > 10:
            wbin[-1] = 10
    plt.scatter(weighted_bins[:, 0], weighted_bins[:, 1], s=32 * weighted_bins[:, 2])
    if highlights is not None and options[2] == "Selected Students":
        highlights = [h for h in highlights if h is not None]
        hxs = var_df.iloc[highlights][x_axis]
        hys = var_df.iloc[highlights][y_axis]
        colors = iter(cm.rainbow(np.linspace(0, 1, len(hys) + 1)))
        next(colors)
        for var_x, var_y in zip(hxs, hys):
            plt.scatter(var_x, var_y, color=next(colors))
        legend_names = ["Other Students"]
        legend_names.extend(var_df.iloc[highlights]["Name"].values)
        if options[0]:
            plt.legend(legend_names)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    st.pyplot(fig)
    return fig


def distribution_graph_expander(current_data, grid_table):
    """
    Renders the expander for the graphing distribution
    """
    with st.expander("See Distribution of Students"):
        with st.container():
            numeric_cols = current_data.copy().select_dtypes(include="number").columns

            fig_select1a = st.selectbox("Select X axis", numeric_cols.values)
            fig_select1b = st.selectbox("Select Y axis", numeric_cols.values)
            fig_select1c = st.selectbox(
                "Highlight Scheme", ["None", "Selected Students"]
            )  # , 'Scholarship Status'
            show_legend = st.checkbox("Show Legend", True)
            weight_bins = st.checkbox("Weight Plot", True)
            sel_row_indices = None
            if fig_select1c == "Selected Students":
                sel_rows = grid_table["selected_rows"]
                sel_row_indices = [
                    rows["_selectedRowNodeInfo"]["nodeRowIndex"] for rows in sel_rows
                ]
            option_select = [show_legend, weight_bins, fig_select1c]
            dynamic_fig(
                current_data,
                fig_select1a,
                fig_select1b,
                option_select,
                sel_row_indices,
            )  # Exporting the selected students
