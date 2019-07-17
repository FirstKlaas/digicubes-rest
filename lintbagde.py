from pylint.lint import Run
from pylint.reporters import BaseReporter
from pybadges import badge

class NullReporter(BaseReporter):
    
    def _display(self, layout):
        pass

results = Run(['x4remote'], reporter=NullReporter(), do_exit=False)
global_score = float(results.linter.stats['global_note'])
global_score_txt = f'{global_score:.1f}'
badge_file_name = "source/_static/pylint-badge.svg"

color = 'green'

if global_score < 3.0:
    color = 'red'
elif global_score < 7.0:
    color = 'yellow'

print(f"Pylint score is {global_score_txt}. Writing badge to {badge_file_name}. Badge color is {color}")

with open(badge_file_name,'w') as badge_file:
    badge_file.write(badge(left_text='pylint', right_text=global_score_txt, right_color=color))

