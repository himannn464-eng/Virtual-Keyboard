import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import cvzone
from pynput.keyboard import Controller
import time

cap = cv2.VideoCapture(0)
cap.set(3, 1280)  
cap.set(4, 720)   

detector = HandDetector(detectionCon=0.8, maxHands=1)

keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        ["SPACE", "BACKSPACE", "CLEAR"]] 

finalText = ""
keyboard = Controller()

isClicked = False
clickStartTime = 0
cooldownTime = 0.5 
KEY_COLOR = (102, 204, 204)         
KEY_HOVER_COLOR = (41, 128, 185)    
KEY_CLICK_COLOR = (52, 152, 219)    
TEXT_COLOR = (255, 255, 255)        
TEXT_FIELD_COLOR = (44, 62, 80, 150)  
BORDER_COLOR = (189, 195, 199)     

class Button():
    def __init__(self, pos, text, size=None):
        self.pos = pos
        self.text = text
        
        if text in ["SPACE", "BACKSPACE", "CLEAR"]:
            if text == "SPACE":
                self.size = [300, 85]
            else:
                self.size = [200, 85]
        else:
            self.size = [85, 85] if size is None else size
            
        self.clicked = False
        self.clickTime = 0

def drawAll(img, buttonList):
    original_img = img.copy()
    keyboard_overlay = np.zeros_like(img)
    cv2.rectangle(keyboard_overlay, (30, 30), (1250, 450), (44, 62, 80), cv2.FILLED)
    img = cv2.addWeighted(keyboard_overlay, 0.3, img, 1.0, 0)
    cv2.rectangle(img, (30, 30), (1250, 450), BORDER_COLOR, 2)
    
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        key_overlay = img.copy()
        cv2.rectangle(key_overlay, (x, y), (x + w, y + h), KEY_COLOR, cv2.FILLED)
        img = cv2.addWeighted(key_overlay, 0.7, img, 0.3, 0)
        cv2.rectangle(img, (x, y), (x + w, y + h), BORDER_COLOR, 1)
        cvzone.cornerRect(img, (x, y, w, h), 20, rt=0, colorC=BORDER_COLOR)
        
        if button.text in ["SPACE", "BACKSPACE", "CLEAR"]:
            font_scale = 2
            text_x = x + 20
        else:
            font_scale = 4
            text_x = x + 20
            
        cv2.putText(img, button.text, (text_x, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, font_scale, TEXT_COLOR, 2)
    
    return img

buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == "SPACE":
            pos_x = 390
            pos_y = 100 * i + 50
        elif key == "BACKSPACE":
            pos_x = 700
            pos_y = 100 * i + 50
        elif key == "CLEAR":
            pos_x = 910
            pos_y = 100 * i + 50
        else:
            pos_x = 100 * j + 50
            pos_y = 100 * i + 50
        
        buttonList.append(Button([pos_x, pos_y], key))

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    img = drawAll(img, buttonList)
    
    if hands:
        lmList = hands[0]['lmList']
        
        for button in buttonList:
            x, y = button.pos
            w, h = button.size
            
            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                hover_overlay = img.copy()
                cv2.rectangle(hover_overlay, (x, y), (x + w, y + h), KEY_HOVER_COLOR, cv2.FILLED)
                img = cv2.addWeighted(hover_overlay, 0.7, img, 0.3, 0)
                cvzone.cornerRect(img, (x, y, w, h), 20, rt=0, colorC=BORDER_COLOR)
                
                if button.text in ["SPACE", "BACKSPACE", "CLEAR"]:
                    font_scale = 2
                    text_x = x + 20
                else:
                    font_scale = 4
                    text_x = x + 20
                    
                cv2.putText(img, button.text, (text_x, y + 65),
                            cv2.FONT_HERSHEY_PLAIN, font_scale, TEXT_COLOR, 2)
                
                x1, y1 = lmList[8][0], lmList[8][1]
                x2, y2 = lmList[12][0], lmList[12][1]
                l, _, _ = detector.findDistance((x1, y1), (x2, y2))
                
                current_time = time.time()
                if l < 40 and not isClicked and (current_time - clickStartTime) > cooldownTime:
                    click_overlay = img.copy()
                    cv2.rectangle(click_overlay, (x, y), (x + w, y + h), KEY_CLICK_COLOR, cv2.FILLED)
                    img = cv2.addWeighted(click_overlay, 0.9, img, 0.1, 0)
                    
                    if button.text == "SPACE":
                        finalText += " "
                        keyboard.press(" ")
                        keyboard.release(" ")
                    elif button.text == "BACKSPACE":
                        if finalText:
                            finalText = finalText[:-1]
                            keyboard.press('\b')
                            keyboard.release('\b')
                    elif button.text == "CLEAR":
                        finalText = ""
                    else:
                        finalText += button.text
                        keyboard.press(button.text)
                        keyboard.release(button.text)
                    
                    isClicked = True
                    clickStartTime = current_time
                    button.clicked = True
                    button.clickTime = current_time
                    
                elif l > 40:
                    isClicked = False
    
    text_field_overlay = img.copy()
    cv2.rectangle(text_field_overlay, (50, 500), (1230, 620), TEXT_FIELD_COLOR, cv2.FILLED)
    img = cv2.addWeighted(text_field_overlay, 0.7, img, 0.3, 0)
    cv2.rectangle(img, (50, 500), (1230, 620), BORDER_COLOR, 2)
    
    if len(finalText) > 40:
        displayed_text = finalText[-40:]
    else:
        displayed_text = finalText
        
    cv2.putText(img, displayed_text, (60, 580),
                cv2.FONT_HERSHEY_PLAIN, 5, TEXT_COLOR, 5)
    
    instructions_overlay = img.copy()
    cv2.rectangle(instructions_overlay, (30, 10), (350, 30), (44, 62, 80), cv2.FILLED)
    cv2.rectangle(instructions_overlay, (1000, 10), (1250, 30), (44, 62, 80), cv2.FILLED)
    img = cv2.addWeighted(instructions_overlay, 0.5, img, 0.5, 0)
    
    cv2.putText(img, "Virtual Keyboard", (50, 25),
                cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
    cv2.putText(img, "Pinch to type", (1050, 25),
                cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 1)
    
    cTime = time.time()
    fps = 1 / (cTime - clickStartTime + 0.01)
    fps_overlay = img.copy()
    cv2.rectangle(fps_overlay, (1140, 680), (1230, 710), (44, 62, 80), cv2.FILLED)
    img = cv2.addWeighted(fps_overlay, 0.5, img, 0.5, 0)
    cv2.putText(img, f'FPS: {int(fps)}', (1150, 700), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    
    cv2.imshow("Virtual Keyboard", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()