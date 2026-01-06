# ts was vibe coded with the aid of chatgpt in like a day and it pmo

# imports
import sys, platform
import asyncio
import pygame
from pygame.locals import *
import random
from itertools import combinations

# innits
pygame.init()
pygame.mixer.init()
if sys.platform == "emscripten":
    platform.window.canvas.style.imageRendering = "pixelated"

# global vars
fps = 60
fpsClock = pygame.time.Clock()
scale = 4
width, height = 160*scale, 144*scale
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("let's go gambling!!1!")
clock = pygame.time.Clock()

# cards
font = pygame.font.SysFont("FreeSans", 4*scale)
card_w, card_h = 10*scale, 14*scale
deck_pos = (width//2 - card_w//2, height//2 - card_h//2)
board_y = height//2 - card_h*2
rank_values = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "T": 10,
    "J": 11, "Q": 12, "K": 13, "A": 14
}
payouts = {
    11: 10.24, # royal flush
    10: 51.2, # straight flush
    9: 25.6, # quads
    8: 12.8, # full house
    7: 6.4, # flush
    6: 3.2, # straight
    5: 1.6, # three of a kind
    4: 0.8, # two pairs
    3: 0.4, # face card pair or aces
    2: 0.2, # pair below face cards
    1: 0.1, # ace high
    0: 0.0 # high card below ace
}

# class
class card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.rect = pygame.Rect(*deck_pos, card_w, card_h)
        # animation
        self.start_pos = pygame.Vector2(self.rect.topleft)
        self.target_pos = pygame.Vector2(self.rect.topleft)
        self.progress = 1.0
        self.speed = 0.03*scale
        # $
        self.highlight = False

    def draw(self, surface):
        if self.suit == "♠":
            colour = "#000000"
        if self.suit == "♥":
            colour = "#B01919"
        if self.suit == "♦":
            colour = "#348DE9"
        if self.suit == "♣":
            colour = "#379639"
        pygame.draw.rect(surface, colour, self.rect)
        pygame.draw.rect(surface, "#FFFFFF", self.rect, scale)
        text = font.render(f"{self.rank}{self.suit}", True, "#FFFFFF")
        surface.blit(text, (self.rect.x + 2*scale, self.rect.y + 2*scale))
        if self.highlight:
            pygame.draw.rect(surface, "#FFD700", self.rect.inflate(scale, scale), scale)

    def move_to(self, pos):
        self.start_pos = pygame.Vector2(self.rect.topleft)
        self.target_pos = pygame.Vector2(pos)
        self.progress = 0.0

    def update(self):
        if self.progress < 1.0:
            self.progress += self.speed
            if self.progress > 1.0:
                self.progress = 1.0
            pos = self.start_pos.lerp(self.target_pos, self.progress)
            self.rect.topleft = pos

# waiter i would love some more popups please
class PayoutPopup:
    def __init__(self, amount, pos):
        self.amount = amount
        self.pos = pygame.Vector2(pos)

    def draw(self, surface):
        pygame.draw.rect(screen, "#000000", (self.pos.x-scale, self.pos.y-scale, 14*scale, 7*scale))
        pygame.draw.rect(surface, "#FFD700", (self.pos.x-scale, self.pos.y-scale, 14*scale, 7*scale), scale)
        text = font.render(f"x{self.amount}x", True, "#FFD700")
        surface.blit(text, self.pos)

# doesn't even look like crt aesthetic
def generate_static(boolean):
    static = []
    r_values = [int(i * 255 / 7) for i in range(8)]
    g_values = [int(i * 255 / 7) for i in range(8)]
    b_values = [int(i * 255 / 3) for i in range(4)]
    for r in r_values:
        for g in g_values:
            for b in b_values:
                if boolean:
                    static.append((min(r*scale*2, 255), min(g*scale*2, 255), min(b*scale*2, 255)))
                else:
                    static.append((r//scale//2, g//scale//2, b//scale//2))
    return static

# func
def get_new_deck():
    suits = ["♠", "♥", "♦", "♣"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    return [card(rank, suit) for suit in suits for rank in ranks]

# rigged
def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

# thanks cs116
def split_every_5(lst):
    return [lst[i:i + 5] for i in range(0, len(lst), 5)]

# oh ok ts is def not my code, purely vibes
def evaluate_5(cards):
    ranks = sorted([rank_values[c.rank] for c in cards], reverse=True)
    suits = [c.suit for c in cards]
    counts = {r: ranks.count(r) for r in set(ranks)}
    count_values = sorted(counts.values(), reverse=True)
    unique_ranks = sorted(counts.keys(), reverse=True)
    is_flush = len(set(suits)) == 1
    is_straight = (
        len(set(ranks)) == 5 and
        (max(ranks) - min(ranks) == 4 or ranks == [14, 5, 4, 3, 2])
    )
    if ranks == [14, 5, 4, 3, 2]:
        ranks = [5, 4, 3, 2, 1]
    if is_straight and is_flush and max(ranks) == 14:
        return (11, ranks) # royal flush
    if is_straight and is_flush:
        return (10, ranks) # straight flush
    if count_values == [4, 1]:
        return (9, unique_ranks) # quads
    if count_values == [3, 2]:
        return (8, unique_ranks) # full house
    if is_flush:
        return (7, ranks) # flush
    if is_straight:
        return (6, ranks) # straight
    if count_values == [3, 1, 1]:
        return (5, unique_ranks) # three of a kind
    if count_values == [2, 2, 1]:
        return (4, unique_ranks) # two pairs
    if count_values == [2, 1, 1, 1]:
        pair_rank = [r for r, cnt in counts.items() if cnt == 2][0]
        if pair_rank >= 11 or pair_rank == 14:
            return (3, unique_ranks) # face card pair or aces
        else:
            return (2, unique_ranks) # pair below face cards
    if max(ranks) == 14:
        return (1, ranks) # ace high
    return (0, ranks) # high card below ace

# helper
def best_hand(cards7):
    best_score = (-1, [])
    best_combo = None
    for combo in combinations(cards7, 5):
        score = evaluate_5(combo)
        if score > best_score:
            best_score = score
            best_combo = combo
    return best_score, best_combo

# make it make money
def calculate_payout(board_cards, hole_cards):
    total = 0.0
    results = []
    for b in board_cards:
        (score, _), winning_cards = best_hand(b + hole_cards)
        payout = payouts[score]
        total += payout
        results.append({
            "score": score,
            "payout": payout,
            "winning": winning_cards
        })
    return total, results

# draw text
def holy_yap():
    text1 = font.render("102.4 = royal flush,", True, "#FFFFFF")
    text2 = font.render("51.2 = straight flush,", True, "#FFFFFF")
    text3 = font.render("25.6 = quads", True, "#FFFFFF")
    text4 = font.render("12.8 = full house", True, "#FFFFFF")
    screen.blit(text1, (scale, scale))
    screen.blit(text2, (scale, scale*6))
    screen.blit(text3, (scale, scale*11))
    screen.blit(text4, (scale, scale*16))
    text1 = font.render("6.4 = flush", True, "#FFFFFF")
    text2 = font.render("3.2 = straight", True, "#FFFFFF")
    text3 = font.render("1.6 = three of a kind", True, "#FFFFFF")
    text4 = font.render("0.8 = two pairs", True, "#FFFFFF")
    screen.blit(text1, (scale*51, scale))
    screen.blit(text2, (scale*51, scale*6))
    screen.blit(text3, (scale*51, scale*11))
    screen.blit(text4, (scale*51, scale*16))
    text1 = font.render("0.4 = face card pair or aces", True, "#FFFFFF")
    text2 = font.render("0.2 = pair below face cards", True, "#FFFFFF")
    text3 = font.render("0.1 = ace high", True, "#FFFFFF")
    text4 = font.render("0.0 = high card below ace", True, "#FFFFFF")
    screen.blit(text1, (scale*101, scale))
    screen.blit(text2, (scale*101, scale*6))
    screen.blit(text3, (scale*101, scale*11))
    screen.blit(text4, (scale*101, scale*16))

# game loop
async def main():
    static1 = generate_static(False)
    static2 = generate_static(True)
    pygame.mixer.music.load("ts_song_full_of_whimsy.ogg")
    pygame.mixer.music.play(-1)
    deck = get_new_deck()
    board = []
    shuffling = False
    deal_triggered = False
    dealing = False
    count = 0
    popups = []
    money = 100.00
    bet = 1.00

    # the house has an edge and always wins
    def draw_money():
        money_text = font.render(f"Money: ${money:.2f}", True, "#FFFFFF")
        bet_text = font.render(f"Bet: ${bet:.2f} per draw = In total, it is ${bet*10:.2f} for 10 draws", True, "#FFFFFF")
        screen.blit(money_text, (scale, height - 3*scale*4))
        screen.blit(bet_text, (scale, height - 2*scale*4))

    while True:
        for x in range(width//scale):
            for y in range(height//scale):
                pygame.draw.rect(screen, static1[random.randint(0, 255)], (x*scale, y*scale, scale, scale))
        for i in range(scale):
            pygame.draw.rect(screen, static1[random.randint(0, 255)], (0, (count*i)%height, width, scale*i))
        count += scale
        if count >= height:
            count = 0
        pygame.draw.rect(screen, static2[random.randint(0, 255)], (0, height//6, width, scale))
        pygame.draw.rect(screen, static2[random.randint(0, 255)], (0, height-height//6, width, scale))
        holy_yap()

        # input
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if not dealing:
                if event.type == pygame.FINGERDOWN:
                    shuffling = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        shuffling = True
                    if event.key == pygame.K_UP:
                        bet += 0.1
                    if event.key == pygame.K_DOWN:
                        bet = max(0.1, bet-0.1)

                if event.type == pygame.FINGERUP:
                    shuffling = False
                    deal_triggered = True
                    money -= 10.0 * bet
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        shuffling = False
                        deal_triggered = True
                        money -= 10.0 * bet

        # process
        if shuffling:
            popups = []
            board = []
            deck = get_new_deck()
            shuffle_deck(deck)

        elif deal_triggered:
            deal_triggered = False
            dealing = True

        elif dealing:
            if len(deck) == 0:
                dealing = False

            elif len(board) < 50 and len(deck) > 0:
                card = deck.pop()
                index = len(board)
                target_x = (card_w-2*scale) + index % 5 * (card_w + 2*scale) + index // 25 * (width // 2 + card_w // 2 + scale)
                target_y = (board_y - card_h//2 - 4*scale) + (index % 25 // 5) * (card_h + 2*scale)
                card.move_to((target_x, target_y))
                board.append(card)

            elif len(board) >= 50 and len(deck) >= 2:
                left = deck.pop()
                right = deck.pop()
                left.rect.topleft = (deck_pos[0] - (card_w // 2 + scale), deck_pos[1])
                right.rect.topleft = (deck_pos[0] + (card_w // 2 + scale), deck_pos[1])
                board.extend([left, right])
                dealing = False
                # for a in range(10):
                #     for b in range(5):
                #         print(split_every_5(board)[a][b].rank + split_every_5(board)[a][b].suit, end=" ")
                #     print()
                hole_cards = board[-2:]
                boards = split_every_5(board[:-2])
                total, results = calculate_payout(boards, hole_cards)
                money += total * bet
                for result in results:
                    for c in result["winning"]:
                        c.highlight = True
                for i, result in enumerate(results):
                    if result["payout"] > 0.05:
                        bx = boards[i][1].rect.centerx + card_w//2 + scale
                        by = boards[i][2].rect.top + card_h//2 + 2*scale
                        popups.append(PayoutPopup(result["payout"], (bx, by)))
                        if i == 9:
                            popups[-1].pos.x = boards[5][1].rect.centerx + card_w//2 + scale
                            popups[-1].pos.y = boards[-2][2].rect.top + card_h//2 + 2*scale + card_h + 3*scale

        # output
        for i in range(len(deck)):
            offset = i * scale // 23
            deck[i].rect.topleft = (deck_pos[0], deck_pos[1]-offset)
            deck[i].draw(screen)

        for card in board:
            card.update()
            card.draw(screen)

        for p in popups[:]:
            p.draw(screen)

        draw_money()
        pygame.display.update()
        await asyncio.sleep(0)
        clock.tick(fps)

asyncio.run(main())
