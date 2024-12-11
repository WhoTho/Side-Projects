"""
Created Date: Jun 23 2024, 02:44:35 PM
Author: @WhoTho whotho06@gmail.com
-----
Last Modified: Jun 29 2024, 11:14:32 PM
Modified By: @WhoTho
-----
CHANGE LOG:
Date                        | Comments
----------------------------+---------------------------------------------
"""

from keybinds import KEYBINDS
from runner import Instruction, allGameData
from pynput import mouse, keyboard
import time
import os

mapName = "carved"
strategyName = "halfCash"


def doMap(mapName, strategyName):
    global lastMapName

    if os.path.exists(f"maps/{mapName}-{strategyName}.txt"):
        print("Map file already exists")
        return
        # if input("Overwrite? (y/n): ").lower() != "y":
        #     return

    if lastMapName and lastMapName != mapName:
        print()
        print(mapName)
        keyboardController = keyboard.Controller()
        keyboardController.tap(keyboard.Key.esc)

    lastMapName = mapName

    print(f"Creating map file for {mapName} using strategy {strategyName}")

    instructions = []
    doesStartExist = False

    print("This strategy consists of:")
    with open(f"strategies/{strategyName}.txt", "r") as f:
        for line in f.readlines():
            if line.startswith("#"):
                continue
            type, *args = line.strip().split(Instruction.DELIMITER)
            if type == "start":
                doesStartExist = True
                print("  start")
                continue

            if type not in ["place", "sell", "set targeting"]:
                continue

            if type == "set targeting" and args[1] != "custom":
                continue

            if args[0].split()[0] not in KEYBINDS:
                print(f"Invalid tower type: {args[0]}")
                continue

            instructions.append((type, args[0]))

            print(f"  {type} {args[0]}")
    print()

    if not doesStartExist:
        print("No start instruction found in strategy file")
        return

    print("Press space to start placing towers")
    keyboardController = keyboard.Controller()
    with keyboard.Listener(on_press=lambda key: key != keyboard.Key.space) as listener:
        listener.join()

    time.sleep(1)

    fileLines = []

    towerName = None
    position = None

    def onClick(x, y, button, pressed):
        nonlocal towerName, position

        if not towerName:
            return True

        if pressed:
            return True

        position = (x, y)
        return False

    def doTowerPlacement(towerName):
        nonlocal position

        keyboardController.tap(KEYBINDS[towerName.split()[0]])

        position = None

        with mouse.Listener(on_click=onClick) as listener:
            listener.join()

        if not position:
            print("Cancelled")
            return

        fileLines.append(
            Instruction.DELIMITER.join(
                ["placement", towerName, str(position[0]), str(position[1])]
            )
        )

    def doTowerSell(towerName):
        print("click on the tower to sell")

        with mouse.Listener(on_click=onClick) as listener:
            listener.join()

        time.sleep(0.1)
        keyboardController.press(keyboard.Key[KEYBINDS["sell"]])
        time.sleep(0.05)
        keyboardController.release(keyboard.Key[KEYBINDS["sell"]])

        # dont need to tell the runner anything about selling
        # fileLines.append(
        #     Instruction.DELIMITER.join(
        #         ["sell", towerName]
        #     )
        # )

    def doSetTargeting(towerName):
        nonlocal position

        print("click on the tower to set targeting")

        with mouse.Listener(on_click=onClick) as listener:
            listener.join()

        print("click on the set target button")

        with mouse.Listener(on_click=onClick) as listener:
            listener.join()

        print("click on the target")

        with mouse.Listener(on_click=onClick) as listener:
            listener.join()

        fileLines.append(
            Instruction.DELIMITER.join(
                ["set targeting", towerName, str(position[0]), str(position[1])]
            )
        )

    for type, towerName in instructions:
        print(type, towerName)
        if type == "place":
            doTowerPlacement(towerName)
        elif type == "sell":
            doTowerSell(towerName)
        elif type == "set targeting":
            doSetTargeting(towerName)

        time.sleep(0.2)

    with open(f"maps/{mapName}-{strategyName}.txt", "w") as f:
        f.write("\n".join(fileLines))

    print("Saved map file")
    keyboardController.press(keyboard.Key.ctrl_l)
    time.sleep(0.2)
    keyboardController.press(keyboard.Key.backspace)
    time.sleep(0.2)
    keyboardController.release(keyboard.Key.backspace)
    keyboardController.release(keyboard.Key.ctrl_l)


lastMapName = None
seen = set()
for mapName, strategyName, *_ in allGameData:
    hash = (mapName, strategyName)
    if hash in seen:
        continue
    seen.add(hash)

    doMap(mapName, strategyName)
