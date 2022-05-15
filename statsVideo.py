#!/usr/local/bin/python3.8

from bokeh.io import show
from bokeh.io.export import get_screenshot_as_png
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from selenium import webdriver
import PIL.Image
from MyNote import MyNote

# driver = webdriver.Firefox(firefox_binary='/Applications/Firefox.app/Contents/MacOS/firefox',
#                            executable_path='/usr/local/bin/geckodriver')

import cv2
import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import re
import time

NOTE_OCTAVE_PATTERN = re.compile("^(\D+)(\d*)")
FPS = 24

# ♭ ♯
CANONICAL_KEY_MAP = {
    "A-": "A♭",
    "B-": "B♭",
    "D-": "D♭",
    "E-": "E♭",
    "G-": "G♭",

    "C#": "C♯",
    "D#": "D♯",
    "F#": "F♯",

    "F-": "E",
    "B--": "A",
    "C-": "B",
    "E--": "D",
}


def getMeasureFromAbsoluteBeat(beatsPerMeasure, absoluteBeat):
    return None if absoluteBeat == None else int(absoluteBeat / beatsPerMeasure) + (0 if absoluteBeat % beatsPerMeasure == 0 else 1)


def getPrettyKeyName(key):
    match = NOTE_OCTAVE_PATTERN.match(key)
    thisKey, thisOctave = match.groups()

    if thisKey in CANONICAL_KEY_MAP:
        thisKey = CANONICAL_KEY_MAP[thisKey]

    return thisKey + thisOctave


def frame2Info(beatsPerMeasure, messages, frame, stats, beats):
    elapsed = (frame - 1) / FPS

    currentBeatIndex = None
    currentBeat = 0
    histograms = {}

    for beatIndex in range(0, len(beats)):
        thisBeat = beats[beatIndex]["performance"]
        nextBeat = None if beatIndex + 1 == len(beats) else beats[beatIndex + 1]["performance"]

        if thisBeat > elapsed:
            break

        if elapsed >= thisBeat and (nextBeat == None or elapsed < nextBeat):
            currentBeatIndex = beatIndex
            currentBeat = thisBeat
            break

    beat = None if currentBeatIndex == None else currentBeatIndex + 1

    notesPlayed = 0
    for key in sorted(stats['offsetsCount']):
        if currentBeatIndex == None or int(key) > currentBeatIndex:
            break

        notesPlayed += stats['offsetsCount'][key]

    message = None
    if beat:
        for myThisBeat in range(1, beat + 1):
            for histogramType in ['global', 'note']:
                if histogramType in stats['histogram'] and str(myThisBeat) in stats['histogram'][histogramType]:
                    thisGlobal = stats['histogram'][histogramType][str(myThisBeat)]

                    if histogramType not in histograms:
                        histograms[histogramType] = {}

                    for key, value in thisGlobal.items():
                        if key not in histograms[histogramType]:
                            histograms[histogramType][key] = value
                        else:
                            histograms[histogramType][key] += value

        for thisMessage in messages:
            if beat >= thisMessage['startBeat'] and beat <= thisMessage['endBeat']:
                message = thisMessage['message']
                break

    print(f"{frame=} {elapsed=} {currentBeatIndex=} {currentBeat=} {notesPlayed=}")

    return {
        'elapsed': elapsed,
        'beat': beat,
        'measure': getMeasureFromAbsoluteBeat(beatsPerMeasure, beat),
        'beatInMeasure': None if beat == None else (currentBeatIndex % beatsPerMeasure) + 1,
        'histograms': histograms,
        'notesPlayed': notesPlayed,
        'notesPerSecond': None if elapsed == 0 else notesPlayed / elapsed,
        'beatsPerSecond': None if (elapsed == 0 or currentBeatIndex == None) else currentBeatIndex / elapsed,
        'beatsPerMinute': None if (elapsed == 0 or currentBeatIndex == None) else currentBeatIndex / elapsed * 60,
        # 'key': None if beat == None or stats['keys'][beat - 1] == None else f"{stats['keys'][beat - 1]['name']} {stats['keys'][beat - 1]['flavor']}",
        'message': message
    }


def computeTimings(directory, stats, align, beatsPerMeasure):
    timings = []

    beatsHintsPath = directory + '/beatsHints.json'

    beatsHints = None
    if os.path.exists(beatsHintsPath):
        with open(beatsHintsPath) as beatsHintsFile:
            beatsHints = json.load(beatsHintsFile)

    for thisAlignIndex in range(0, len(align)):
        for scoreTiming in stats['scoreTimings']:
            thisAlign = align[thisAlignIndex]

            frame = None

            if beatsHints != None and str(len(timings)) in beatsHints:
                # frame = int(beatsHints[str(len(timings))])
                print('not supported :(')
            elif thisAlign['score'] >= scoreTiming['elapsed']:
                frame = FPS * int(thisAlign['performance']) + int(FPS * (thisAlign['performance'] - int(thisAlign['performance'])))

            if frame != None:
                timings.append({
                    "absoluteBeat": scoreTiming['beat'],
                    "measure": getMeasureFromAbsoluteBeat(beatsPerMeasure, scoreTiming['beat']),
                    "performance": thisAlign['performance'],
                    "frame": frame
                })
                break

    return timings


def go(path, beatsPerMeasure):
    directory = os.path.dirname(path)
    statsFilename = f"{directory}/stats.json"
    messagesFilename = f"{directory}/messages.json"
    alignFilename = f"{directory}/align.json"

    with open(statsFilename) as f:
        tempStats = json.load(f)

        stats = {
            'histogram': tempStats['histogram'],
            'keys': tempStats['keys'],
            'scoreTimings': tempStats['scoreTimings'],
            'offsetsCount': {}
        }
        for key in tempStats['offsetsCount']:
            stats['offsetsCount'][float(key)] = tempStats['offsetsCount'][key]

    if os.path.exists(messagesFilename):
        with open(messagesFilename) as f:
            messages = json.load(f)
    else:
        messages = []

    print(f'{alignFilename=}')
    with open(alignFilename) as f:
        align = json.load(f)

    totalNotes = 0

    maxElapsed = None
    for alignData in align:
        if maxElapsed == None or alignData['performance'] > maxElapsed:
            maxElapsed = alignData['performance'] + 1

    fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 40)

    mainImageOut = cv2.VideoWriter(directory + '/statsVideo.mp4', cv2.VideoWriter_fourcc(*'MP4V'), FPS, (495, 1080))
    histogramInfo = {
        'global': {
            'width': 768,
            'height': 216,
            'title': 'Global'
        },
        'note': {
            'width': 384,
            'height': 216,
            'title': 'By Note'
        }
    }

    for histogramType in ['global', 'note']:
        histogramInfo[histogramType]['file'] = cv2.VideoWriter(f'{directory}/{histogramType}HistogramOut.mp4', cv2.VideoWriter_fourcc(*'MP4V'), FPS,
                                                               (histogramInfo[histogramType]['width'], histogramInfo[histogramType]['height']))

    maxFrame = int(maxElapsed) * FPS + FPS

    textColor = (0, 0, 0)

    beats = computeTimings(directory, stats, align, beatsPerMeasure)

    with open(directory + '/beats.json', 'w') as outfile:
        json.dump(beats, outfile, indent=4)

    for frame in range(1, maxFrame):
        # if frame > 12:
        #     break

        info = frame2Info(beatsPerMeasure, messages, frame, stats, beats)
        image = Image.new('RGB', (495, 1080), color=(220, 220, 220))
        print(f"{frame} / {maxFrame - 1}")
        d = ImageDraw.Draw(image)
        d.text((10, 10), f"frame number -> {str(frame).rjust(len(str(maxFrame)))}", font=fnt, fill=textColor)
        d.text((10, 110), f"elapsed -> {str(round(info['elapsed'], 2))}", font=fnt, fill=textColor)
        d.text((10, 210), f"beat -> {info['beat']}", font=fnt, fill=textColor)
        d.text((10, 310), f"notesPlayed -> {info['notesPlayed']}", font=fnt, fill=textColor)
        d.text((10, 410), f"notesPerSecond -> {None if info['notesPerSecond'] == None else str(round(info['notesPerSecond'], 2))}", font=fnt, fill=textColor)
        d.text((10, 510), f"beatsPerSecond -> {None if info['beatsPerSecond'] == None else str(round(info['beatsPerSecond'], 2))}", font=fnt, fill=textColor)
        d.text((10, 610), f"beatsPerMinute -> {None if info['beatsPerMinute'] == None else str(round(info['beatsPerMinute'], 0))}", font=fnt, fill=textColor)
        d.text((10, 710), f"measure -> {None if info['measure'] == None else info['measure']}", font=fnt, fill=textColor)
        d.text((10, 810), f"beatInMeasure -> {None if info['beatInMeasure'] == None else info['beatInMeasure']}", font=fnt, fill=textColor)
        # d.text((10, 910), f"key -> {'' if info['key'] == None else info['key']}", font=fnt, fill=textColor)
        d.text((10, 1010), f"message -> {'' if info['message'] == None else info['message']}", font=fnt, fill=textColor)

        mainImageOut.write(np.array(image))

        # for histogramType in ['global', 'note']:
        for histogramType in []:
            labels = []
            counts = []

            for key, value in sorted(info['histograms'][histogramType].items()):
                if histogramType == 'global':
                    labels.append(getPrettyKeyName(MyNote.getNoteWithOctave(key)))
                else:
                    labels.append(getPrettyKeyName(str(key)))
                counts.append(value)

            plot = figure(x_range=labels, plot_width=histogramInfo[histogramType]['width'], plot_height=histogramInfo[histogramType]['height'],
                          title=histogramInfo[histogramType]['title'],
                          toolbar_location=None, tools="")
            plot.yaxis.minor_tick_line_alpha = 0.0
            #            plot.yaxis.minor_tick_line_cap = None  # turn off y-axis minor ticks
            plot.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
            #            plot.yaxis.minor_tick_line_join = None  # turn off y-axis minor ticks
            plot.yaxis.minor_tick_line_width = 0  # turn off y-axis minor ticks
            plot.yaxis.minor_tick_out = 0
            plot.xgrid.grid_line_color = None
            plot.y_range.start = 0
            plot.vbar(x=labels, top=counts, width=0.9, hatch_color=None)
            # histogramImageA = get_screenshot_as_png(plot, driver=driver)
            # histogramImage = histogramImageA.convert('RGB')
            # histogramInfo[histogramType]['file'].write(np.array(histogramImage))

    mainImageOut.release()
    for histogramType in ['global', 'note']:
        histogramInfo[histogramType]['file'].release()


start = int(time.time())
go("/Users/earlcahill/music-video-experiments/goldbergs/01-Aria/01-Aria-performance.wav", 3)
# go("/Users/earlcahill/music-video-experiments/transcendental_etude_no_10/transcendental_etude_no_10-Albert.wav", 2)
print(f"elapsed: {int(time.time()) - start}")

# steps
# - export musicxml as wav 44100 from musescore, making sure to not play the repeats - /Users/earlcahill/music-video-experiments/goldbergs/01-Aria/01-Aria-midi-recording.wav
# - export performance as wav 44100 /Users/earlcahill/music-video-experiments/goldbergs/01-Aria/01-Aria-performance.wav
# - run align with files changed (took 412 seconds for the Aria)
# - change output to align.json (:%s/^\([0-9.]*\) *\([0-9.]*\) *$/    {"score" : \1, "performance" : \2},/) - /Users/earlcahill/music-video-experiments/goldbergs/align.json
# - cp musicxml over - /Users/earlcahill/music-video-experiments/goldbergs/01-Aria.musicxml
# - potentially create /Users/earlcahill/music-video-experiments/goldbergs/messages.json
# - run fun with this line uncommented - generateGenericStats('/Users/earlcahill/music-video-experiments/goldbergs/01-Aria.musicxml')
