from collections import deque
from math import log
from random import randint

import matplotlib.pyplot as plt
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
    ColorProperty)
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivymd.app import MDApp

GRAVITY = 6.67430e-11
SCALE = 2e6  # one pixel in meters


# GRAVITY = 1


class Planet(EventDispatcher):

    pos: Vector = ObjectProperty(Vector(-2, 17))
    speed: Vector = ObjectProperty()
    mass: float = NumericProperty(1)
    name: str = StringProperty("Planet")
    radius: float = NumericProperty()
    force: Vector = ObjectProperty(Vector(0, 0))
    color = ColorProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"""{self.name.capitalize()}(
    pos: {tuple(self.pos)}, 
    speed: {tuple(self.speed)}, 
    mass: {self.mass}, 
    force: {tuple(list(map(round, self.force)))}
)"""

    def gravity(self, other: "Planet"):
        d = other.pos - self.pos
        f = GRAVITY * self.mass * other.mass / d.length() ** 3
        self.force = self.force + f * d

    def update(self, dt):
        a = self.force * dt / self.mass
        # print(self.force, a, self.name)
        self.speed += a
        self.pos = self.pos + self.speed * dt
        # print(self.pos)
        self.force = Vector(0, 0)


def evolve(objects, dt):
    for a in objects:
        for b in objects:
            if a is not b:
                a.gravity(b)

    for a in objects:
        a.update(dt)


class PlanetWidget(Widget):
    planet = ObjectProperty(Planet(), rebind=True)
    color = ListProperty()
    trail : list = ListProperty()

    def __init__(self, planet, **kwargs):

        super().__init__(**kwargs)

        self.planet = planet
        self.size = (log(planet.mass) / 5,) * 2


    def update_pos(self, *args):
        self.center = self.to_screen(self.planet.pos)
        self.size = (self.planet.radius / SCALE * 10,) * 2

        if self.planet.name == 'Moon':
            save = tuple(self.center)
        else:
            save = self.planet.pos

        self.trail.append(save)
        if len(self.trail) > 400:
            self.trail.pop(0)

    def to_screen(self, pos):
        rel_pos = pos - self.parent.get_planet("Earth").pos
        return rel_pos / SCALE + self.parent.center

    def mult_to_screen(self, poss):
        if not poss: return []
        earth = self.parent.get_planet("Earth").pos
        r = list(map(lambda p: (p - earth) / SCALE + self.parent.center, poss))
        return r


class Eggplant(Widget):

    planets = ListProperty()
    dt = NumericProperty(60)

    def __init__(self, planets, **kwargs):
        super().__init__(**kwargs)
        self.planets = planets

        Clock.schedule_interval(lambda *a: self.update(), 1 / 100)

    def on_planets(self, *args):
        for pl in self.planets:
            self.add_widget(PlanetWidget(pl))

    def get_planet(self, name):
        for p in self.planets:
            if p.name == name:
                return p
        raise ValueError("No such planet")

    def update(self):
        for _ in range(200):
            evolve(self.planets, dt=self.dt)
        for w in self.children:
            if isinstance(w, PlanetWidget):
                w.update_pos()


class EggplantApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Eggplant"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Purple"

    def build(self):
        sun = Planet(
            pos=Vector(0, 0),
            speed=Vector(0, 0),
            mass=1.98847e30,
            radius=6.957e8,
            name="Sun",
        )
        earth = Planet(
            pos=Vector(149_598_023_000, 0),
            speed=Vector(0, 28000),
            mass=5.9722e24,
            radius=6_378_000,
            name="Earth",
            color='#00a5ff'
        )

        moon = Planet(
            pos=earth.pos + Vector(384_402_000, 0),
            speed=earth.speed + Vector(0, 1_022),
            mass=7.342e22,
            radius=1_737_000,
            name="Moon",
            color='faf5e0'
        )

        planets = [sun, earth, moon]

        return Eggplant(planets)


if __name__ == "__main__":
    EggplantApp().run()
