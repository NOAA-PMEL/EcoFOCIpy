"""
EcoFOCI Cruise Seabird QuickLook

Plots data from csv and cnv files
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seawater as sw

__all__ = ["CTDProfilePlot", "plot_salvtemp"]

'------------------------------------------------------------------------------'

class CTDProfilePlot(object):


    def __init__(self, fontsize=10, labelsize=10, plotstyle='k-.', stylesheet='seaborn-ticks'):
        """Initialize the timeseries with items that do not change.

        This sets up the axes and station locations. The `fontsize` and `spacing`
        are also specified here to ensure that they are consistent between individual
        station elements.

        Parameters
        ----------
        fontsize : int
            The fontsize to use for drawing text
        labelsize : int
          The fontsize to use for labels
        stylesheet : str
          Choose a mpl stylesheet [u'seaborn-darkgrid', 
          u'seaborn-notebook', u'classic', u'seaborn-ticks', 
          u'grayscale', u'bmh', u'seaborn-talk', u'dark_background', 
          u'ggplot', u'fivethirtyeight', u'seaborn-colorblind', 
          u'seaborn-deep', u'seaborn-whitegrid', u'seaborn-bright', 
          u'seaborn-poster', u'seaborn-muted', u'seaborn-paper', 
          u'seaborn-white', u'seaborn-pastel', u'seaborn-dark', 
          u'seaborn-dark-palette']
        """

        self.fontsize = fontsize
        self.labelsize = labelsize
        self.plotstyle = plotstyle
        self.max_xticks = 10
        plt.style.use(stylesheet)
        mpl.rcParams['svg.fonttype'] = 'none'
        mpl.rcParams['ps.fonttype'] = 42 #truetype/type2 fonts instead of type3
        mpl.rcParams['pdf.fonttype'] = 42 #truetype/type2 fonts instead of type3
        mpl.rcParams['axes.grid'] = True
        mpl.rcParams['axes.edgecolor'] = 'white'
        mpl.rcParams['axes.linewidth'] = 0.25
        mpl.rcParams['grid.linestyle'] = '--'
        mpl.rcParams['grid.linestyle'] = '--'
        mpl.rcParams['xtick.major.size'] = 2
        mpl.rcParams['xtick.minor.size'] = 1
        mpl.rcParams['xtick.major.width'] = 0.25
        mpl.rcParams['xtick.minor.width'] = 0.25
        mpl.rcParams['ytick.major.size'] = 2
        mpl.rcParams['ytick.minor.size'] = 1
        mpl.rcParams['xtick.major.width'] = 0.25
        mpl.rcParams['xtick.minor.width'] = 0.25
        mpl.rcParams['ytick.direction'] = 'out'
        mpl.rcParams['xtick.direction'] = 'out'
        mpl.rcParams['ytick.color'] = 'grey'
        mpl.rcParams['xtick.color'] = 'grey'
        
    def plot2var(self, varname=None, xdata=None, ydata=None, xlabel=None, secondary=False, **kwargs):
        fig, ax1 = plt.subplots(figsize=(5.5, 4.25))
        p1 = ax1.plot(xdata[0], ydata)
        plt.setp(p1, color=self.var2format(varname[0])['color'],
                   linestyle=self.var2format(varname[0])['linestyle'],
                   linewidth=self.var2format(varname[0])['linewidth'])
        if secondary and not (xdata[1].size == 0):
            p1 = ax1.plot(xdata[1],ydata)
            plt.setp(p1, color=self.var2format(varname[1])['color'],
                         linestyle=self.var2format(varname[1])['linestyle'],
                         linewidth=self.var2format(varname[1])['linewidth'])
            #set plot limits for two vars by finding the absolute range and adding 10%
            abmin=np.nanmin([np.nanmin(xdata[0]),np.nanmin(xdata[1])])
            abmax=np.nanmax([np.nanmax(xdata[0]),np.nanmax(xdata[1])])
            try:
              ax1.set_xlim([abmin - 0.1*(abmax-abmin),abmax + 0.1*(abmax-abmin)])
            except:
              ax1.set_xlim([0,1])

        ax1.invert_yaxis()
        plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
        plt.xlabel(xlabel[0], fontsize=self.labelsize, fontweight='bold')

        fmt=mpl.ticker.StrMethodFormatter(self.var2format(varname[0])['format'])
        ax1.xaxis.set_major_formatter(fmt)
        ax1.tick_params(axis='both', which='major', labelsize=self.labelsize)

        #plot second param
        ax2 = ax1.twiny()
        p1 = ax2.plot(xdata[2], ydata)
        plt.setp(p1, color=self.var2format(varname[2])['color'],
                   linestyle=self.var2format(varname[2])['linestyle'],
                   linewidth=self.var2format(varname[2])['linewidth'])
        if secondary and not (xdata[3].size == 0):
            p1 = ax2.plot(xdata[3],ydata)
            plt.setp(p1, color=self.var2format(varname[3])['color'],
                         linestyle=self.var2format(varname[3])['linestyle'],
                         linewidth=self.var2format(varname[3])['linewidth'])
            #set plot limits for two vars by finding the absolute range and adding 10%
            abmin=np.nanmin([np.nanmin(xdata[2]),np.nanmin(xdata[3])])
            abmax=np.nanmax([np.nanmax(xdata[2]),np.nanmax(xdata[3])])
            try:
                ax2.set_xlim([abmin - 0.1*(abmax-abmin),abmax + 0.1*(abmax-abmin)])
            except:
                ax2.set_xlim([0,1])

        plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
        plt.xlabel(xlabel[1], fontsize=self.labelsize, fontweight='bold')

        #set xticks and labels to be at the same spot for all three vars
        ax1.set_xticks(np.linspace(ax1.get_xbound()[0], ax1.get_xbound()[1], self.max_xticks))
        ax2.set_xticks(np.linspace(ax2.get_xbound()[0], ax2.get_xbound()[1], self.max_xticks))

        fmt=mpl.ticker.StrMethodFormatter(self.var2format(varname[2])['format'])
        ax2.xaxis.set_major_formatter(fmt)
        ax2.tick_params(axis='x', which='major', labelsize=self.labelsize)


        return plt, fig

    def plot2var_2y(self, varname=None, xdata=None, ydata=None, xlabel=None, secondary=False, **kwargs):
        fig, ax1 = plt.subplots(figsize=(5.5, 4.25))
        p1 = ax1.plot(xdata[0], ydata[0])
        plt.setp(p1, color=self.var2format(varname[0])['color'],
                   linestyle=self.var2format(varname[0])['linestyle'],
                   linewidth=self.var2format(varname[0])['linewidth'])
        if secondary and not (xdata[1].size == 0):
            p1 = ax1.plot(xdata[1],ydata[0])
            plt.setp(p1, color=self.var2format(varname[1])['color'],
                         linestyle=self.var2format(varname[1])['linestyle'],
                         linewidth=self.var2format(varname[1])['linewidth'])
            #set plot limits for two vars by finding the absolute range and adding 10%
            abmin=np.min([np.nanmin(xdata[0]),np.nanmin(xdata[1])])
            abmax=np.max([np.nanmax(xdata[0]),np.nanmax(xdata[1])])
            ax1.set_xlim([abmin - 0.1*(abmax-abmin),abmax + 0.1*(abmax-abmin)])

        ax1.invert_yaxis()
        plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
        plt.xlabel(xlabel[0], fontsize=self.labelsize, fontweight='bold')

        fmt=mpl.ticker.StrMethodFormatter(self.var2format(varname[0])['format'])
        ax1.xaxis.set_major_formatter(fmt)
        ax1.tick_params(axis='both', which='major', labelsize=self.labelsize)

        #plot second param
        ax2 = ax1.twiny()
        p1 = ax2.plot(xdata[2], ydata[1])
        plt.setp(p1, color=self.var2format(varname[2])['color'],
                   linestyle=self.var2format(varname[2])['linestyle'],
                   linewidth=self.var2format(varname[2])['linewidth'])
        if secondary and not (xdata[3].size == 0):
            p1 = ax2.plot(xdata[3],ydata[1])
            plt.setp(p1, color=self.var2format(varname[3])['color'],
                         linestyle=self.var2format(varname[3])['linestyle'],
                         linewidth=self.var2format(varname[3])['linewidth'])
            #set plot limits for two vars by finding the absolute range and adding 10%
            abmin=np.min([np.nanmin(xdata[0]),np.nanmin(xdata[1])])
            abmax=np.max([np.nanmax(xdata[0]),np.nanmax(xdata[1])])
            try:
                ax2.set_xlim([abmin - 0.1*(abmax-abmin),abmax + 0.1*(abmax-abmin)])
            except:
                ax2.set_xlim([0,1])

        plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
        plt.xlabel(xlabel[1], fontsize=self.labelsize, fontweight='bold')

        #set xticks and labels to be at the same spot for all three vars
        ax1.set_xticks(np.linspace(ax1.get_xbound()[0], ax1.get_xbound()[1], self.max_xticks))
        ax2.set_xticks(np.linspace(ax2.get_xbound()[0], ax2.get_xbound()[1], self.max_xticks))

        fmt=mpl.ticker.StrMethodFormatter(self.var2format(varname[2])['format'])
        ax2.xaxis.set_major_formatter(fmt)
        ax2.tick_params(axis='x', which='major', labelsize=self.labelsize)

        return plt, fig    

    def plot3var(self, varname=None, xdata=None, ydata=None, xlabel=None, secondary=False, **kwargs):
        fig = plt.figure(1)
        ax1 = fig.add_subplot(111)
        p1 = ax1.plot(xdata[0], ydata)
        plt.setp(p1, color=self.var2format(varname[0])['color'],
                    linestyle=self.var2format(varname[0])['linestyle'],
                    linewidth=self.var2format(varname[0])['linewidth'])
        if secondary and not (xdata[1].size == 0):
          p1 = ax1.plot(xdata[1],ydata)
          plt.setp(p1, color=self.var2format(varname[1])['color'],
                      linestyle=self.var2format(varname[1])['linestyle'],
                      linewidth=self.var2format(varname[1])['linewidth'])
          #set plot limits for two vars by finding the absolute range and adding 10%
          abmin=np.nanmin([np.nanmin(xdata[0]),np.nanmin(xdata[1])])
          abmax=np.nanmax([np.nanmax(xdata[0]),np.nanmax(xdata[1])])
          ax1.set_xlim([abmin - 0.1*(abmax-abmin),abmax + 0.1*(abmax-abmin)])

        ax1.invert_yaxis()
        plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
        plt.xlabel(xlabel[0], fontsize=self.labelsize, fontweight='bold')
      
        fmt=mpl.ticker.StrMethodFormatter(self.var2format(varname[0])['format'])
        ax1.xaxis.set_major_formatter(fmt)
        ax1.tick_params(axis='both', which='major', labelsize=self.labelsize)

        #plot second param
        ax2 = ax1.twiny()
        p1 = ax2.plot(xdata[2], ydata)
        plt.setp(p1, color=self.var2format(varname[2])['color'],
                    linestyle=self.var2format(varname[2])['linestyle'],
                    linewidth=self.var2format(varname[2])['linewidth'])
        if secondary and not (xdata[3].size == 0):
          p1 = ax2.plot(xdata[3],ydata)
          plt.setp(p1, color=self.var2format(varname[3])['color'],
                      linestyle=self.var2format(varname[3])['linestyle'],
                      linewidth=self.var2format(varname[3])['linewidth'])
          #set plot limits for two vars by finding the absolute range and adding 10%
          abmin=np.nanmin([np.nanmin(xdata[2]),np.nanmin(xdata[3])])
          abmax=np.nanmax([np.nanmax(xdata[2]),np.nanmax(xdata[3])])
          try:
            ax2.set_xlim([abmin - 0.1*(abmax-abmin),abmax + 0.1*(abmax-abmin)])
          except:
            ax2.set_xlim([0,1])

        plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
        plt.xlabel(xlabel[1], fontsize=self.labelsize, fontweight='bold')

        fmt=mpl.ticker.StrMethodFormatter(self.var2format(varname[2])['format'])
        ax2.xaxis.set_major_formatter(fmt)
        ax2.tick_params(axis='x', which='major', labelsize=self.labelsize)

        ax3 = ax1.twiny()
        ax3.spines["top"].set_position(("axes", 1.05))
        self.make_patch_spines_invisible(ax3)
        # Second, show the right spine.
        ax3.spines["top"].set_visible(True)
        p1 = ax3.plot(xdata[4], ydata)
        plt.setp(p1, color=self.var2format(varname[4])['color'],
                    linestyle=self.var2format(varname[4])['linestyle'],
                    linewidth=self.var2format(varname[4])['linewidth'])
        if secondary and not (xdata[5].size == 0):
          p1 = ax2.plot(xdata[5],ydata)
          plt.setp(p1, color=self.var2format(varname[5])['color'],
                      linestyle=self.var2format(varname[5])['linestyle'],
                      linewidth=self.var2format(varname[5])['linewidth'])
          #set plot limits for two vars by finding the absolute range and adding 10%
          abmin=np.nanmin([np.nanmin(xdata[4]),np.nanmin(xdata[5])])
          abmax=np.nanmax([np.nanmax(xdata[4]),np.nanmax(xdata[5])])
          ax3.set_xlim([abmin - 0.1*(abmax-abmin),abmax + 0.1*(abmax-abmin)])

        plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
        plt.xlabel(xlabel[2], fontsize=self.labelsize, fontweight='bold')

        #set bounds based on max and min values

        #set xticks and labels to be at the same spot for all three vars
        ax1.set_xticks(np.linspace(ax1.get_xbound()[0], ax1.get_xbound()[1], self.max_xticks))
        ax2.set_xticks(np.linspace(ax2.get_xbound()[0], ax2.get_xbound()[1], self.max_xticks))
        ax3.set_xticks(np.linspace(ax3.get_xbound()[0], ax3.get_xbound()[1], self.max_xticks))

        fmt=mpl.ticker.StrMethodFormatter(self.var2format(varname[4])['format'])
        ax3.xaxis.set_major_formatter(fmt)
        ax3.tick_params(axis='x', which='major', labelsize=self.labelsize)

        return plt, fig

    @staticmethod
    def var2format(varname):
        """list of plot specifics based on variable name"""
        plotdic={}
        if varname in ['temperature_ch1']:
          plotdic['color']='red'
          plotdic['linestyle']='-'
          plotdic['linewidth']=0.5
          plotdic['format']='{x:.3f}'
        elif varname in ['temperature_ch2']:
          plotdic['color']='magenta'
          plotdic['linestyle']='--'
          plotdic['linewidth']=0.5
          plotdic['format']='{x:.3f}'
        elif varname in ['salinity_ch1', 'oxy_percentsat_ch1', 'oxy_conc_ch1']:
          plotdic['color']='blue'
          plotdic['linestyle']='-'
          plotdic['linewidth']=0.5
          if varname in ['salinity_ch1']:
            plotdic['format']='{x:.3f}'
          else:
            plotdic['format']='{x:3.1f}'
        elif varname in ['salinity_ch2', 'oxy_percentsat_ch2', 'oxy_conc_ch2']:
          plotdic['color']='cyan'
          plotdic['linestyle']='--'
          plotdic['linewidth']=0.5
          plotdic['format']='{x:3.1f}'
          if varname in ['salinity_ch2']:
            plotdic['format']='{x:.3f}'
          else:
            plotdic['format']='{x:3.1f}'
        elif varname in ['sigmatheta','turbidity','sigmaT']:
          plotdic['color']='black'
          plotdic['linestyle']='-'
          plotdic['linewidth']=0.5
          plotdic['format']='{x:.3f}'
        elif varname in ['chlor_fluorescence']:
          plotdic['color']='green'
          plotdic['linestyle']='-'
          plotdic['linewidth']=0.5
          plotdic['format']='{x:.2f}'
        elif varname in ['par']:
          plotdic['color']='darkorange'
          plotdic['linestyle']='-'
          plotdic['linewidth']=0.75
          plotdic['format']='{x:5.0f}'
        else:
          plotdic['color']='black'
          plotdic['linestyle']='--'
          plotdic['linewidth']=1.0      
          plotdic['format']='{x:.3f}'

        return plotdic

    @staticmethod
    #python3 change as dictionaries no longer have itervalues methods
    def make_patch_spines_invisible(ax):
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        for sp in ax.spines.values():
            sp.set_visible(False)
            

def plot_salvtemp(cruise=None, cast=None, salt=None, temp=None, press=None, srange=[28,34], trange=[-2,15], ptitle=""): 
    plt.style.use('ggplot')
    
    # Figure out boudaries (mins and maxs)
    smin = srange[0]
    smax = srange[1]
    tmin = trange[0]
    tmax = trange[1]

    # Calculate how many gridcells we need in the x and y dimensions
    xdim = int(round((smax-smin)/0.1+1,0))
    ydim = int(round((tmax-tmin)+1,0))
    
    #print 'ydim: ' + str(ydim) + ' xdim: ' + str(xdim) + ' \n'
    if (xdim > 10000) or (ydim > 10000): 
        print('To many dimensions for grid in {cruise} {cast} file. \
              Likely  missing data \n'.format(cruise=cruise,cast=cast))
        return
 
    # Create empty grid of zeros
    dens = np.zeros((ydim,xdim))
 
    # Create temp and salt vectors of appropiate dimensions
    ti = np.linspace(0,ydim-1,ydim)+tmin
    si = np.linspace(0,xdim-1,xdim)*0.1+smin
 
    # Loop to fill in grid with densities
    for j in range(0,int(ydim)):
        for i in range(0, int(xdim)):
            dens[j,i]=sw.dens0(si[i],ti[j])
 
    # Substract 1000 to convert to sigma-t
    dens = dens - 1000
 
    # Plot data ***********************************************
    fig, ax1 = plt.subplots(figsize=(8, 8), facecolor='w', edgecolor='w')
    CS = plt.contour(si,ti,dens, linestyles='dashed', colors='gray')
    plt.clabel(CS, fontsize=12, inline=1, fmt='%1.1f') # Label every second level
 
    ts = ax1.scatter(salt,temp, c=press, cmap='gray', s=10)
    cbar = plt.colorbar(ts)
    cbar.ax.tick_params(labelsize=14) 

    plt.ylim(tmin,tmax)
    plt.xlim(smin,smax)
    plt.tick_params(axis='both', which='major', labelsize=14)
 
    ax1.set_xlabel('Salinity (PSU)',fontsize=16)
    ax1.set_ylabel('Temperature (C)',fontsize=16)

    fig.suptitle(ptitle, fontsize=18, fontweight='bold')
    return fig  
