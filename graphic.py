import codecs
import numpy
import json

from collections import namedtuple
from matplotlib import pyplot
from matplotlib.widgets import TextBox


translation = {}

try:
    with codecs.open('i18n.json', 'r', 'utf-8') as translationFile:
        translation = json.load(translationFile)
except (IOError, ValueError):
    print('Could not get or parse translation')

def translate(key):
    return translation.get(key, key)


class Plot(namedtuple('Plot', ('label', 'coords'))):
    @property
    def start(self):
        return min(self.coords)

    @property
    def end(self):
        return max(self.coords)

    @property
    def size(self):
        return self.end - self.start

    def membership(self, x):
        a, b, c, d = self.coords

        if d < x or x < a:
            return 0
        elif a <= x < b:
            return (x - a) / (b - a)
        elif b <= x <= c:
            return 1
        elif c < x <= d:
            return (d - x) / (d - c)

class Layout(namedtuple('Layout', ('title', 'start', 'end'))):
    _LEGEND_LOCATION = 'center left'
    _Y_LABEL = 'Y'

    def __init__(self, *args, **kwargs):
        super(Layout, self).__init__()

        self.values = {}
        self.plots = set()

    @property
    def size(self):
        return self.end - self.start

    def add(self, plot):
        self.plots.add(plot)

    def create(self, axis):
        values = self.values

        for plot in self.plots:
            xValues = plot.start + numpy.arange(plot.size)
            yValues = numpy.array([plot.membership(x) for x in xValues])

            for x in xValues:
                newY = plot.membership(x)

                oldY = values.get(x)
                if oldY is not None and oldY > newY:
                    continue

                values[x] = newY

            axis.plot(xValues, yValues, label=plot.label)

        axis.set_title(self.title)
        axis.set_ylabel(self._Y_LABEL)
        axis.set_xlim(xmin=self.start, xmax=self.end)
        axis.legend(loc=self._LEGEND_LOCATION)


class Figure(object):
    _TITLE = 'Heating system'
    _SIZE = (20, 10)
    _GRID_SIZE = (4, 8)

    _TEXTBOX_RECT = (0, 7, 2, 1)
    _TEXTBOX_LABEL = 'Water temperature:'

    _TEXT_LABEL_RECT = (2, 7, 2, 1)
    _TEXT_LABEL_TEXT = 'Membership function value:'

    _LAYOUTS_DATA = {
        'Square Footage': {
            'rect': (0, 0, 4, 2),
            'start': 200,
            'end': 1000,
            'plotsData': {
                'Low square': (199, 200, 450, 510),
                'Medium square': (450, 480, 720, 780),
                'Big square': (710, 750, 1000, 1001)
            }
        },
        'Street Temperature': {
            'rect': (0, 2, 4, 2),
            'start': -30,
            'end': 30,
            'plotsData': {
                'Low temperature': (-31, -30, 2, 6),
                'Medium temperature': (1, 5, 18, 21),
                'High temperature': (20, 23, 30, 32)
            }
        },
        'Water Temperature': {
            'rect': (0, 4, 4, 3),
            'start': 40,
            'end': 105,
            'plotsData': {
                'Low temperature': (39, 40, 57, 65),
                'Medium temperature': (55, 60, 79, 83),
                'High temperature': (78, 83, 105, 106)
            }
        }
    }
    
    def __init__(self):
        super(Figure, self).__init__()

        gridSize = self._GRID_SIZE[::-1]

        figure = pyplot.figure(figsize=self._SIZE)

        self.__layouts = layouts = {}

        for layoutTitle, layoutData in self._LAYOUTS_DATA.items():
            x, y, width, height = layoutData['rect']
            
            axis = pyplot.subplot2grid(gridSize, (y, x), rowspan=height, colspan=width, fig=figure)

            layout = layouts[layoutTitle] = Layout(
                title=translate(layoutTitle),
                start=layoutData['start'],
                end=layoutData['end']
            )
            
            for plotTitle, plotCoords in layoutData['plotsData'].items():
                layout.add(Plot(
                    label=translate(plotTitle),
                    coords=tuple(map(float, plotCoords))
                ))

            layout.create(axis)

        x, y, width, height = self._TEXTBOX_RECT

        textboxAxis = pyplot.subplot2grid(gridSize, (y, x), rowspan=height, colspan=width, fig=figure)

        textbox = TextBox(textboxAxis, translate(self._TEXTBOX_LABEL))
        textbox.on_submit(self.onTextChanged)
        textbox.on_text_change(self.onTextChanged)

        x, y, width, height = self._TEXT_LABEL_RECT

        textLabelAxis = pyplot.subplot2grid(gridSize, (y, x), rowspan=height, colspan=width, fig=figure)
        self.textLabel = TextBox(textLabelAxis, translate(self._TEXT_LABEL_TEXT))

        figure.canvas.set_window_title(translate(self._TITLE))
        figure.tight_layout()

        pyplot.show()

    def onTextChanged(self, text):
        if not text:
            self.textLabel.set_val('')
            return

        try:
            waterTemperature = int(text)
        except ValueError:
            self.textLabel.set_val(translate('Incorrect water temperature value'))
            return

        membershipValue = self.__layouts['Water Temperature'].values.get(waterTemperature)
        if membershipValue is None:
            self.textLabel.set_val(translate('Incorrect water temperature value'))
            return

        self.textLabel.set_val(str(round(membershipValue, 4)))


figure = Figure()
