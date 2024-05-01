import pandas as pd
from matplotlib import axes
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib import patches


def plot_strike_zone(data: pd.DataFrame, title: str = '', colorby: str = 'pitch_type', legend_title: str = '',
                     annotation: str = 'pitch_type', axis: Optional[axes.Axes] = None) -> axes.Axes:
    """
    Produces a pitches overlaid on a strike zone using StatCast data
    
    Args:
        data: (pandas.DataFrame)
            StatCast pandas.DataFrame of StatCast pitcher data
        title: (str), default = ''
            Optional: Title of plot
        colorby: (str), default = 'pitch_type'
            Optional: Which category to color the mark with. 'pitch_type', 'pitcher', 'description' or a column within data
        legend_title: (str), default = based on colorby
            Optional: Title for the legend
        annotation: (str), default = 'pitch_type'
            Optional: What to annotate in the marker. 'pitch_type', 'release_speed', 'effective_speed',
              'launch_speed', or something else in the data
        axis: (matplotlib.axis.Axes), default = None
            Optional: Axes to plot the strike zone on. If None, a new Axes will be created
    Returns:
        A matplotlib.axes.Axes object that was used to generate the pitches overlaid on the strike zone
    """
    
    # some things to auto adjust formatting
    # make the markers really visible when fewer pitches
    alpha_markers = min(0.8, 0.5 + 1 / data.shape[0])
    alpha_text = alpha_markers + 0.2
    
    # define Matplotlib figure and axis
    if axis is None:
        fig, axis = plt.subplots()

    assert axis is not None

    # add home plate to plot 
    home_plate_coords = [[-0.71, 0], [-0.85, -0.5], [0, -1], [0.85, -0.5], [0.71, 0]]
    axis.add_patch(patches.Polygon(home_plate_coords,
                                   edgecolor = 'darkgray',
                                   facecolor = 'lightgray',
                                   zorder = 0.1))
    
    # add strike zone to plot, technically the y coords can vary by batter
    axis.add_patch(patches.Rectangle((-0.71, 1.5), 2*0.71, 2,
                 edgecolor = 'lightgray',
                 fill=False,
                 lw=3,
                 zorder = 0.1))
    
    # legend_title = ""
    color_label = ""
    
    # to avoid the SettingWithCopyWarning error
    sub_data = data.copy().reset_index(drop=True)
    if colorby == 'pitch_type':
        color_label = 'pitch_type'
        
        if not legend_title:
            legend_title = 'Pitch Type'
            
    elif colorby == 'description':
        values = sub_data.loc[:, 'description'].str.replace('_', ' ').str.title()
        sub_data.loc[:, 'desc'] = values
        color_label = 'desc'
        
        if not legend_title:
            legend_title = 'Pitch Description'
    elif colorby == 'pitcher':
        color_label = 'player_name'
        
        if not legend_title:
            legend_title = 'Pitcher'
            
    elif colorby == "events":
        # only things where something happened
        sub_data = sub_data[sub_data['events'].notna()]
        sub_data['event'] = sub_data['events'].str.replace('_', ' ').str.title()
        color_label = 'event'
        
        if not legend_title:
            legend_title = 'Outcome'
    
    else:
        color_label = colorby
        if not legend_title:
            legend_title = colorby
        
    scatters = []
    for color in sub_data[color_label].unique():
        color_sub_data = sub_data[sub_data[color_label] == color]
        scatters.append(axis.scatter(
            color_sub_data["plate_x"],
            color_sub_data['plate_z'],
            s = 10**2,
            label = pitch_code_to_name_map[color] if color_label == 'pitch_type' else color,
            alpha = alpha_markers
        ))
        
        # add an annotation at the center of the marker
        if annotation:
            for i, pitch_coord in zip(color_sub_data.index, zip(color_sub_data["plate_x"], color_sub_data['plate_z'])):
                label_formatted = color_sub_data.loc[i, annotation]
                label_formatted = label_formatted if not pd.isna(label_formatted) else ""
                
                # these are numbers, format them that way
                if annotation in ["release_speed", "effective_speed", "launch_speed"] and label_formatted != "":
                    label_formatted = "{:.0f}".format(label_formatted)
                
                axis.annotate(label_formatted,
                            pitch_coord,
                            size = 7,
                            ha = 'center',
                            va = 'center',
                            alpha = alpha_text)

    axis.set_xlim(-4, 4)
    axis.set_ylim(-1.5, 7)
    axis.axis('off')

    axis.legend(handles=scatters, title=legend_title, bbox_to_anchor=(0.7, 1), loc='upper left')
    plt.plot(
        data["plate_x_no_movement"],
        data["plate_z_no_movement"],
        marker="o",
        markersize=10,
        markerfacecolor="none",
        color="red",
        label="Pitch Tunnel",
    )

    plt.legend()
    plt.title(title)

    return axis
