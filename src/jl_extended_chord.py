from jl_note import Note
from enum import Enum
import jl_constants as constants
from jl_extended_interval import ExtendedInterval
from jl_dictionaries import Dictionaries
from pychord_jl import Chord

class ChordMode(Enum):
    Neutral = 0
    Major = 1
    Minor = 2

class ExtendedChord:
    def __init__(self,pychord_chord):
        self.pychord_chord = pychord_chord

    def __str__(self):
        return self.pychord_chord.__str__()

    @property
    def root(self):
        return Note(self.pychord_chord.root)

    @property
    def mode(self):
        components = self.pychord_chord.quality.components
        if constants.MAJOR_INTERVAL in components: return ChordMode.Major
        if constants.MINOR_INTERVAL in components: return ChordMode.Minor

        return ChordMode.Neutral

    @property 
    def note_in_5h_circle(self):
        root_note = Note(self.pychord_chord.root)

        return root_note if self.mode != ChordMode.Minor else root_note.relative_major

    @property
    def x_in_5th_circle(self):
        return self.note_in_5h_circle.x_y_in_5th_circle[0]

    @property
    def y_in_5th_circle(self):
        return self.note_in_5h_circle.x_y_in_5th_circle[1]

    @property
    def slash_bass(self):
        return Note(self.pychord_chord.on or self.pychord_chord.root)

    @property
    def relative_on(self):
        if self.pychord_chord.on is None: return None

        diff = Dictionaries.get_note_value(self.pychord_chord.on) - Dictionaries.get_note_value(self.pychord_chord.root)

        return diff if diff >= 0 else constants.NUMBER_OF_SEMITONES + diff

    @property
    def relative_slash_bass(self):
        return self.slash_bass - self.root

    @property
    def relative_slash_x(self):
        return self.relative_slash_bass[0]

    @property
    def relative_slash_y(self):
        return self.relative_slash_bass[1]

    @property
    def intervals(self):
        components = self.pychord_chord.quality.components

        intervals = []
        for index, component in enumerate(components):
            for index_2, component_2 in enumerate(components[index:]):
                intervals = [*intervals, component_2 - component]

        intervals = [interval if interval < 12 else interval -12 for interval in intervals if interval > 0]

        return list(set(intervals))

    @property
    def complexity(self):
        complexities = [ExtendedInterval(interval).complexity for interval in self.intervals]

        return sum(complexities) / len(complexities)

    @property
    def components(self):
        components = self.pychord_chord.quality.components

        root = Dictionaries.get_note_value(self.pychord_chord.root)

        components = [(component + root) % constants.NUMBER_OF_NOTES for component in components]

        return components

    @property
    def note_vector(self):
        result = [0] * 12

        for component in self.components:
            result[component] = 1

        return result

    @property
    def standard_name(self):
        standard_root = Dictionaries.get_note_name(Dictionaries.get_note_value(self.pychord_chord.root))

        standard_quality = Dictionaries.get_quality_name(tuple(self.pychord_chord.quality.components))

        return f'{standard_root}{standard_quality}'

    def transpose(self, semitones):
        cloned = Chord(self.pychord_chord.chord)
        cloned.transpose(semitones)
        return ExtendedChord(cloned)