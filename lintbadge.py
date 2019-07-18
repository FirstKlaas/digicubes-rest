from pylint.lint import Run
from pylint.reporters import BaseReporter
from pybadges import badge

class NullReporter(BaseReporter):
    
    def _display(self, layout):
        pass

results = Run(['digicubes'], reporter=NullReporter(), do_exit=False)
global_score = float(results.linter.stats['global_note'])
global_score_txt = f'{global_score:.1f}'
badge_file_name = "source/_static/pylint-badge.svg"

color = 'green'

if global_score < 3.0:
    color = 'red'
elif global_score < 7.0:
    color = 'yellow'

with open("source/_static/python_version.svg", 'w') as badge_file:
    badge_file.write(badge(left_text='python', right_text="3.7", right_color="blue"))

with open(badge_file_name, 'w') as badge_file:
    badge_file.write(badge(left_text='pylint score', right_text=global_score_txt, right_color=color))

with open("source/_static/style_black.svg", 'w') as badge_file:
    badge_file.write(badge(left_text='style', right_text="black", right_color="black"))

