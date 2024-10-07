import time
import pygame
from pygame.sprite import Sprite
from gym.spaces import MultiDiscrete
import random
import numpy as np
import helper
import torch
import torch.nn as nn
from config import CreatureManager
from config import SensorManager
import config

CREATURE_MANAGER = CreatureManager()


class OrganismNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(OrganismNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.sigmoid(self.fc2(x))
        return x


class Creature(Sprite):
    def __init__(
        self,
        env,
        screen,
        radius=5,
        n=100,
        color=(151, 190, 90),
        parent=None,
        genes="",
    ):
        super().__init__()

        self.screen = screen
        self.env = env

        self.parent = parent

        self.radius = radius
        self.n = n

        self.brain = OrganismNN(
            input_size=5,
            hidden_size=10,
            output_size=5,
        )

        self.energy = self.max_energy = 1000

        self.hunger = 2
        self.dead = False

        self.done = False
        self.color = color

        # Create a transparent surface for the creature
        surface_size = (2 * radius) + 4  # Total size of the surface
        self.image = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)

        # Random position within screen bounds
        self.closest_edge = None

        # Calculate center of the surface
        self.center = (surface_size // 2, surface_size // 2)

        # Draw the outer black circle and inner colored circle at the center
        self.draw_self(radius, color)

        # Get rect for positioning
        self.rect = self.image.get_rect()
        self.rect.center = helper.get_edge_position(radius, screen)

        self.DNA = CREATURE_MANAGER.register_creature(self)

    def set_closest_edge(self, position):
        if self.closest_edge:
            return self.closest_edge

        left = 0
        up = 0
        right = self.env.screen_width - 0
        down = self.env.screen_height - 0

        x, y = position

        distance_up = y - up
        distance_down = down - y
        distance_left = x - left
        distance_right = right - x

        distances = {
            "up": distance_up,
            "down": distance_down,
            "left": distance_left,
            "right": distance_right,
        }

        closest_edge = min(distances, key=distances.get)

        if closest_edge == "up":
            self.closest_edge = (x, up)
        elif closest_edge == "down":
            self.closest_edge = (x, down)
        elif closest_edge == "left":
            self.closest_edge = (left, y)
        elif closest_edge == "right":
            self.closest_edge = (right, y)

        return self.closest_edge

    def draw_self(self, radius, color, border_thickness=2, border_color=(0, 0, 0)):
        pygame.draw.circle(
            self.image,
            border_color,
            self.center,
            radius + border_thickness,
        )
        pygame.draw.circle(
            self.image,
            color,
            self.center,
            radius,
        )

    def step(self):
        observation = self.get_observation()
        # self.energy -= 1
        # if self.energy < 0:
        #     self.done = True
        # return
        if not (self.dead or self.done):
            self.energy -= 1
            # input_data = torch.tensor([0.5, 1.0, 0.2, 0.9, 0.3])
            # actions = self.brain(input_data)
            # best_action = actions[torch.argmax(actions).item()]

            if self.energy <= 0:
                self.die()
                return

            if self.hunger > 0:
                food_available = env.nearest_food(self.rect.center)
                if food_available is not None:
                    if env.touching_food(self.rect.center):
                        self.eat()
                    else:
                        self.move_in_direction(SensorManager.obs_Nfd(self.env, self))
                        pass

                else:
                    if self.hunger == 1:
                        self.move_in_direction(SensorManager.obs_Nfd(self.env, self))
                    else:
                        self.die()
                        return
            else:
                self.move_towards(self.set_closest_edge(self.rect.center))

            if self.rect.center == self.closest_edge:
                self.progress()

    def reset(self):
        self.hunger = 2
        self.done = False
        self.energy = self.max_energy
        self.closest_edge = None
        self.original_position = helper.get_edge_position(self.radius, self.screen)
        self.rect.center = self.original_position
        self.draw_self(self.radius, self.color)

    def progress(self):
        if not self.done:
            if self.hunger == 0:
                self.reproduce()
            elif self.hunger == 1:
                pass
            else:
                self.die()
            self.done = True

    def reproduce(self):
        self.draw_self(self.radius, (128, 0, 128))
        self.env.children.add(
            Creature(
                self.env,
                self.screen,
                radius=self.radius,
                n=self.n,
            )
        )

    def die(self):
        self.dead = True
        self.done = True
        self.draw_self(self.radius, (255, 0, 0))

    def eat(self):
        self.hunger -= 1

    def move_towards(self, target, speed=1.0):
        direction = np.array(target) - np.array(self.rect.center)
        norm = np.linalg.norm(direction)
        if norm > 0:
            direction = direction / norm  # Normalize direction vector
        new_position = np.array(self.rect.center) + direction * speed
        self.rect.center = new_position
        
    def move_in_direction(self, target, speed=1.0):
        # direction = np.array(target) - np.array(self.rect.center)
        # Step 1: Convert degrees to radians
        direction_radians = np.radians(target)
        
        # Step 2: Calculate the change in x and y coordinates
        dx = speed * np.cos(direction_radians) * speed
        dy = speed * np.sin(direction_radians) * speed
        
        # Step 3: Update the current position
        new_position = (self.rect.center[0] + dx, self.rect.center[1] + dy)
        
        self.rect.center = new_position

    def get_observation(self):
        if not hasattr(self, "parsed_dna"):
            self.parsed_dna = CREATURE_MANAGER.get_parsed_dna(self.DNA)

        observations = []
        for sensor in self.parsed_dna:
            observation_func = getattr(SensorManager, f"obs_{sensor}", None)
            if observation_func is not None:
                observation = observation_func(self.env, self)
                observations.append(observation)
            else:
                # Handle the case where the sensor doesn't exist (optional)
                raise Exception(f"Error: No method for sensor {sensor}")
        return observations

    def render(self):
        # Blit the food image to the screen at its position
        self.screen.blit(self.image, self.rect.topleft)


class Food(Sprite):
    def __init__(self, env, screen, radius=8, n=100, color=(232, 141, 103)):
        super().__init__()

        self.screen = screen
        self.env = env

        self.radius = radius
        self.n = n

        # Create a transparent surface for the food
        self.image = pygame.Surface(
            ((2 * radius) + 5, (2 * radius) + 5), pygame.SRCALPHA
        )

        # Random position within screen bounds
        self.position = (
            random.randint(radius + 75, screen.get_width() - radius - 75),
            random.randint(radius + 75, screen.get_height() - radius - 75),
        )

        # Create the circle on the image surface (center of the surface)
        pygame.draw.circle(self.image, color, (radius + 2, radius + 2), radius)

        # Get rect for positioning
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def draw(self):
        # Blit the food image to the screen at its position
        self.screen.blit(self.image, self.rect.topleft)


class Nature:
    def __init__(self):
        self.background_color = (243, 247, 236)
        self.food_color = (232, 141, 103)
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Walker")

        self.action_space = MultiDiscrete([3, 3])
        self.observation_space = None

        self.truncation = 1_000_000

        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        self.generate_creatures(n=1)
        self.foods = pygame.sprite.Group()
        self.children = pygame.sprite.Group()

        self.reset()

    def generate_creatures(self, radius=5, n=50):
        self.creatures = pygame.sprite.Group()
        for _ in range(n):
            # food sprite group
            self.creatures.add(Creature(self, self.screen, radius=radius, n=n))

    def generate_food(self, radius=5, n=100):
        self.foods = pygame.sprite.Group()
        for _ in range(n):
            # food sprite group
            self.foods.add(Food(self, self.screen, radius=radius, n=n))

    def nearest_food(self, position):
        creature_pos = np.array(position)
        food_positions = np.array([food.position for food in env.foods])

        # Squared distances
        distances = np.sum((food_positions - creature_pos) ** 2, axis=1)

        # If there are no food objects
        if len(distances) == 0:
            # No food, so return infinite distance and no position
            return None

        # Find the index of the nearest food
        nearest_index = np.argmin(distances)

        # Return the nearest distance and its coordinates
        nearest_coordinates = food_positions[nearest_index]

        return nearest_coordinates

    def touching_food(self, position):
        for food in self.foods:
            if food.rect.collidepoint(position):
                self.foods.remove(food)
                return True
        return False

    def step(self):
        self.time_alive += 1
        reward = 0

        # Batch all steps before rendering
        for creature in self.creatures:
            creature.step()

        if self.time_alive >= self.truncation:
            self.done = True
            self.truncated = True

        self.done = all(creature.done for creature in self.creatures)
        self.truncated = len(self.creatures) == 0
        return self.get_observation(), reward, self.done, self.truncated

    def reset(self):
        time.sleep(1)

        self.done = False
        self.truncated = False
        self.time_alive = 0
        self.generate_food(n=100)

        self.new_generation = pygame.sprite.Group()

        for creature in self.creatures:
            if not creature.dead:
                creature.reset()
                self.new_generation.add(creature)

        for creature in self.children:
            self.new_generation.add(creature)

        self.creatures = self.new_generation.copy()
        self.children = pygame.sprite.Group()
        self.new_generation = pygame.sprite.Group()
        print(len(self.creatures))

    def render(self):
        self.screen.fill(self.background_color)
        self.foods.draw(self.screen)  # Render all food items
        self.creatures.draw(self.screen)  # Render all creatures
        pygame.display.update()

    def get_observation(self):
        return None


env = Nature()

while True:
    env.reset()
    env.render()
    done = False
    truncated = False

    while not (done or truncated):
        observation, reward, done, truncated = env.step()
        env.render()

    break

    if truncated:
        break
