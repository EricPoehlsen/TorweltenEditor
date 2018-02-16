import config
import random
from PIL import ImageTk
import tk_ as tk

msg = config.Messages()

class MoveScreen(tk.Frame):
    """ An informational Screen about the character movement"""

    def __init__(self,main,app):
        tk.Frame.__init__(self,main)
        self.app = app
        self.char = app.char

        self.showEffectiveMovement()


    def showEffectiveMovement(self):
        """ Calculate and show effective character movement

        This takes into account the encumberence of equipment
        as well as the effects of relevant character traits

        """

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
                if name not in ["strength", "movement"]: continue
                factor = int(effect.get("factor", "1"))

                rank_value = 1
                ranks = trait.findall("rank")
                for rank in ranks:
                    rank_value = int(rank.get("value", "1"))

                if name == "strength":
                    str_mod += factor * rank_value
                elif name == "movement":
                    spd_mod += factor * rank_value

        lift_base = phy_val + str_mod
        speed_base = phy_val + spd_mod

        weights = [
            lift_base * config.Core.WEIGHT_LIGHT,
            lift_base * config.Core.WEIGHT_MARCH,
            lift_base * config.Core.WEIGHT_HEAVY,
            lift_base * config.Core.WEIGHT_LIMIT
        ]
        range_light = msg.MV_WEIGHT_RANGE.format(low=0, high=weights[0])
        range_march = msg.MV_WEIGHT_RANGE.format(low=weights[0], high=weights[1])
        range_heavy = msg.MV_WEIGHT_RANGE.format(low=weights[1], high=weights[2])
        range_limit = msg.MV_WEIGHT_RANGE.format(low=weights[2], high=weights[3])

        # retrieve the current encumberance
        items = self.char.getItems()
        equipment_weight = 0
        clothing_weight = 0
        excess_weight = 0
        for item in items:
            if item.get("equipped", "0") == "1":
                if item.get("type", "item") == "clothing":
                    clothing_weight += self.char.getWeight(item)
                    if clothing_weight > range_light:
                        excess_weight += clothing_weight - range_light
                        clothing_weight = range_light
                else:
                    equipment_weight += self.char.getWeight(item)

        weight_list = [
            (msg.MV_WEIGHT_LIGHT, range_light),
            (msg.MV_WEIGHT_MARCH, range_march),
            (msg.MV_WEIGHT_HEAVY, range_heavy),
            (msg.MV_WEIGHT_LIMIT, range_limit)
        ]

        gross_weight = equipment_weight + excess_weight
        encumberance = 0

        weight_table = tk.LabelFrame(self, text=msg.MV_WEIGHT_CLASSES)

        for row, data in enumerate(weight_list):
            active = False
            if gross_weight >= weights[row] * 1000:
                encumberance += 1
            if encumberance == row: active = True

            label = tk.Label(weight_table, text=data[0])
            value = tk.Label(weight_table, text=data[1])

            if active:
                label.config(config.Style.RED)
                value.config(config.Style.RED)

            label.grid(row=row, column=0, sticky=tk.W)
            value.grid(row=row, column=1, sticky=tk.W)
        weight_table.pack()

        hex_img = ImageTk.PhotoImage(file="img/hex.png")
        hex_start = ImageTk.PhotoImage(file="img/hex_start.png")
        hex_jump_start = ImageTk.PhotoImage(file="img/hex_jump_start.png")
        hex_jump_start_1 = ImageTk.PhotoImage(file="img/hex_jump_start_1.png")
        hex_jump = ImageTk.PhotoImage(file="img/hex_jump.png")
        hex_jump_land = ImageTk.PhotoImage(file="img/hex_start.png")
        hex_light = ImageTk.PhotoImage(file="img/hex_light.png")
        hex_march = ImageTk.PhotoImage(file="img/hex_march.png")
        hex_heavy = ImageTk.PhotoImage(file="img/hex_heavy.png")
        hex_limit = ImageTk.PhotoImage(file="img/hex_limit.png")

        running_table = tk.LabelFrame(self, text=msg.MV_RUNNING)
        for i in range(0, speed_base + 1):
            img = None
            if i == speed_base:
                img = hex_light
            elif i == speed_base - 1:
                img = hex_march
            elif i == speed_base - 3:
                img = hex_heavy
            else:
                img = hex_img

            if i == 0:
                img = hex_start
            if i == 1:
                img = hex_limit

            if not img:
                img = hex_img

            label = tk.Label(
                running_table,
                padx=0,
                pady=0,
                border=0,
                image=img
            )
            label.image = img
            label.pack(side=tk.LEFT, padx=0, pady=0)
        running_table.pack()

        jumping_table = tk.LabelFrame(self, text=msg.MV_JUMPING)
        jump_distance = int(round(speed_base / 2))
        start_distance = int(round(jump_distance / 2))
        if start_distance < 1: start_distance = 1
        if jump_distance < 1: jump_distance = 1
        for i in range(start_distance + jump_distance + 1):
            if i < start_distance:
                if i == 0:
                    if start_distance == 1:
                        img = hex_jump_start_1
                    else: img = hex_start
                elif i < start_distance - 1:
                    img = hex_img
                else: img = hex_jump_start
            else:
                if i == start_distance + jump_distance:
                    img = hex_jump_land
                else:
                    i = hex_jump

            label = tk.Label(
                jumping_table,
                padx=0,
                pady=0,
                border=0,
                image=img
            )
            label.image = img
            label.pack(anchor = tk.S, side=tk.LEFT, padx=0, pady=0)

        jumping_table.pack()


        info = "Kleidung: {clothing}g, Ausrüstung: {equipment}g\nPHY: {phy}\nLIFT_BASE: {lift}".format(
            clothing=clothing_weight,
            equipment=equipment_weight,
            phy=phy_val,
            lift=lift_base
        )
        a = tk.Label(self)
        a.config(text=str(info))
        a.pack()
