
import keyboard

from detection import Detection
from bot import Bot


print("Running...")

detector = Detection()
bot = Bot()

detector.start()
bot.start()

while not keyboard.is_pressed("p"):
    GameState = detector.GameState
    click_xy = detector.click_xy
    bot.update_info(GameState, click_xy)

else:
    detector.stop()
    bot.stop()

print("Done.")
        
