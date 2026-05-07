# # # # # # # # # # # # # #
# NUCLEI POCKET VIEWER 3D #
# # # # # # # # # # # # # # # # #
# Program by Dr Frederic Strobl #
# # # # # # # # # # # # # # # # #
# Version 1.0 #
# # # # # # # #



# -------------
#  1 - Imports
# -------------

print("🚀 --- STARTING NUCLEI POCKET VIEWER 3D --- 🚀")
print("---------------------------------------------")

import os
import numpy as np
import pandas as pd
import dash
from dash import dcc, html, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go


# ---------------
#  2 - Load Data
# ---------------

# Automatically screen the "data" subfolder for Excel files
script_directory = os.path.dirname(os.path.abspath(__file__))
data_directory = os.path.join(script_directory, "data")

if not os.path.isdir(data_directory):
    raise FileNotFoundError(f"⚠️ --- DATA SUBFOLDER NOT FOUND: {data_directory} --- ⚠️")

available_nuclei_files = sorted([
    file_name for file_name in os.listdir(data_directory)
    if file_name.lower().endswith((".xlsx"))
])

if not available_nuclei_files:
    raise FileNotFoundError(f"⚠️ --- NO XLSX FILES FOUND IN DATA SUBFOLDER: {data_directory} --- ⚠️")

default_nuclei_file = available_nuclei_files[0]


# -----------------
#  3 - Preferences
# -----------------

# Size of the displayed nuclei (default = 4 / recommendation = 3 to 5)
nuclei_size = 4  

# Color scheme of the nuclei (default = "Rainbow" / other stylish options are "RdBu_r" or "Viridis")
nuclei_color_scheme = "Rainbow"

# Width of the nuclei outlines (default = 0.5 / can be set to 0 to remove the outlines)
nuclei_line_width = 0.5

# Color of the nuclei outlines (default = "Black" / other stylish options are "Red" or "Magenta")
nuclei_line_color = "Black"

# Opacity of the nuclei (default = 0.7 / recommendation = 0.5 to 1)
nuclei_opacity = 0.7

# Define rendering axis ranges (default = (600, 0), (1100, 0) and (600, 0) / adjust according to the data scope)
x_rendering_axis_range = (600, 0)
y_rendering_axis_range = (1100, 0)
z_rendering_axis_range = (600, 0)


# --------------------------
#  4 - Advanced Preferences
# --------------------------

# (!) Change these properties only if you know what you are doing (!)

# Camera distance and rendering dimensions
xz_camera_distance_neg = -3
xz_camera_distance_pos = 3
y_camera_distance_neg = -3.0
y_camera_distance_pos = 3.0
rendering_width  = 800
rendering_height = 800



# -----------------
#  5 - Format Data
# -----------------

# Function to load nuclei coordinate data from an Excel file
def load_nuclei_data(file_name):
    nuclei_file_path = os.path.join(data_directory, file_name)

    # Error management: unable to load the nuclei coordinates-containing xlsx file
    if not os.path.isfile(nuclei_file_path):
        raise FileNotFoundError(f"⚠️ --- NUCLEI XLSX FILE NOT FOUND: {nuclei_file_path} --- ⚠️")

    # Transfer data from the nuclei coordinates-containing xlsx file to a Pandas data frame
    pd_data_frame_nuclei_coordinates = pd.read_excel(nuclei_file_path)

    # Error management: less than four columns in the nuclei coordinates-containing xlsx file
    if pd_data_frame_nuclei_coordinates.shape[1] < 4:
        raise ValueError("⚠️ --- THE NUCLEI COORDINATES-CONTAINING XLSX FILE HAS LESS THAN 4 COLUMNS --- ⚠️")

    # Create numpy arrays for plotting
    nuclei_names = pd_data_frame_nuclei_coordinates.iloc[:, 0].astype(str).fillna("(unnamed)").to_numpy()
    nuclei_x = pd_data_frame_nuclei_coordinates.iloc[:, 1].to_numpy(dtype = float)
    nuclei_y = pd_data_frame_nuclei_coordinates.iloc[:, 2].to_numpy(dtype = float)
    nuclei_z = pd_data_frame_nuclei_coordinates.iloc[:, 3].to_numpy(dtype = float)

    # Color cutoff limits
    global_cmin = float(np.nanmin(nuclei_z))
    global_cmax = float(np.nanmax(nuclei_z))

    return nuclei_names, nuclei_x, nuclei_y, nuclei_z, global_cmin, global_cmax

# Initial data loading
nuclei_names, nuclei_x, nuclei_y, nuclei_z, global_cmin, global_cmax = load_nuclei_data(default_nuclei_file)



# ------------------------------
#  6 - Definition and Functions
# ------------------------------

# Define camera views for view buttons
view_cameras = {
    "view-z-neg": dict(eye = dict(x = 0, y = 0, z = xz_camera_distance_neg), up = dict(x = 0, y = 1, z = 0)),
    "view-z-pos": dict(eye = dict(x = 0, y = 0, z = xz_camera_distance_pos), up = dict(x = 0, y = 1, z = 0)),
    "view-y-neg": dict(eye = dict(x = 0, y = y_camera_distance_neg, z = 0), up = dict(x = 0, y = 0, z = 1)),
    "view-y-pos": dict(eye = dict(x = 0, y = y_camera_distance_pos, z = 0), up = dict(x = 0, y = 0, z = 1)),
    "view-x-neg": dict(eye = dict(x = xz_camera_distance_neg, y = 0, z = 0), up = dict(x = 0, y = 1, z = 0)),
    "view-x-pos": dict(eye = dict(x = xz_camera_distance_pos, y = 0, z = 0), up = dict(x = 0, y = 1, z = 0)),
}

# Define initial camera position by referencing the first camera view
initial_camera = view_cameras["view-z-neg"]

# Function to create a 3D scatter trace showing nuclei positions in different colors and specific labels
def create_scatter_trace(x_values, y_values, z_values, nuclei_names_array, cmin = None, cmax = None):
    return go.Scatter3d(
        x = x_values, y = y_values, z = z_values,
        mode = "markers",
        marker = dict(
            size = nuclei_size,
            color = z_values,
            colorscale = nuclei_color_scheme,
            cmin = cmin,
            cmax = cmax,
            showscale = False,
            line = dict(width = nuclei_line_width, color = nuclei_line_color),
            opacity = nuclei_opacity,
        ),
        name = "Nuclei",
        customdata = nuclei_names_array,
        hovertemplate = "<b>%{customdata}</b><br>X: %{x:.2f}<br>Y: %{y:.2f}<br>Z: %{z:.2f}<extra></extra>",
    )

# Function to define the 3D scene layout
def define_scene_layout(camera_settings):
    aspect_ratio_dict = dict(
        x = 1,  # Use X-axis as normalization reference
        y = y_rendering_axis_range[0] / x_rendering_axis_range[0],  # Change to [1] if the axis range is inverted in the Preferences
        z = z_rendering_axis_range[0] / x_rendering_axis_range[0],  # Change to [1] if the axis range is inverted in the Preferences
    )

    scene_dict = dict(
        xaxis = dict(title = "x", range = list(x_rendering_axis_range)),
        yaxis = dict(title = "y", range = list(y_rendering_axis_range)),
        zaxis = dict(title = "z", range = list(z_rendering_axis_range)),
        aspectmode = "manual",
        aspectratio = aspect_ratio_dict,
        camera = camera_settings,
        domain = dict(x = [0, 1], y = [0, 1])  # Fill the full plotting area
    )
    return scene_dict

# Function to assemble the rendering figure
def assemble_rendering_figure(scatter_trace, camera_settings):
    rendering_figure = go.Figure(data = [scatter_trace])
    rendering_figure.update_layout(
        title = None,  # No title for a clean look
        margin = dict(t = 0, b = 0, l = 0, r = 0),  # To override the "20" defaults
        height = rendering_height,
        width = rendering_width,
        scene = define_scene_layout(camera_settings),
        uirevision = "keep"  # Preserve user interactions across updates
    )
    return rendering_figure

# Initial rendering
scatter_trace = create_scatter_trace(
    nuclei_x, nuclei_y, nuclei_z, nuclei_names,
    cmin = global_cmin, cmax = global_cmax
)
rendering = assemble_rendering_figure(scatter_trace, initial_camera)



# ------------------
#  7 - Dash Program
# ------------------

# Initialize the Dash Program
program = dash.Dash(__name__)

# Button style
button_style_bgcolor = "#DDDDDD"
button_style_margin = "2px"
button_style_width = "80px"

# View buttons
view_buttons = [
    dict(id = "view-z-neg", label = "Ven View"),
    dict(id = "view-x-neg", label = "L-1 View"),
    dict(id = "view-z-pos", label = "Dor View"),
    dict(id = "view-x-pos", label = "L-2 View"),
    dict(id = "view-y-pos", label = "Ant View"),
    dict(id = "view-y-neg", label = "Pos View")
]

# Filter buttons
filter_buttons = [
    dict(id = "filter-x-pos", label = "X Left"),
    dict(id = "filter-x-neg", label = "X Right"),
    dict(id = "filter-y-pos", label = "Y Top"),
    dict(id = "filter-y-neg", label = "Y Bottom"),
    dict(id = "filter-z-pos", label = "Z Front"),
    dict(id = "filter-z-neg", label = "Z Back"),
    # dict(id="reset-filters", label = "Reset Filters"),
]

# All buttons variable
all_buttons = view_buttons + filter_buttons

# Program layout
program.layout = html.Div([

    # Program title
    html.H3(
        "NucleiPocketViewer3D",
        style = {
            "textAlign": "center",
            "marginBottom": "5px",
            "marginTop": "5px",
            "fontFamily": "Arial"
        }
    ),

    # File selection dropdown
    html.Div(
        [
            dcc.Dropdown(
                id = "nuclei-file-dropdown",
                options = [{"label": file_name, "value": file_name} for file_name in available_nuclei_files],
                value = default_nuclei_file,
                clearable = False,
                style = {
                    "width": "500px",
                    "margin": "0 auto",
                    "fontFamily": "Arial"
                }
            )
        ],
        style = {
            "textAlign": "center",
            "marginBottom": "10px"
        }
    ),

    # View button row
    html.Div(
        [
            html.Button(
                btn["label"],
                id = btn["id"],
                n_clicks = 0,
                style = {
                    "background-color": button_style_bgcolor,
                    "margin": button_style_margin,
                    "width": button_style_width
                }
            )
            for btn in view_buttons
        ],
        id = "view-button-row",
        style = {
            "textAlign": "center",
            "marginBottom": "5px"
        }
    ),

    # Filter button row
    html.Div(
        [
            html.Button(
                btn["label"],
                id = btn["id"],
                n_clicks = 0,
                style = {
                    "background-color": button_style_bgcolor,
                    "margin": button_style_margin,
                    "width": button_style_width
                }
            )
            for btn in filter_buttons
        ],
        id = "filter-button-row",
        style = {
            "textAlign": "center",
            "marginBottom": "5px"
        }
    ),

    # 3D rendering
    html.Div(
        dcc.Graph(
            id = "nuclei-plot",
            figure = rendering,
            config = {
                "displayModeBar": False,
                "scrollZoom": False
            },
            style = {"display": "inline-block"}  # Required for centering
        ),
        style = {
            "textAlign": "center"  # To center the graph horizontally
        }
    ),


    dcc.Store(id = "filter-state", data = {
        "x_pos": False, "x_neg": False,
        "y_pos": False, "y_neg": False,
        "z_pos": False, "z_neg": False
    }),

    dcc.Store(id = "camera-state", data = initial_camera),
])

# ---------------
#  8 - Callbacks
# ---------------

# Main callback
@program.callback(
    Output("nuclei-plot", "figure"),
    Output("filter-state", "data"),
    Output("camera-state", "data"),
    [Input("nuclei-file-dropdown", "value"),
     Input("nuclei-plot", "relayoutData")] + [Input(btn["id"], "n_clicks") for btn in all_buttons],
    State("filter-state", "data"),
    State("camera-state", "data"),
    prevent_initial_call = True
)

# Function for safe callback
def safe_callback(relayout_data, *args):
    try:
        return update_rendering(relayout_data, *args)
    except Exception as e:
        print("⚠️  Visualization error (silent):", str(e).split("\n")[0])
        raise PreventUpdate

# Function to update the rendering
def update_rendering(selected_file, relayout_data, *args):
    triggered_id = ctx.triggered_id
    button_clicks = args[:-2]
    filter_state = args[-2]
    stored_camera = args[-1]

    # Load currently selected file
    nuclei_names, nuclei_x, nuclei_y, nuclei_z, global_cmin, global_cmax = load_nuclei_data(selected_file)

    new_state = filter_state.copy()
    new_camera = stored_camera

    if triggered_id == "nuclei-file-dropdown":
        new_state = {
            "x_pos": False, "x_neg": False,
            "y_pos": False, "y_neg": False,
            "z_pos": False, "z_neg": False
        }
        new_camera = initial_camera
        print("FILE DROPDOWN TRIGGER - DATA RELOADED")
        print("-------------------------------------")

    elif triggered_id in [btn["id"] for btn in all_buttons]:  # If-fork for button presses
        for i, btn in enumerate(all_buttons):
            btn_id = btn["id"]
            n_clicks = button_clicks[i]
            if triggered_id == btn_id:
                if btn_id.startswith("view-"):
                    new_camera = view_cameras[btn_id]
                    print("VIEW BUTTON TRIGGER - CAMERA MOVEMENT")
                    print("-------------------------------------")
                elif btn_id.startswith("filter-"):
                    print("FILTER/RESET BUTTON TRIGGER - NO CAMERA MOVEMENT")
                    print("------------------------------------------------")
                    if btn_id == "reset-filters":
                        for k in new_state:
                            new_state[k] = False
                    elif btn_id.startswith("filter-"):
                        key = btn_id.replace("filter-", "").replace("-", "_")
                        new_state[key] = not new_state[key]
                break

    elif triggered_id == "nuclei-plot":  # Elif-fork for mouse rotation
        if relayout_data and "scene.camera" in relayout_data:
            new_camera = relayout_data["scene.camera"]
        elif relayout_data and "scene.camera.eye" in relayout_data and "scene.camera.up" in relayout_data:
            new_camera = {
                "eye": relayout_data["scene.camera.eye"],
                "up": relayout_data["scene.camera.up"]
            }
        print("RELAYOUT TRIGGER - CAMERA MOVEMENT")
        print("----------------------------------")

    else:  # Else for unforeseen things
        print("NO INPUT - KEEP CAMERA")

    # Apply filters
    mask = np.ones(len(nuclei_x), dtype = bool)
    if new_state["x_pos"]: mask &= nuclei_x >= x_rendering_axis_range[0] / 2
    if new_state["x_neg"]: mask &= nuclei_x <  x_rendering_axis_range[0] / 2
    if new_state["y_pos"]: mask &= nuclei_y >= y_rendering_axis_range[0] / 2
    if new_state["y_neg"]: mask &= nuclei_y <  y_rendering_axis_range[0] / 2
    if new_state["z_pos"]: mask &= nuclei_z >= z_rendering_axis_range[0] / 2
    if new_state["z_neg"]: mask &= nuclei_z <  z_rendering_axis_range[0] / 2

    x_f = nuclei_x[mask]
    y_f = nuclei_y[mask]
    z_f = nuclei_z[mask]
    names_f = nuclei_names[mask]

    if x_f.size == 0:
        x_f = np.array([0.0])
        y_f = np.array([0.0])
        z_f = np.array([0.0])
        names_f = np.array(["(no nuclei visible)"])

    scatter_new = create_scatter_trace(
        x_f, y_f, z_f, names_f,
        cmin = global_cmin, cmax = global_cmax
    )
    fig_new = assemble_rendering_figure(scatter_new, new_camera)

    return fig_new, new_state, new_camera

# Callback for filter button highlighting
@program.callback(
    [Output(btn["id"], "style") for btn in filter_buttons],
    Input("filter-state", "data")
)

# Function to update the filter button styles
def update_filter_button_styles(filter_state):
    active = {
        "background-color": "lightgreen",
        "margin": button_style_margin,
        "width": button_style_width
    }
    inactive = {
        "background-color": button_style_bgcolor,
        "margin": button_style_margin,
        "width": button_style_width
    }
    styles = []
    for btn in filter_buttons:
        key = btn["id"].replace("filter-", "").replace("-", "_")
        styles.append(active if filter_state.get(key, False) else inactive)
    return styles

# Run the program
if __name__ == "__main__":
    program.run(debug = True)