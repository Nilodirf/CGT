# Here you can call some plot functions, plot and save plots

from plot import SimPlot


# Initialize the plot class with the simulation results folder denoted 'file':
plotter = SimPlot(file='14_nm')

plotter.convert_to_dat()

# Plot a map of the denoted simulation of one of the three subsystems, save if you want to:
plotter.map_plot(key='mag',  save_fig=False, max_time=10)
# plotter.map_plot(key='te', max_time=30, save_fig=True)

# Plot the dynamics of one subsystem for some layers in line-plots to see the dynamics, save if you want to:
# plotter.line_plot(key='mag', min_layer=0, max_layer=6, average=False, save_fig=True)
# plotter.line_plot(key='te', average=False, save_fig=False)
# plotter.line_plot(key='mag', min_layer=0, average=False, save_fig=True, norm=False)
