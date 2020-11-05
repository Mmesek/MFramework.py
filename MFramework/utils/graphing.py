from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

colors = {
    "Human":"white",
    "Vampire": "tab:red",
    "Werewolf": "tab:orange",
    "Zombie": "tab:green",
    "Vampire Hunter": "tab:blue",
    "Huntsman": "tab:purple",
    "Zombie Slayer": "tab:cyan"
}
markers = {
    "Human":"",
    "Vampire": ".",
    "Werewolf": ".",
    "Zombie": ".",
    "Vampire Hunter": ".",
    "Huntsman": ".",
    "Zombie Slayer": "."
}

def timeseries(ax, total: dict(name=dict(x=list, y=list)), resample, growth):
    for i in total:
        if total[i] == {}:
            continue
        if not growth:
            df = pd.Series(total[i]['y'], index=total[i]['x'])
            df.index = pd.to_datetime(df.index, utc=True)
            #df = df.resample(resample).count()
            idf = pd.to_datetime(df.index)

            ax.plot(idf, df, label=i, marker=markers.get(i), color=colors.get(i))
        else:
            df = pd.Series(total[i]['x'], index=total[i]['y'])
            ax.plot(df, df.index, label=i)

def plot(data_to_plot, resample, growth, locator, interval):
    fig, ax = plt.subplots(figsize=(12, 8))
    #fig.subplots_adjust()
    ax.patch.set_facecolor('#333333')
    plt.style.use(['dark_background'])
    
    timeseries(ax, data_to_plot, resample, growth)

    set_locator(ax, locator, interval)
    fig.autofmt_xdate()
    ax.tick_params(labelcolor='tab:orange', color='tab:orange', labelsize=17)
    ax.tick_params(which='minor', labelcolor='tab:orange', color='tab:orange', labelsize=15)


    #Set Names
    set_legend(ax, 'Halloween 2020 Summary', 'Population', 'Days', loc='upper left', framealpha=255)
    fig.tight_layout()

    return create_image(fig)

def set_locator(ax, locator, interval):
    locator = locator.lower()
    major = '%d/%m'
    minor = '%H/%d'
    if locator == 'minute':
        ax.xaxis.set_major_locator(mdates.HourLocator())
        lctr = mdates.MinuteLocator(interval=int(interval))
        major = '%H/%d'
        minor = '%M:%H'
    elif locator == 'hour':
        ax.xaxis.set_major_locator(mdates.DayLocator())
        lctr = mdates.HourLocator(interval=int(interval))
        major = '%d/%m'
        minor = '%H'
    elif locator == 'day':
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=7))
        lctr = mdates.DayLocator(interval=int(interval))
        major = '%d/%m'
        minor = '%d'
    elif locator == 'week':
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        lctr = mdates.WeekdayLocator(interval=int(interval))
        major = '%m/%y'
        minor = '%d'
    elif locator == 'month':
        ax.xaxis.set_major_locator(mdates.YearLocator())
        lctr = mdates.MonthLocator(interval=int(interval))
        major = '%y'
        minor = '%m'
    elif locator == 'year':
        lctr = mdates.YearLocator()

    ax.xaxis.set_minor_locator(lctr)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter(major))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter(minor))

def set_legend(ax, title, y, x, loc='best', framealpha=100, text_color="tab:orange"):
    ax.legend(fontsize=16, loc=loc, framealpha=framealpha)
    ax.set_title(title, color=text_color, size=25)
    ax.set_ylabel(y, color=text_color, size=23)
    ax.set_xlabel(x, color=text_color, size=23)

def create_image(fig):
    buffered = BytesIO()
    fig.savefig(buffered)
    img_str = buffered.getvalue()
    return img_str