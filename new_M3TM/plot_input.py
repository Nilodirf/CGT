# Here you can call some plot functions, plot and save plots

from plot import SimPlot


# Initialize the plot class with the simulation results folder denoted 'file':
plotter = SimPlot(file='fit/thin')

# plotter.convert_to_dat()

# Plot a map of the denoted simulation of one of the three subsystems, save if you want to:
# plotter.map_plot(key='tp',  save_fig=False)

# plotter.map_plot(key='mag', kind='surface', max_time=5, save_fig=True, filename='thin_eptime_mag', show_title=False, color_scale='inferno', vmin=0, vmax=1)
plotter.map_plot(key='tp', kind='surface', min_time=0.1, max_time=2000, save_fig=True, filename='thick_smalltime', show_title=False, color_scale='Greens_r')


# Plot the dynamics of one subsystem for some layers in line-plots to see the dynamics, save if you want to:
# plotter.line_plot(key='tp', min_layer=16, average=True, save_fig=False)
# plotter.line_plot(key='te', min_layer=0, max_layer=4, average=True, save_fig=False, norm=False)

# plotter.line_plot(key='mag', min_layer=0, max_layer=4, average=False, save_fig=False, norm=False)

# plotter.te_tp_plot(max_time=5, average=False, save_fig=True,  filename='te_tp_thick', tp_layers=[8, 83], color_scales=['Blues_r', 'Greens_r'])
