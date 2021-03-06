import numpy as np
from utils import track, seriationMDS, sorting, seriationMDS3, seriationMDS5
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models.widgets import Slider, Select
from bokeh.plotting import figure, output_file
from bokeh.models import ColumnDataSource, LogColorMapper, LogTicker, ColorBar, LinearColorMapper, CustomJS, Range1d
from bokeh.palettes import all_palettes
from bokeh.models.tools import *
from bokeh.models.glyphs import ImageURL
from read import *
from boundingbox import *
from more_itertools import unique_everseen

# flask magic
url_params = curdoc().session_context.request.arguments

##### CHECK FF OF IK DIT GEBROKEN HEB ###

stimuli_meta = read_metadata()
stimuli_names = list(stimuli_meta.keys())


############
###Matrix###
############

user_list = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13', 'p14', 'p15', 'p16',
            'p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24', 'p25', 'p26', 'p27', 'p28', 'p29', 'p30', 'p31',
            'p32', 'p33', 'p34', 'p35', 'p36', 'p37', 'p38', 'p39', 'p40']
zeros = np.zeros(400)

example_loaded_stimuli = stimuli_names.pop()
print(example_loaded_stimuli)

df = read_main_df()

# setup empty ColumnDataSource
source = ColumnDataSource(data=dict(
   xname=[],
   yname=[],
   alphas=[],
   colors=[],
   zeros=[],
   count=[],
   MappedFixationPointY=[],
   MappedFixationPointX=[]
))

# initiate plot
p = figure(title="Bounding box",
          x_axis_location="above", tools="hover,save,wheel_zoom,reset,tap,box_select",
          x_range=list(reversed(user_list)), y_range=list(user_list))

# set some plot parameters
# p.plot_width = 800
# p.plot_height = 800
p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "10pt"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = np.pi / 3

# plotting the actual rectangles
p.rect('xname', 'yname', 0.9, 0.9, source=source, color='colors',
      alpha='alphas', line_color=None,
      hover_line_color='black', hover_color='black')

# Configure Hover tool
p.select_one(HoverTool).tooltips = [
   ('names', '@yname, @xname'),
   ('Similarity score', '@count')]

###############
###Color Bar###
###############

# select
unselect_rectangle = Rect(line_alpha=0, fill_alpha=0)

# set up color bar
color_bar = figure(
   tools="box_select, crosshair", width=80, height=600, title=None,
   y_range=(0, 1),
   y_axis_label="Similarity score", toolbar_location=None)
color_bar.rect(
   'zeros', 'count', 0.5, 0.0005, name='color_bar',
   source=source, color='colors', alpha='alphas')
render = color_bar.select(name='color_bar')
render.nonselection_glyph = unselect_rectangle

crosshair = color_bar.select(type=CrosshairTool)
crosshair.dimensions = 'width'

# color bar parameters
color_bar.xgrid.grid_line_color = None
color_bar.ygrid.grid_line_color = None
color_bar.yaxis.axis_label_text_font_size = '12pt'
color_bar.xaxis.major_label_text_font_size = '0pt'
color_bar.xaxis.major_tick_line_color = None
color_bar.xaxis.minor_tick_line_color = None

###########
###Box 1###
###########

# set up widgets lists
cities = list(stimuli_names)
colorSchemes = ['SteelBlue', 'Tomato', 'MediumSeaGreen', 'Inferno', 'Magma', 'Plasma', 'Viridis']
ordering = ['default', 'seriationMDS', 'seriationMDS2', 'seriationMDS3', 'seriationMDS4','seriationMDS5', 'seriationMDS6', 'ward']

# Set up widgets
city_select = Select(title="City", options=cities)
colorScheme_select = Select(title="Color Scheme", value="SteelBlue", options=colorSchemes)
ordering_select = Select(title="Ordering", options=ordering)


# Set up callbacks
@track
def update_title(attrname, old, new):
   p.title.text = city_select.value


# updates title of plot
city_select.on_change('value', update_title)

###########
###Box 4###
###########
source4 = ColumnDataSource(data=dict(
   MappedFixationPointX=[],
   MappedFixationPointY=[],
))

p4 = figure(title="Bokeh Map", tools="save")
p4.circle('MappedFixationPointX', 'MappedFixationPointY', size=15,
          source=source4, fill_color="orange", alpha=0.5)
p4.line('MappedFixationPointX', 'MappedFixationPointY',
           line_color="navy", source=source4, alpha=0.5)
p4.y_range = Range1d(1200,0)

source.callback = CustomJS(args=dict(source4=source4), code="""
       var inds = cb_obj.selected['1d'].indices;
       var d1 = cb_obj.data;
       var d2 = source4.data;
       d2['MappedFixationPointX'] = [[]]
       d2['MappedFixationPointY'] = [[]]
       for (var i = 0; i < inds.length; i++) {
           d2['MappedFixationPointX'][[i]] = d1['MappedFixationPointX'][inds[i]]
           d2['MappedFixationPointY'][[i]] = d1['MappedFixationPointY'][inds[i]]
       }
       d2['MappedFixationPointX'] = d2['MappedFixationPointX'].map(JSON.stringify).reverse().filter(function (e, i, a) {
           return a.indexOf(e, i+1) === -1;
           }).reverse().map(JSON.parse) //
       d2['MappedFixationPointY'] = d2['MappedFixationPointY'].map(JSON.stringify).reverse().filter(function (e, i, a) {
           return a.indexOf(e, i+1) === -1;
           }).reverse().map(JSON.parse) //

       d2['MappedFixationPointX'] = [].concat.apply([], d2['MappedFixationPointX']);
       d2['MappedFixationPointY'] = [].concat.apply([], d2['MappedFixationPointY']);
       source4.change.emit();
   """)


#################
###Update data###
#################

@track
def update_data(attrname, old, new):
   # Get the current slider values
   city = city_select.value
   colorScheme = colorScheme_select.value

   # Generate the new adjacency matrix
   alpha = []
   color = []
   xname = []
   yname = []
   count = []
   MappedFixationPointY = []
   MappedFixationPointX = []

   temp = df[(df['StimuliName'] == city)]
   p4.x_range = Range1d(0, stimuli_meta.get(city).get('x_dim'))
   p4.y_range = Range1d(stimuli_meta.get(city).get('y_dim'), 0)
   gradient = 0

   if colorScheme not in ['Tomato', 'SteelBlue', 'MediumSeaGreen']:
       colormap = all_palettes[colorScheme][256]
       gradient = 1

   adjacency =  scanpaths_dict(city, user_list, df)
   # retrieve similarity score from dictionary and add color
   for i in range(0, len(user_list)):
       for j in range(0, len(user_list)):
           value = adjacency[city][user_list[i]].get(user_list[j], 'Key not present')
           if value == 'Key not present':
               continue
           xname.append(user_list[i])
           yname.append(user_list[j])
           count.append(value)

           MappedFixationPointX.append(
               temp[(temp['user'] == user_list[i]) | (temp['user'] == user_list[j])]['MappedFixationPointX'])
           MappedFixationPointY.append(
               temp[(temp['user'] == user_list[i]) | (temp['user'] == user_list[j])]['MappedFixationPointY'])

           if gradient == 1:
               color.append(colormap[255 - int(round(255 * value))])
               alpha.append(1.0)
           else:
               alpha.append(value)
               color.append(colorScheme)

   zeros = np.zeros(pow(len(np.unique(xname)), 2))

   # swap out the old data for the new data
   source.data = dict(
       xname=xname,
       yname=yname,
       alphas=alpha,
       colors=color,
       count=count,
       zeros=zeros,
       MappedFixationPointY=MappedFixationPointY,
       MappedFixationPointX=MappedFixationPointX
   )

   source4.data = dict(
       MappedFixationPointY=[item for sublist in MappedFixationPointY for item in sublist],
       MappedFixationPointX=[item for sublist in MappedFixationPointX for item in sublist]
   )

   # update the x and y labels
   order = list(unique_everseen(xname))
   p.x_range.factors = order
   p.y_range.factors = list(reversed(order))

   # log to console
   print('Updated Plot')

@track
def reorder(attrname, old, new):
    order = ordering_select.value

    if order == "default":
        new_order = list(unique_everseen(source.data["xname"]))
    if order == "seriationMDS":
        new_order = seriationMDS(source.data, 0)
    if order == "seriationMDS2":
        new_order = seriationMDS(source.data, 1)
    if order == "seriationMDS3":
        new_order = seriationMDS3(source.data, 0)
    if order == "seriationMDS4":
        new_order = seriationMDS3(source.data, 1)
    if order == "seriationMDS5":
        new_order = seriationMDS5(source.data, 0)
    if order == "seriationMDS6":
        new_order = seriationMDS5(source.data, 1)
    if order == "ward":
        new_order = sorting(source.data)
    p.x_range.factors = list(new_order)
    p.y_range.factors = list(reversed(new_order))

@track
def update_colorscheme(attrname, old, new):
    alpha = []
    color = []
    colorScheme = colorScheme_select.value
    gradient = 0

    if colorScheme not in ['Tomato', 'SteelBlue', 'MediumSeaGreen']:
        colormap = all_palettes[colorScheme][256]
        gradient = 1

    for i in range(0, len(source.data["count"])):
        value = source.data["count"][i]
        if gradient == 1:
            color.append(colormap[255 - int(round(255 * value))])
            alpha.append(1.0)
        else:
            alpha.append(value)
            color.append(colorScheme)

    source.data["colors"] = color
    source.data["alphas"] = alpha

#############
###output####
#############

# updates plot data on_change
city_select.on_change('value', update_data)
colorScheme_select.on_change('value', update_colorscheme)
ordering_select.on_change('value', reorder)

# Set up layouts and add to document
inputs = widgetbox([city_select, colorScheme_select, ordering_select ])

# Flask/Bokeh magic
curdoc().add_root(row(inputs, color_bar, p, p4))

