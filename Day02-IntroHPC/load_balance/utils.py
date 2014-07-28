#!/user/bin/env python
import os
from IPython.core.getipython import get_ipython
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd

MATPLOTLIBRC = '''
patch.linewidth: 0.5
patch.facecolor: 348ABD
patch.facecolor: white

patch.edgecolor: EEEEEE
patch.antialiased: True

font.size: 10.0

axes.facecolor: white
axes.edgecolor: white
axes.linewidth: 1
axes.grid: True
axes.titlesize: x-large
axes.labelsize: large
axes.labelcolor: 555555
axes.axisbelow: True       # grid/ticks are below elements (eg lines, text)

axes.color_cycle: E24A33, 348ABD, 988ED5, 777777, FBC15E, 8EBA42, FFB5B8
                   # E24A33 : red
                   # 348ABD : blue
                   # 988ED5 : purple
                   # 777777 : gray
                   # FBC15E : yellow
                   # 8EBA42 : green
                   # FFB5B8 : pink

xtick.color: 555555
xtick.direction: out

ytick.color: 555555
ytick.direction: out

grid.color: white
grid.linestyle: -    # solid line

figure.facecolor: white
figure.edgecolor: 0.50

legend.scatterpoints: 1
legend.frameon: True'''

def create_matplotlibrc():

	directory = os.path.join(os.environ['HOME'],'.matplotlib')

	if not os.path.exists(directory):
		os.makedirs(directory)

	filename = os.path.join(directory,'matplotlibrc')
	with open(filename,'w') as outfile:
		outfile.write(MATPLOTLIBRC)


def print_fig(fig):
	for ax in fig.axes:
		for s in ['bottom', 'left', 'top', 'right']:
			ax.spines[s].set_linewidth(0.7)
			ax.spines[s].set_color('grey')  

		for s in ['top','right']:
			ax.spines[s].set_visible(False)
	        
		ax.patch.set_facecolor('1.0')
		ax.grid(False)

		ax.tick_params(direction='out', 
		               length=10, 
		               width=1., 
		               colors='grey',
		               bottom='on',
		               top='off', 
		               left='on', 
		               right='off',
		               pad=12
		               )
		
		if ax.legend_ is not None:
			ax.legend_.get_frame().set_linewidth(0)
			ax.legend_.get_frame().set_alpha(0.5)

def plot_workflow(results):
    res = pd.DataFrame(results)
    ids = list(set(res['id']))
    id_dic = dict( [k,v+0.65] for k,v in zip(ids, range(len(ids))))
    fig, ax = plt.subplots(figsize=(8, 6))

    tmin = res['start'].min()    
    for i in res.index:
        x_start = res.ix[i]['start'] - tmin
        x_end = res.ix[i]['end_time'] - tmin - x_start
        x_id = id_dic[res.ix[i]['id']]
        ax.add_patch(plt.Rectangle((x_start, x_id), x_end, 0.8, alpha=0.5, color='grey'))
    
    ax.set_ylim(0.5, len(ids)+0.5)
    ax.set_xlim(0, res['end_time'].max() - tmin)
    ax.set_ylabel("Worker")
    ax.set_xlabel("seconds")


create_matplotlibrc()

ip = get_ipython()
formatter = ip.display_formatter.formatters['text/html']
formatter.for_type(Figure, print_fig)
