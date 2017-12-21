import config
import random
from PIL import ImageTk
import tk_ as tk


class MoveScreen(tk.Frame):
    """ An informational Screen about the character movement"""

    def __init__(self,main,app):
        tk.Frame.__init__(self,main)
        self.app = app
        self.char = app.char

        self.showMovement()


    def showMovement(self):
        phy_val = int(self.char.getAttributeValue(config.CharData.PHY))

        # check if the character has a modified strength or speed
        spd_mod = 0
        str_mod = 0

        traits = self.char.getTraits()
        for trait in traits:
            trait_name = trait.get("name")
            print(trait_name)
            effects = trait.findall("effect")
            if not effects: continue
            factor = 0
            for effect in effects:
                name = effect.get("name", "none")
                factor = effect.get("factor", "1")

            rank_value = 1
            ranks = trait.findall("rank")
            for rank in ranks:
                rank_value = rank.get("value", "1")

            factor = int(rank_value) * int(factor)
            print(name, factor)

            if name == "strength": str_mod = factor * rank_value
            elif name == "movement": spd_mod = factor * rank_value

        lift_base = phy_val + str_mod

        weight_light = lift_base * config.Core.WEIGHT_LIGHT
        weight_march = lift_base * config.Core.WEIGHT_MARCH
        weight_heavy = lift_base * config.Core.WEIGHT_HEAVY
        weight_limit = lift_base * config.Core.WEIGHT_LIMIT

        items = self.char.getItems()
        equipment_weight = 0
        clothing_weight = 0
        for item in items:
            if item.get("equipped", "0") == "1":
                if item.get("type", "item") == "clothing":
                    clothing_weight += self.char.getWeight(item)
                else:
                    equipment_weight += self.char.getWeight(item)

        info = "Kleidung: {clothing}g, Ausrüstung: {equipment}g\nPHY: {phy}\nLIFT_BASE: {lift}".format(
            clothing=clothing_weight,
            equipment=equipment_weight,
            phy=phy_val,
            lift=lift_base
        )
        a = tk.Label(self)
        a.config(text=str(info))
        a.pack()
