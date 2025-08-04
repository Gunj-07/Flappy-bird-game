import pygame as pg
import sys, time
import os
from bird import Bird
from pipe import Pipe


pg.init()

class Game:
    def __init__(self):
        self.width = 568
        self.height = 768
        self.scale_factor = 1.5
        self.win = pg.display.set_mode((self.width, self.height))
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("Arial", 36)
        self.high_score = self.loadHighScore()
        self.new_high_score = False

        self.resetGame()

        self.gameLoop()

    def handleButtons(self, restart_button, exit_button):
        mouse_pos = pg.mouse.get_pos()
        mouse_click = pg.mouse.get_pressed()

        if restart_button.collidepoint(mouse_pos) and mouse_click[0]:
            pg.time.delay(200)  # to prevent multiple clicks
            self.resetGame()

        if exit_button.collidepoint(mouse_pos) and mouse_click[0]:
            pg.quit()
            sys.exit()


    def loadHighScore(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as file:
                try:
                    return int(file.read())
                except ValueError:
                    return 0
        return 0

    def saveHighScore(self):
        with open("highscore.txt", "w") as file:
            file.write(str(self.high_score))

    
    def resetGame(self):
        self.move_speed = 250
        self.bird = Bird(self.scale_factor)
        self.is_enter_pressed = False
        self.pipes = []
        self.pipe_generate_counter = 71
        self.score = 0
        self.passed_pipe = False
        self.game_over = False
        self.setUpBgAndGround()
        self.new_high_score = False

    def gameLoop(self):
        last_time = time.time()
        while True:
            dt = time.time() - last_time
            last_time = time.time()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN and not self.game_over:
                        self.is_enter_pressed = True
                        self.bird.update_on = True

                    if event.key == pg.K_SPACE and self.is_enter_pressed:
                        self.bird.flap(dt)

                    if event.key == pg.K_r and self.game_over:
                        self.resetGame()

            if not self.game_over:
                self.updateEverything(dt)
                self.checkCollisions()
                self.checkScore()

            self.drawEverything()
            pg.display.update()
            self.clock.tick(60)

    def checkCollisions(self):
        if len(self.pipes):
            if self.bird.rect.bottom > 568:
                self.triggerGameOver()
            if (self.bird.rect.colliderect(self.pipes[0].rect_down) or
                    self.bird.rect.colliderect(self.pipes[0].rect_up)):
                self.triggerGameOver()

    def checkScore(self):
        for pipe in self.pipes:
            if not pipe.scored and pipe.rect_up.right < self.bird.rect.left:
                self.score += 1
                pipe.scored = True  # Mark this pipe as scored

    def triggerGameOver(self):
        self.bird.update_on = False
        self.is_enter_pressed = False
        self.game_over = True

        if self.score > self.high_score:
            self.high_score = self.score
            self.new_high_score = True
            self.saveHighScore()

    def updateEverything(self, dt):
        if self.is_enter_pressed:
            self.ground1_rect.x -= int(self.move_speed * dt)
            self.ground2_rect.x -= int(self.move_speed * dt)

            if self.ground1_rect.right < 0:
                self.ground1_rect.x = self.ground2_rect.right
            if self.ground2_rect.right < 0:
                self.ground2_rect.x = self.ground1_rect.right

            if self.pipe_generate_counter > 70:
                self.pipes.append(Pipe(self.scale_factor, self.move_speed))
                self.pipe_generate_counter = 0

            self.pipe_generate_counter += 1

            for pipe in self.pipes:
                pipe.update(dt)

            if self.pipes and self.pipes[0].rect_up.right < 0:
                self.pipes.pop(0)

        self.bird.update(dt)

    def drawEverything(self):
        self.win.blit(self.bg_img, (0, -300))
        for pipe in self.pipes:
            pipe.drawPipe(self.win)
        self.win.blit(self.ground1_img, self.ground1_rect)
        self.win.blit(self.ground2_img, self.ground2_rect)
        self.win.blit(self.bird.image, self.bird.rect)

        if self.game_over == False:
            score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
            self.win.blit(score_text, (10, 25))
            
            score_text = self.font.render(f"HIGH SCORE: {self.high_score}", True, (255, 0, 0))
            self.win.blit(score_text, (180, 25))

        if self.game_over:
            # Game Over title
            over_text = self.font.render("GAME OVER!", True, (255, 0, 0))
            self.win.blit(over_text, (self.width // 2 - over_text.get_width() // 2, 120))

            # Final Score
            if self.new_high_score == False:
                score_text = self.font.render(f"YOUR SCORE: {self.score}", True, (255, 255, 255))
                self.win.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 180))

            # High Score
            if self.new_high_score == False:
                high_score_text = self.font.render(f"HIGH SCORE: {self.high_score}", True, (255, 215, 0))
                self.win.blit(high_score_text, (self.width // 2 - high_score_text.get_width() // 2, 230))
            if self.new_high_score:
                congrats_font = pg.font.SysFont("Arial", 36, bold=True)
                congrats_text = congrats_font.render(" CONGRATULATIONS !!! ", True, (255, 215, 0))
                self.win.blit(congrats_text, (self.width // 2 - congrats_text.get_width() // 2, 180))
               
                n_highscore_font = pg.font.SysFont("Arial", 36, bold=True)
                n_highscore_text = n_highscore_font.render(f"NEW HIGH SCORE: {self.high_score}", True, (0, 0, 0))
                self.win.blit(n_highscore_text, (self.width // 2 - n_highscore_text.get_width() // 2, 230))

            # Buttons
            button_font = pg.font.SysFont("Arial", 28)
            restart_button = pg.Rect(self.width // 2 - 100, 280, 200, 50)
            exit_button = pg.Rect(self.width // 2 - 100, 350, 200, 50)

            pg.draw.rect(self.win, (0, 200, 0), restart_button)   # Green Restart
            pg.draw.rect(self.win, (200, 0, 0), exit_button)      # Red Exit

            restart_text = button_font.render("RESTART", True, (255, 255, 255))
            exit_text = button_font.render("EXIT", True, (255, 255, 255))

            self.win.blit(restart_text, (restart_button.x + 55, restart_button.y + 10))
            self.win.blit(exit_text, (exit_button.x + 70, exit_button.y + 10))

            self.handleButtons(restart_button, exit_button)

    def setUpBgAndGround(self):
        self.bg_img = pg.transform.scale_by(pg.image.load("assets/bg.png").convert(), self.scale_factor)
        self.ground1_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(), self.scale_factor)
        self.ground2_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(), self.scale_factor)

        self.ground1_rect = self.ground1_img.get_rect()
        self.ground2_rect = self.ground2_img.get_rect()

        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.ground1_rect.y = 568
        self.ground2_rect.y = 568

game = Game()