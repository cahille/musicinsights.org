#!/usr/local/bin/python3.8

import cv2
import glob
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FPS = 24


def frame2Info(beatsPerMeasure, messages, frame, stats, beats):
    elapsed = (frame - 1) / FPS

    currentBeatIndex = None
    currentBeat = 0

    for beatIndex in range(0, len(beats)):
        thisBeat = beats[beatIndex]
        nextBeat = None if beatIndex + 1 == len(beats) else beats[beatIndex + 1]

        if thisBeat > elapsed:
            break

        if elapsed >= thisBeat and (nextBeat == None or elapsed < nextBeat):
            currentBeatIndex = beatIndex
            currentBeat = thisBeat
            break

    beat = None if currentBeatIndex == None else currentBeatIndex + 1

    notesPlayed = 0
    for key in sorted(stats['intOffsetsCount']):
        if currentBeatIndex == None or key > currentBeatIndex:
            break

        notesPlayed += stats['intOffsetsCount'][key]

    message = None
    if beat:
        for thisMessage in messages:
            if beat >= thisMessage['startBeat'] and beat <= thisMessage['endBeat']:
                message = thisMessage['message']
                break

    print(f"{frame=} {elapsed=} {currentBeatIndex=} {currentBeat=} {notesPlayed=}")

    return {
        'elapsed': elapsed,
        'beat': beat,
        'measure': None if beat == None else int(beat / beatsPerMeasure) + 1,
        'beatInMeasure': None if beat == None else (currentBeatIndex % beatsPerMeasure) + 1,
        'notesPlayed': notesPlayed,
        'notesPerSecond': None if elapsed == 0 else notesPlayed / elapsed,
        'beatsPerSecond': None if (elapsed == 0 or currentBeatIndex == None) else currentBeatIndex / elapsed,
        'beatsPerMinute': None if (elapsed == 0 or currentBeatIndex == None) else currentBeatIndex / elapsed * 60,
        'key': None if beat == None or beat not in stats['keys'] else stats['keys'][beat],
        'message': message
    }


def go(directory, movement, beatsPerMeasure):
    statsFilename = f"{directory}/stats.json"
    messagesFilename = f"{directory}/messages.json"
    beatsFilename = f"{directory}/beats.json"
    alignFilename = f"{directory}/align.txt"

    stats = {}

    with open(statsFilename) as f:
        tempStats = json.load(f)

        for statsType in tempStats:
            if movement in tempStats[statsType]:
                stats[statsType] = {}

                for key in tempStats[statsType][movement]:
                    if statsType == 'intOffsetsCount':
                        stats[statsType][int(key)] = tempStats[statsType][movement][key]
                    elif statsType == 'keys':
                        stats[statsType][len(stats[statsType]) + 1] = f"{key['name']} {key['flavor']}"

    with open(messagesFilename) as f:
        messages = json.load(f)[movement]

    with open(beatsFilename) as f:
        beats = json.load(f)[movement]
        maxBeatTime = beats[-1]

    totalNotes = 0

    maxBeat = None
    for beat in stats['intOffsetsCount']:
        totalNotes += stats['intOffsetsCount'][beat]
        if maxBeat == None or int(beat) + 1 > maxBeat:
            maxBeat = int(beat) + 1

    fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 40)

    out = cv2.VideoWriter(directory + '/statsVideo.mp4', cv2.VideoWriter_fourcc(*'MP4V'), FPS, (1920, 1080))

    maxFrame = int(maxBeatTime) * FPS + FPS
    textColor = (0, 0, 0)

    for frame in range(1, maxFrame):
        info = frame2Info(beatsPerMeasure, messages, frame, stats, beats)
        image = Image.new('RGB', (1920, 1080), color=(220, 220, 220))
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
        d.text((10, 910), f"key -> {'' if info['key'] == None else info['key']}", font=fnt, fill=textColor)
        d.text((10, 1010), f"message -> {'' if info['message'] == None else info['message']}", font=fnt, fill=textColor)

        out.write(np.array(image))

    #        image.save(f'/Users/earlcahill/frames/{frame:05}.png')

    # filenames = glob.glob('/Users/earlcahill/frames/*.png')
    #
    # filenames.sort()
    #
    # for filename in filenames:
    #     print(filename)
    #     image = cv2.imread(filename)
    #     out.write(image)

    out.release()


go("/Users/earlcahill/music-video-experiments/transcendental_etude_no_10", 'feux_follets', 2)
