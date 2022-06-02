import cvzone
import cv2
import numpy as np
import pygame

from cvzone.HandTrackingModule import HandDetector
import math
import random
import os


pygame.init()
pygame.font.init()
pygame.mixer.init()


s = 'Sound'

eatsound = pygame.mixer.Sound(os.path.join(s, 'eatsound.wav'))
explosion = pygame.mixer.Sound(os.path.join(s, 'explosion.mp3'))

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)

class SnakeGame:
    def __init__(self, Foodpath):

        self.points = []     # All the points of the snake
        self.Lengths = []     # Distance between each points of the snake
        self.CurrentLength = 0     # Total length of the snake
        self.AllowedLength = 150   # Total allowed length of the snake
        self.previousHead = 0, 0   # previous head point

        self.FoodImage = cv2.imread(Foodpath, cv2.IMREAD_UNCHANGED)
        self.Foodheight, self.Foodwidth, _ = self.FoodImage.shape
        self.randomfoodLocation()
        self.score = 0
        self.GameOver = False


    def randomfoodLocation(self):
        self.foodpoint = random.randint(100, 800), random.randint(100, 500)

    def update(self, Main_image, currentHead):


        if self.GameOver == False:

            previous_X, previous_Y = self.previousHead
            current_X, current_Y = currentHead

            self.points.append([current_X, current_Y])
            distance = math.hypot(current_X - previous_X, current_Y - previous_Y)
            print(f"disatance: {distance}")

            self.Lengths.append(distance)
            self.CurrentLength += distance
            self.previousHead = current_X, current_Y


            # Reduction of the snake lenght
            if self.CurrentLength > self.AllowedLength:
                for i, length in enumerate(self.Lengths):
                    self.CurrentLength -= length
                    self.Lengths.pop(i)
                    self.points.pop(i)
                    if self.CurrentLength < self.AllowedLength:
                        break

            # Check if snake ate the food
            random_X, random_Y = self.foodpoint
            if random_X-self.Foodwidth//2 < current_X < random_X+self.Foodwidth//2 and\
                    random_Y-self.Foodheight//2 < current_Y < random_Y+self.Foodheight//2:
                self.randomfoodLocation()
                self.AllowedLength += 50



                self.score += 1
                print(self.score)
                print("Khaliya")
                pygame.mixer.Sound.play(eatsound)


            # Draw a snake
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv2.line(Main_image, self.points[i - 1], self.points[i], (102, 204, 0), 20)
                    cv2.circle(Main_image, self.points[-1], 20, (128, 128, 0), cv2.FILLED)


            # Draw Food
            Main_image = cvzone.overlayPNG(Main_image, self.FoodImage,
                                        (random_X-self.Foodwidth//2, random_Y-self.Foodheight//2))
            print(f"width: {self.Foodwidth}, height: {self.Foodheight}, {random_X-self.Foodwidth//2}, {random_Y-self.Foodheight//2}")####
            cvzone.putTextRect(Main_image, f"Score : {self.score}", [50, 70],
                               scale=3, thickness=3, offset=10)

            # Cheking for collision of the snake body
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(Main_image, [pts], False, (128, 0, 0), 3)
            minimum_distance = cv2.pointPolygonTest(pts, (current_X, current_Y), True)
            print(minimum_distance)


            if minimum_distance > -1 and minimum_distance < 1:
                print('Collided')
                self.GameOver = True
                pygame.mixer.Sound.play(explosion)



        elif self.GameOver:
            cvzone.putTextRect(Main_image, "Game Over", [300, 400],
                               scale=7, thickness=5, offset=20)
            cvzone.putTextRect(Main_image, f"Your Score : {self.score}", [300, 550],
                               scale=7, thickness=5, offset=20)

            self.points = []  # All the points of the snake
            self.Lengths = []  # Distance between each points of the snake
            self.CurrentLength = 0  # Total length of the snake
            self.AllowedLength = 150  # Total allowed length of the snake
            self.previousHead = 0, 0  # previous head point
            self.randomfoodLocation()

        return Main_image


game = SnakeGame("Food.png")

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if hands:
        lmList = hands[0]['lmList']
        pointIndex = lmList[8][0:2]
        img = game.update(img, pointIndex)
        cv2.circle(img, pointIndex, 20, (76, 0, 153), cv2.FILLED)

    # img = cv2.resize(img, (1440, 920))
    cv2.imshow("Classic Snake Game", img)
    key = cv2.waitKey(1)
    if key == ord('r'):
        game.GameOver = False
        game.score = 0
