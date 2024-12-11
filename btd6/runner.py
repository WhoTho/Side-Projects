"""
Created Date: Jun 23 2024, 12:05:39 PM
Author: @WhoTho whotho06@gmail.com
-----
Last Modified: Jun 30 2024, 06:53:34 PM
Modified By: @WhoTho
-----
CHANGE LOG:
Date                        | Comments
----------------------------+---------------------------------------------
"""

# 158746 cash on medium

import pyautogui
import time
from keybinds import KEYBINDS
from random import random
import traceback
import os

pyautogui.FAILSAFE = True

# ---------------------------------------------------------------------------- #
#                                   MAP INFO                                   #
# ---------------------------------------------------------------------------- #

MAP_NAME = "candy falls"
STRATEGY_NAME = "militaryOnly"

STRATEGY_EXTRA = ""  # "" or "abr" or "apop"

# ---------------------------------------------------------------------------- #
#                                      END                                     #
# ---------------------------------------------------------------------------- #

UPDATE_INTERVAL = 1
MOUSE_MOVE_DURATION = 0.2

CENTER_OF_SCREEN = (2880, 540)
WINDOW_TOP_LEFT = (1920, 0)
WINDOW_BOTTOM_RIGHT = (3840, 1080)


towers = {}
instructions = []
screenshot = None


class Tower:
    def __init__(self, rawName):
        self.name = rawName
        self.position = None
        self.type = rawName.split(" ")[0]

        self.upgrades = [0, 0, 0]
        self.targetingPosition = None


class Instruction:
    DELIMITER = ", "

    def __init__(self, rawInstruction):
        self.rawInstruction = rawInstruction
        self.tower = None
        self.type = None
        self.upgrades = None
        self.abilityKeybind = None
        self.targeting = None
        self.extraInfo = None

        self.parse()

    def parse(self):
        type, *args = self.rawInstruction.split(Instruction.DELIMITER)

        if type == "place":
            self.type = "place"
            if args[0].split()[0] not in KEYBINDS:
                stopProgram(f"Invalid tower type: {args[0]}")

            self.tower = Tower(args[0])
            towers[args[0]] = self.tower
        elif type == "upgrade":
            self.type = "upgrade"
            if args[0] not in towers:
                stopProgram(f"Cannot upgrade tower as it doesn't exist: {args[0]}")

            self.tower = towers[args[0]]
            self.upgrades = list(map(int, args[1]))
            if len(self.upgrades) != 3:
                stopProgram(f"Invalid number of upgrades: {len(self.upgrades)}")
        elif type == "ability":
            self.type = "ability"
            self.abilityKeybind = args[0]
        elif type == "start":
            self.type = "start"
        elif type == "set targeting":
            self.type = "set targeting"
            if args[0] not in towers:
                stopProgram(f"Cannot set targeting as tower doesn't exist: {args[0]}")

            self.tower = towers[args[0]]
            self.targeting = args[1]
            if len(args) == 3:
                self.extraInfo = args[2]
        elif type == "sell":
            self.type = "sell"
            if args[0] not in towers:
                stopProgram(f"Cannot sell tower as it doesn't exist: {args[0]}")

            self.tower = towers[args[0]]
        else:
            stopProgram(f"Invalid instruction type: {type}")


lastMessage = ""
lastMessageCount = 0


def log(*args, spaceBefore=False):
    global lastMessage, lastMessageCount

    message = " ".join(map(str, args))
    if message == lastMessage:
        lastMessageCount += 1
        print(f"\033[A\033[K{message} [x{lastMessageCount}]")
    else:
        if spaceBefore:
            print()
        print(message)
        lastMessageCount = 0
        lastMessage = message


def clickAt(x, y):
    pyautogui.moveTo((x, y), duration=MOUSE_MOVE_DURATION)
    pyautogui.click()


def toWindow(x, y=None):
    if y is None:
        return (x[0] - WINDOW_TOP_LEFT[0], x[1] - WINDOW_TOP_LEFT[1])
    return (x - WINDOW_TOP_LEFT[0], y - WINDOW_TOP_LEFT[1])


def isMouseInBounds():
    mousePos = pyautogui.position()

    return (
        WINDOW_TOP_LEFT[0] < mousePos[0] < WINDOW_BOTTOM_RIGHT[0]
        and WINDOW_TOP_LEFT[1] < mousePos[1] < WINDOW_BOTTOM_RIGHT[1]
    )


def synchronizeWithUpdateInterval(previousSleeps=0):
    if previousSleeps > UPDATE_INTERVAL:
        return
    time.sleep(UPDATE_INTERVAL - previousSleeps + random() * 0.25)


def stopProgram(reason="Unknown"):
    log(f"Exiting program... Reason: {reason}")

    if instructionIndex < len(instructions):
        with open("lastInstruction.txt", "w") as f:
            line = str(instructionIndex)
            if instructions[instructionIndex].type == "upgrade":
                line += Instruction.DELIMITER + upgradesToString(
                    instructions[instructionIndex].tower.upgrades
                )
            f.write(line)
    else:
        log("Unable to save last instruction")

    raise Exception(reason)


def takeScreenshot(skipOverlayCheck=False, skipMouseCheck=False):
    global screenshot
    screenshot = pyautogui.screenshot(
        region=(
            WINDOW_TOP_LEFT[0],
            WINDOW_TOP_LEFT[1],
            WINDOW_BOTTOM_RIGHT[0] - WINDOW_TOP_LEFT[0],
            WINDOW_BOTTOM_RIGHT[1] - WINDOW_TOP_LEFT[1],
        )
    )

    if not skipOverlayCheck and isOverlayPresent():
        handleOverlay()

    if not skipMouseCheck and not isMouseInBounds():
        stopProgram("Mouse out of bounds")


def pixelColor(*args):
    return screenshot.getpixel(toWindow(*args))


def isOverlayPresent():
    # color from stuff
    return not (
        pixelColor(3659, 43) == (255, 255, 255)
        and pixelColor(3803, 66) == (192, 152, 95)
    )


def detectOverlayType():
    takeScreenshot(True, True)

    overlayData = {
        "pause": [
            [(2242, 459), (0, 199, 255)],
            [(2235, 521), (255, 255, 255)],
            [(2550, 853), (0, 180, 222)],
            [(3248, 873), (61, 214, 0)],
        ],
        "win": [
            [(2619, 179), (244, 83, 22)],
            [(2659, 161), (255, 246, 0)],
            [(2920, 903), (255, 255, 255)],
        ],
        "round100win": [
            [(2684, 665), (243, 77, 19)],
            [(2703, 666), (0, 0, 0)],
            [(2726, 664), (255, 217, 0)],
        ],
        "levelUp": [
            [(2745, 557), (243, 79, 19)],
            [(2768, 571), (32, 20, 15)],
            [(2777, 567), (255, 255, 255)],
        ],
        "defeat": [
            [(2562, 358), (100, 151, 216)],
            [(2655, 350), (81, 11, 0)],
            [(2676, 333), (255, 65, 0)],
        ],
    }

    for overlayType, data in overlayData.items():
        for coords, color in data:
            if pixelColor(coords) != color:
                break
        else:
            return overlayType

    return None


def handleOverlay():
    time.sleep(1)

    overlayType = detectOverlayType()
    if overlayType is None:
        stopProgram("Unknown overlay")

    if overlayType == "round100win":
        pyautogui.click()
        time.sleep(2)
        overlayType = "win"

    if overlayType == "levelUp":
        pyautogui.click()
        time.sleep(1)
        pyautogui.click()
    elif overlayType == "win":
        pyautogui.moveTo((2878, 919), duration=MOUSE_MOVE_DURATION)
        pyautogui.click()
        time.sleep(2)
        pyautogui.moveTo((2698, 858), duration=MOUSE_MOVE_DURATION)
        pyautogui.click()
        stopProgram("Game won")
    elif overlayType == "defeat":
        stopProgram("Game lost")
    elif overlayType == "pause":
        while True:
            takeScreenshot(True, True)
            if not isOverlayPresent():
                break
            log("Game paused")
            synchronizeWithUpdateInterval()
    else:
        stopProgram(f"Unhandled overlay: {overlayType}")

    time.sleep(1)
    takeScreenshot()


def getUpgradeWindowSide():
    # checks middle of the info button and the side of the info button
    if pixelColor(3210, 163) == (255, 255, 255) and pixelColor(3199, 157) == (
        0,
        216,
        255,
    ):
        return "right"

    if pixelColor(1988, 161) == (254, 254, 254) and pixelColor(1977, 156) == (
        0,
        217,
        255,
    ):
        return "left"

    return None


def isHoldingTower():
    # checks middle of x button and the side of x button
    return pixelColor(3519, 122) == (255, 255, 255) and pixelColor(3501, 115) == (
        254,
        109,
        0,
    )


def placeTower(instruction: Instruction):
    keybind = KEYBINDS[instruction.tower.type]
    pyautogui.press(keybind)

    mousePos = pyautogui.position()
    validTopLeft = (1978, 68)
    validBottomRight = (3535, 1058)

    if (
        not validTopLeft[0] < mousePos[0] < validBottomRight[0]
        or not validTopLeft[1] < mousePos[1] < validBottomRight[1]
    ):
        pyautogui.moveTo(CENTER_OF_SCREEN, duration=MOUSE_MOVE_DURATION)

    time.sleep(0.3)  # animation completed in 0.025 seconds
    takeScreenshot()
    if not isHoldingTower():
        return False

    pyautogui.moveTo(instruction.tower.position, duration=MOUSE_MOVE_DURATION)
    pyautogui.click()

    return True


def upgradesToString(upgrades):
    return "".join(map(str, upgrades))


def closeUpgradeWindowIfNotNeeded():
    if (
        instructionIndex + 1 < len(instructions)
        and instructions[instructionIndex].tower
        == instructions[instructionIndex + 1].tower
        and (
            instructions[instructionIndex + 1].type
            in ["upgrade", "set targeting", "sell"]
        )
    ):
        return False

    time.sleep(0.3)
    pyautogui.press(KEYBINDS["escape"])
    return True


def openTower(tower):
    windowSide = getUpgradeWindowSide()
    if windowSide:
        return windowSide

    pyautogui.moveTo(tower.position, duration=MOUSE_MOVE_DURATION)
    pyautogui.click()

    time.sleep(0.3)  # animation completed in 0.01 seconds
    takeScreenshot()

    return getUpgradeWindowSide()


def upgradeTower(instruction: Instruction):
    tower, upgrades = instruction.tower, instruction.upgrades

    upgradeCoords = {
        "left": [(2176, 485), (2176, 634), (2177, 784)],
        "right": [(3397, 485), (3397, 634), (3398, 784)],
    }

    if not openTower(tower):
        return False

    log(
        f"Upgrading: {tower.name} ({upgradesToString(tower.upgrades)} -> {upgradesToString(upgrades)})"
    )

    noUpgradesCount = 0

    while tower.upgrades != upgrades:
        synchronizeWithUpdateInterval()
        takeScreenshot()
        windowSide = getUpgradeWindowSide()
        if not windowSide:
            return False

        for i, upgrade in enumerate(upgrades):
            if tower.upgrades[i] == upgrade:
                continue
            if tower.upgrades[i] > upgrade:
                stopProgram(
                    f"Cannot downgrade tower: {tower.name} ({tower.upgrades[i]} -> {upgrade})"
                )
            if pixelColor(upgradeCoords[windowSide][i]) != (84, 222, 0):
                continue

            pyautogui.press(KEYBINDS[f"upgrade {i + 1}"])

            oldUpgrades = upgradesToString(tower.upgrades)
            tower.upgrades[i] += 1
            log(
                f"Upgraded {tower.name} from {oldUpgrades} to {upgradesToString(tower.upgrades)}"
            )

            noUpgradesCount = 0
            break
        else:
            noUpgradesCount += 1
            if noUpgradesCount > 1:
                log(f"\033[A\033[KNo upgrades available... [x{noUpgradesCount}]")
            else:
                log("No upgrades available...")

    closeUpgradeWindowIfNotNeeded()
    return True


def useAbility(instruction: Instruction):
    pyautogui.press(instruction.abilityKeybind)
    return True


def startRound(instruction: Instruction):
    pyautogui.press(KEYBINDS["start"])

    if instruction.extraInfo == "apop":
        return True

    time.sleep(0.3)
    pyautogui.press(KEYBINDS["start"])
    return True


def setTargeting(instruction: Instruction):
    windowSide = openTower(instruction.tower)
    if not windowSide:
        return False

    if instruction.targeting == "strong":
        pyautogui.shortcut(KEYBINDS["reverse targeting"].split("+"))
    elif instruction.targeting == "last":
        pyautogui.shortcut(KEYBINDS["cycle targeting"])
    elif instruction.targeting == "close":
        pyautogui.shortcut(KEYBINDS["cycle targeting"])
        time.sleep(0.3)
        pyautogui.shortcut(KEYBINDS["cycle targeting"])
    elif instruction.targeting == "tab amount":
        amount = int(instruction.extraInfo)
        if amount < 0:
            keybind = KEYBINDS["reverse targeting"].split("+")
            amount = -amount
        else:
            keybind = KEYBINDS["cycle targeting"].split("+")

        for _ in range(amount):
            pyautogui.shortcut(keybind)
            time.sleep(0.3)
    elif instruction.targeting == "custom":
        setCustomTargeting(instruction, windowSide)

    closeUpgradeWindowIfNotNeeded()
    return True


def setCustomTargeting(instruction: Instruction, windowSide):
    # main, 1, 2

    coords = {
        "left": [(2144, 373), (2296, 305), (2296, 221)],
        "right": [(3367, 371), (3521, 303), (3519, 225)],
    }

    index = int(instruction.extraInfo) if instruction.extraInfo != "main" else 0

    pyautogui.moveTo(coords[windowSide][index], duration=MOUSE_MOVE_DURATION)

    # have to do this because the game does weird thing
    pyautogui.mouseDown()
    time.sleep(0.1)
    pyautogui.mouseUp()

    time.sleep(0.3)

    pyautogui.moveTo(instruction.tower.targetingPosition, duration=MOUSE_MOVE_DURATION)
    pyautogui.click()

    return True


def sellTower(tower):
    if not openTower(tower):
        return False

    pyautogui.press(KEYBINDS["sell"])

    return True


def getStrategyFilePath(strategyName, strategyExtra):
    extraFileInfo = " (" + strategyExtra + ")" if strategyExtra else ""
    return f"strategies/{strategyName}{extraFileInfo}.txt"


def getMapFilePath(mapName, strategyName):
    return f"maps/{mapName}-{strategyName}.txt"


def loadAllData(mapName, strategyName, strategyExtra, mode):
    with open(getStrategyFilePath(strategyName, strategyExtra), "r") as file:
        for line in file.readlines():
            if line.strip() == "":
                continue

            if line.startswith("#"):
                continue

            instructions.append(Instruction(line.strip()))

    with open(getMapFilePath(mapName, strategyName), "r") as file:
        for line in file.readlines():
            type, name, x, y = line.strip().split(Instruction.DELIMITER)
            if name not in towers:
                log("WARNING: Tower doesn't exist in strategy:", name)
            elif type == "placement":
                towers[name].position = (int(x), int(y))
            elif type == "set targeting":
                towers[name].targetingPosition = (int(x), int(y))

    for tower in towers.values():
        if not tower.position:
            stopProgram(f"Missing tower position: {tower.name}")

    if mode == "apop":
        startInstruction = None
        for instruction in instructions:
            if instruction.type == "start":
                startInstruction = instruction
                break
        if not startInstruction:
            stopProgram("Missing start instruction for apop mode")

        startInstruction.extraInfo = "apop"

    log("Loaded all data")


instructionIndex = 0


def gameLoop():
    global instructionIndex

    instruction = instructions[instructionIndex]

    takeScreenshot()

    log(f"Running instruction: {instructionIndex}", spaceBefore=True)

    if instruction.type == "place":
        if placeTower(instruction):
            instructionIndex += 1
    elif instruction.type == "upgrade":
        if upgradeTower(instruction):
            instructionIndex += 1
    elif instruction.type == "ability":
        if useAbility(instruction):
            instructionIndex += 1
    elif instruction.type == "start":
        if startRound(instruction):
            instructionIndex += 1
    elif instruction.type == "set targeting":
        if setTargeting(instruction):
            instructionIndex += 1
    elif instruction.type == "sell":
        if sellTower(instruction.tower):
            instructionIndex += 1
    else:
        stopProgram(f"Unknown instruction type: {instruction.type}")

    synchronizeWithUpdateInterval()


def waitForGameEnd():
    for i in range(10 * 60 // 3):
        log("Waiting for game to end...", spaceBefore=True)

        takeScreenshot()

        time.sleep(3)

    stopProgram("Game didn't end")


def autoCompleteUpgradeInstructions(uptoIndex):
    for i in range(uptoIndex):
        instruction = instructions[i]
        if instruction.type == "upgrade":
            instruction.tower.upgrades = instruction.upgrades

    log("Auto completed upgrade instructions")


def getLastInstruction():
    global instructionIndex

    with open("lastInstruction.txt", "r") as f:
        line = f.readline().strip()
        if line == "":
            instructionIndex = 0
            return

        lastInstructionIndex = int(line.split(Instruction.DELIMITER)[0])
        if lastInstructionIndex >= len(instructions):
            stopProgram("Last instruction index out of bounds")

        instructionIndex = lastInstructionIndex
        autoCompleteUpgradeInstructions(instructionIndex)
        if instructions[instructionIndex].type == "upgrade":
            currentUpgrades = list(map(int, line.split(Instruction.DELIMITER)[1]))
            instructions[instructionIndex].tower.upgrades = currentUpgrades

        log(f"Loaded last instruction: {instructionIndex}")


# ---------------------------------------------------------------------------- #
#                              MAIN GAME HANDLERS                              #
# ---------------------------------------------------------------------------- #


def resetGame():
    global instructionIndex, towers, screenshot, instructions
    instructionIndex = 0
    towers = {}
    instructions = []
    screenshot = None


def playNewGame(mapName, strategyName, strategyExtra, mode):
    resetGame()
    loadAllData(mapName, strategyName, strategyExtra, mode)

    log("Loaded new game")

    try:
        while instructionIndex < len(instructions):
            gameLoop()

        waitForGameEnd()
    except Exception as e:
        if str(e) != "Game won":
            print("Exception occurred:", e)
            traceback.print_exc()
            exit()

    return True


def isMainScreen():
    if (
        pixelColor(1996, 214) == (0, 235, 242)
        and pixelColor(3481, 965) == (161, 102, 214)
        and pixelColor(2757, 936) == (255, 255, 255)
        and pixelColor(2254, 938) == (255, 255, 255)
    ):
        return True

    return False


def isMapSelectionScreen():
    if (
        pixelColor(2008, 170) == (255, 255, 255)
        and pixelColor(1975, 141) == (0, 219, 255)
        and pixelColor(2500, 967) == (255, 200, 0)
        and pixelColor(3281, 957) == (255, 44, 0)
    ):
        return True

    return False


def selectMap(mapName):
    takeScreenshot(True, False)
    if not isMainScreen():
        stopProgram("Not on main screen")

    clickAt(2742, 924)
    time.sleep(1)

    takeScreenshot(True, False)
    if not isMapSelectionScreen():
        stopProgram("Not on map screen")

    clickAt(1998, 165)
    time.sleep(0.3)

    clickAt(2807, 46)
    time.sleep(0.3)

    pyautogui.write(mapName, interval=0.1)

    time.sleep(0.3)
    clickAt(2453, 338)

    return True


def isDifficultyScreen():
    if (
        pixelColor(2560, 373) == (173, 92, 36)
        and pixelColor(2836, 353) == (255, 255, 255)
        and pixelColor(3206, 442) == (42, 45, 54)
        and pixelColor(1975, 79) == (0, 198, 255)
    ):
        return True

    return False


def startDifficulty(mode):
    takeScreenshot(True, False)
    if not isDifficultyScreen():
        stopProgram("Not on difficulty screen")

    if mode in ["easy", "primaryOnly", "deflation"]:
        difficulty = "easy"
    elif mode in ["medium", "militaryOnly", "apop", "reverse"]:
        difficulty = "medium"
    elif mode in [
        "hard",
        "magicOnly",
        "doubleHpMoabs",
        "halfCash",
        "abr",
        "impoppable",
        "chimps",
    ]:
        difficulty = "hard"
    else:
        stopProgram("Invalid mode: " + mode)

    difficultyCoords = {"easy": (2556, 387), "medium": (2881, 411), "hard": (3216, 411)}
    modeCoords = {
        "easy": (2558, 592),
        "primaryOnly": (2879, 454),
        "deflation": (3202, 455),
        "medium": (2558, 592),
        "militaryOnly": (2879, 454),
        "apop": (3202, 455),
        "reverse": (2880, 743),
        "hard": (2558, 592),
        "magicOnly": (2879, 454),
        "doubleHpMoabs": (3202, 455),
        "halfCash": (3522, 456),
        "abr": (2880, 743),
        "impoppable": (3201, 748),
        "chimps": (3525, 746),
    }

    pyautogui.moveTo(difficultyCoords[difficulty], duration=MOUSE_MOVE_DURATION)
    pyautogui.click()

    time.sleep(1)

    pyautogui.moveTo(modeCoords[mode], duration=MOUSE_MOVE_DURATION)
    pyautogui.click()

    if mode in ["deflation", "impoppable", "chimps", "halfCash"]:
        for i in range(10):
            time.sleep(1)
            takeScreenshot(True, False)
            if pixelColor(2876, 759) == (255, 255, 255) and pixelColor(2923, 775) == (
                67,
                216,
                0,
            ):
                break
        else:
            stopProgram("Failed to find 'ok' button for mode " + mode)

        pyautogui.moveTo((2875, 760), duration=MOUSE_MOVE_DURATION)
        pyautogui.click()
    elif mode == "apop":
        for i in range(10):
            time.sleep(1)
            takeScreenshot(True, False)
            if pixelColor(2878, 755) == (255, 255, 255) and pixelColor(2917, 718) == (
                113,
                232,
                0,
            ):
                break
        else:
            stopProgram("Failed to find 'start' button for mode " + mode)

        pyautogui.moveTo((2880, 758), duration=MOUSE_MOVE_DURATION)
        pyautogui.click()

    waitForMapToLoad()

    return True


def waitForMapToLoad():
    for i in range(10):
        time.sleep(1)
        takeScreenshot(True, False)
        if not isOverlayPresent():
            break
    else:
        stopProgram("Map failed to load in 10 seconds")

    return True


def isCollectionEventScreen():
    return (
        pixelColor(2547, 49) == (0, 129, 156)
        and pixelColor(2676, 64) == (255, 255, 255)
        and pixelColor(2255, 655) == (240, 44, 141)
        and pixelColor(2966, 691) == (76, 219, 0)
        and pixelColor(3622, 46) == (224, 41, 0)
    )


def startNewGame(mapName, strategyName, strategyExtra, mode):
    log(f'Playing "{mapName}" on {mode} mode with "{strategyName}" strategy')

    selectMap(mapName)
    time.sleep(1)
    startDifficulty(mode)

    playNewGame(mapName, strategyName, strategyExtra, mode)

    log(f'Beat "{mapName}" on {mode} mode with "{strategyName}" strategy')


def calculateEta(gameData):
    modeTimes = {
        "easy": 4 * 60 + 46,
        "primaryOnly": 4 * 60 + 46,
        "deflation": 4 * 60 + 46,
        "medium": 7 * 60 + 53,
        "militaryOnly": 7 * 60 + 53,
        "apop": 7 * 60 + 26,
        "reverse": 7 * 60 + 53,
        "hard": 11 * 60 + 50,
        "magicOnly": 11 * 60 + 50,
        "doubleHpMoabs": 12 * 60,
        "halfCash": 11 * 60 + 50,
        "abr": 11 * 60 + 50,
        "impoppable": 14 * 60 + 23,
        "chimps": 15 * 60 + 45,
    }

    totalTime = 0
    for _, _, _, mode in gameData:
        totalTime += modeTimes[mode]
        totalTime += 20

    return totalTime


def handleGameData(gameData):
    for mapName, strategyName, strategyExtra, _ in gameData:
        if not os.path.exists(getStrategyFilePath(strategyName, strategyExtra)):
            strategyExtraString = f" ({strategyExtra})" if strategyExtra else ""
            stopProgram(
                f"Strategy file doesn't exist: {strategyName}{strategyExtraString}"
            )
        elif not os.path.exists(getMapFilePath(mapName, strategyName)):
            stopProgram(f"Map file doesn't exist: {mapName} - {strategyName}")

    eta = calculateEta(gameData)
    log(
        f"Estimated time: {eta // 60 // 60} hours {eta // 60 % 60} minutes {eta % 60} seconds"
    )
    currentTime = time.time()
    endTime = currentTime + eta
    log(f"Ending at {time.strftime('%I:%M:%S %p', time.localtime(endTime))}")

    print("Starting in 5 seconds...")

    for i, (mapName, strategyName, strategyExtra, mode) in enumerate(gameData):
        time.sleep(5)
        takeScreenshot(True)
        if isCollectionEventScreen():
            handleCollectionEvent()
            time.sleep(5)
        log(f"Starting game {i + 1}/{len(gameData)}")
        startNewGame(mapName, strategyName, strategyExtra, mode)
        log(f"Finished game {i + 1}/{len(gameData)}")


def handleCollectionEvent():
    print("Handling collection event...")

    clickAt(2882, 680)

    time.sleep(2)

    clickAt(2719, 540)
    time.sleep(1)
    pyautogui.click()

    time.sleep(1)
    clickAt(3033, 542)
    time.sleep(1)
    pyautogui.click()

    clickAt(2882, 1000)
    time.sleep(1)

    if not isCollectionEventScreen():
        stopProgram(
            "Failed to get back to collection event screen after collecting rewards"
        )

    clickAt(1992, 62)

    return True


DEFAULT_EXCLUDED_MODES = ["apop"]


def makeNormalGameData(mapName, excludeModes=[], onlyModes=[]):
    excludeModes.extend(DEFAULT_EXCLUDED_MODES)

    normalData = [
        ["primaryOnly", "", "easy"],
        ["primaryOnly", "", "primaryOnly"],
        ["deflation", "", "deflation"],
        ["militaryOnly", "", "medium"],
        ["militaryOnly", "", "militaryOnly"],
        ["militaryOnly", "", "apop"],
        ["reverse", "", "reverse"],
        ["druid", "", "hard"],
        ["magicOnly", "", "magicOnly"],
        ["druid", "", "doubleHpMoabs"],
        ["halfCash", "", "halfCash"],
        ["druid", "abr", "abr"],
        ["druid", "", "impoppable"],
        ["druid", "", "chimps"],
    ]

    data = []
    for strategyName, strategyExtra, mode in normalData:
        if onlyModes and mode not in onlyModes:
            continue
        if mode in excludeModes:
            continue
        data.append([mapName, strategyName, strategyExtra, mode])

    return data


# game mode unlock paths
# easy -> primaryOnly -> deflation
# medium -> militaryOnly -> apop
# medium -> reverse
# hard -> magicOnly -> doubleHpMoabs -> halfCash
# hard -> abr -> impoppable -> chimps

# map name, strategy name, strategy extra, mode
allGameData = []

allGameData.extend(
    makeNormalGameData(
        "logs",
        [],
        [
            "impoppable",
            "chimps",
        ],
    )
)


# def main():
#     loadAllData(MAP_NAME, STRATEGY_NAME, STRATEGY_EXTRA)
#     if input("Start a new game? (y/n): ").lower() != "y":
#         getLastInstruction()

#     log("Starting in 3 seconds...")
#     time.sleep(3)

#     while instructionIndex < len(instructions):
#         gameLoop()

#     log("Finished all instructions")


if __name__ == "__main__":
    handleGameData(allGameData)
