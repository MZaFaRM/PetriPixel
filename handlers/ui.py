import pygame
from components.home import EnvComponent, HomeComponent, SidebarComponent
from config import Colors, image_assets
from copy import deepcopy


class UIHandler:
    def __init__(self):
        self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("DARWIN")
        self.bg_image = pygame.image.load(image_assets + "/background.svg")
        self.surface.blit(self.bg_image, (0, 0))

        self.screen_states = {
            "current_screen": "home",
            "screens": ["home"],
            "home": {
                "components": {
                    "env": {
                        "handler": EnvComponent,
                        "custom_position": {
                            "topleft": (50, 100),
                        },
                    },
                    "sidebar": {
                        "handler": SidebarComponent,
                        "custom_position": {
                            "topright": (self.surface.get_width() - 50, 50),
                        },
                    },
                    "main": {
                        "handler": HomeComponent,
                        "custom_position": {
                            "topleft": (0, 0),
                        },
                    },
                },
                "context": {},
            },
        }

    def initialize_screen(self, screen="home"):
        self.screen_states["current_screen"] = screen
        self.screen_states["rendered_components"] = {}

        for name, info in self.screen_states[screen]["components"].items():
            rendered_component = info["handler"](
                main_surface=self.surface,
                context=self.screen_states[screen].get("context", {}),
            )
            self.screen_states["rendered_components"][name] = {
                **info,
                "handler": rendered_component,
            }

    def _event_handler(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            for name, info in self.screen_states["rendered_components"].items():
                yield from info["handler"]._event_handler(event) or []

    def update_screen(self, context=None):
        self.surface.blit(self.bg_image, (0, 0))

        for name, info in self.screen_states["rendered_components"].items():
            info["handler"].update(context=context)
            rect = info["handler"].surface.get_rect(**info["custom_position"])
            self.surface.blit(info["handler"].surface, dest=rect)

        pygame.display.flip()

    def get_component(self, name):
        return self.screen_states["rendered_components"].get(name)["handler"]
