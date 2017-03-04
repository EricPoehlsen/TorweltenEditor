import tkinter as tk
from PIL import ImageTk
import config
msg = config.Messages()


class LogScreen(tk.Frame):
    """ The log screen displays the character edit history 

    main (tk.Tk): holding the program
    app (Application): the programs primary screen 
    """

    def __init__(self, main, app):
        tk.Frame.__init__(self, main)
        self.app = app
        self.char = app.char

        # create canvas ... 
        self.log_canvas = tk.Canvas(self, width=770, height=540)
        self.log_canvas.pack(side=tk.LEFT)
        self.log_scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.log_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.log_scroll.config(command=self.log_canvas.yview)
        self.log_canvas.config(yscrollcommand=self.log_scroll.set)

        self.renderLog()

    def renderLog(self):
        
        events_tag = self.char.getEvents()
        stored_hash = int(self.char.getEvents().get("hash"))
        current_hash = 0
        events = events_tag.findall("event")

        # draw the header
        x, y = 0, 65
        label = tk.Label(self.log_canvas, text=msg.LOG_HEADER)
        self.log_canvas.create_window(x, y, window=label, anchor=tk.NW)
        y += label.winfo_reqheight()

        # building the log display and extracting data for integrity checks
        for event in events:
            # hash for integrity check
            event_hash = self.char.hashElement(event)
            current_hash += event_hash

            op = event.get("op")

            # common data
            element = event.get("element")
            date = event.get("date")

            event_string = ""
            linebreak = True
            display = True
            x = 40
            anchor = tk.NW
            if element == "xp" and op == "upd":
                event_string = self.displayXP(event)
                linebreak = False
                x = 35
                anchor = tk.NE
            elif element == "attribute":
                event_string = self.displayAttribute(event)
            elif element == "skill":
                event_string = self.displaySkill(event)
            elif element == "data":
                event_string = self.displayData(event)
            elif element == "item":
                event_string, display = self.displayItem(event)
            elif element == "account":
                event_string = self.displayAccount(event)
            elif element == "contact":
                event_string = self.displayContact(event)
            elif element == "modified":
                event_string = msg.LOG_CORRUPT_FILE
            else:
                op = event.get("op", "")
                mod = event.get("mod", "")
                if op:
                    event_string += op
                if op and mod:
                    event_string += ": "
                if mod:
                    event_string += mod

            # show the logline on screen ...
            if linebreak:
                event_string = date + " - " + event_string
            if display:
                label = tk.Label(self.log_canvas, text=event_string)
                self.log_canvas.create_window(x, y, window=label, anchor=anchor)
                if linebreak:
                    y += label.winfo_reqheight()
 
        # display the result of the integrity checks ...
        data_integrity = tk.LabelFrame(
            self.log_canvas,
            text=msg.LOG_INTEGRITY
        )
        self.checkIntegrity(data_integrity)
        self.log_canvas.create_window(0, 0, window=data_integrity, anchor=tk.NW)

        # ... finally set the canvas scrollbox ... 
        self.log_canvas.config(scrollregion=self.log_canvas.bbox(tk.ALL))

    @staticmethod
    def displayXP(event):
        delta = int(float(event.get("mod")))
        if delta > 0:
            event_string = "+"+str(delta)
        else:
            event_string = str(delta)
        return event_string

    def displayAttribute(self, event):
        name = event.get("name")
        value = int(event.get("value"))
        event_string = "Attribut geändert" + " (" + name.upper() + "): " + str(value)
        return event_string

    def displaySkill(self, event):
        op = event.get("op")
        id = int(event.get("id"))
        value = int(event.get("value", "0"))
        skill_name = self.char.getSkillById(str(id)).get("name")
        event_string = op + ": " + skill_name + " - " + str(value)
        return event_string

    @staticmethod
    def displayData(event):
        op = event.get("op")
        data_str = {
            'name': msg.NAME,
            'species': msg.SPECIES,
            'origin': msg.ORIGIN,
            'concept': msg.CONCEPT,
            'player': msg.PLAYER,
            'height': msg.HEIGHT,
            'weight': msg.WEIGHT,
            'age': msg.AGE,
            'gender': msg.GENDER,
            'hair': msg.HAIR,
            'eyes': msg.EYES,
            'skin': msg.SKIN_COLOR,
            'skintype': msg.SKIN_TYPE
        }
        name = event.get("name")
        value = event.get("value")
        event_string = op + ": " + data_str[name] + ", " + str(value)
        return event_string

    def displayItem(self, event):
        display = True
        op = event.get("op")
        name = event.get("name")
        id = int(str(event.get("id")))
        quantity = int(event.get("quantity"))
        hash_value = int(event.get("hash"))
        event_string = ""
        if op == msg.CHAR_ITEM_ADDED:
            event_string = msg.LOG_ITEM_ADDED % (name, quantity)
        elif op == msg.CHAR_ITEM_RENAMED:
            old_name = event.get("mod")
            event_string = msg.LOG_ITEM_RENAMED % (old_name, name)
        elif op == msg.CHAR_ITEM_PACKED:
            bag_id = event.get("mod")
            bag_item = self.char.getItemById(bag_id)
            if bag_item is not None:
                bag_name = bag_item.get("name")
            else:
                bag_name = msg.LOG_ITEM_UNKNOWN
            event_string = msg.LOG_ITEM_PACKED.format(
                name=name,
                container=bag_name
            )
        elif op == msg.CHAR_ITEM_UNPACKED:
            bag_id = event.get("mod")
            bag_item = self.char.getItemById(bag_id)
            if bag_item is not None:
                bag_name = bag_item.get("name")
                event_string = msg.LOG_ITEM_UNPACKED.format(
                    name=name,
                    container=bag_name
                )
            else:
                display = False
        elif op == msg.CHAR_ITEM_EQUIP:
            event_string = msg.LOG_ITEM_EQUIPPED.format(
                name=name
            )
        elif op == msg.CHAR_ITEM_BAG or op is None:
            display = False
        else:
            event_string = name + " " + str(quantity) + " " + str(op)
        return event_string, display

    @staticmethod
    def displayAccount(event):
        op = event.get("op", "")
        amount = float(event.get("mod", "0"))
        amount = "{:+.2f}".format(amount)

        event_string = op + " " + amount

        return event_string

    def displayContact(self, event):
        op = event.get("op")
        mod = event.get("mod")
        id = int(str(event.get("id")))
        contact = self.char.getContactById(id)

        name = contact.get("name")

        changes = []
        if "name" in mod:
            name = event.get("oldname")
            changes.append((
                msg.LOG_CONTACT_RENAMED,
                contact.get("name", "")
            ))
        if "location" in mod:
            changes.append((
                msg.LOG_CONTACT_LOCATION,
                event.get("loc", "")
            ))
        if "competency" in mod:
            competency = event.get("comp", "")
            if competency != "":
                changes.append((
                    msg.LOG_CONTACT_COMPETENCY,
                    competency
                ))
        if "loyality" in mod:
            changes.append((
                msg.LOG_CONTACT_LOYALITY,
                event.get("loy", "")
            ))
        if "frequency" in mod:
            changes.append((
                msg.LOG_CONTACT_FREQUENCY,
                event.get("frq", "")
            ))
        if "description" in mod:
            desc = event.get("desc")
            if desc:
                changes.append((
                    msg.LOG_CONTACT_DESC,
                    msg.LOG_CONTACT_DESC_CHANGED
                ))
            else:
                changes.append((
                    msg.LOG_CONTACT_DESC,
                    msg.LOG_CONTACT_DESC_CHANGED
                ))

        info = ""
        for change in changes:
            what, diff = change
            info += what + diff + ", "
        info = info[0:-2]
        event_string = msg.LOG_CONTACT_CHANGED.format(
            id=id,
            name=name,
            diff=info)

        return event_string

    def checkIntegrity(self, frame):
        tick = ImageTk.PhotoImage(file="ui_img/tick.png")
        cross = ImageTk.PhotoImage(file="ui_img/cross.png")

        icon = tk.Label(frame)
        icon.pack(side=tk.LEFT)

        text = tk.Label(frame)
        text.pack(side=tk.LEFT)

        hash_element = self.char.getHashes()
        if hash_element is None:
            icon.config(image=tick)
            icon.image = tick
            text.config(text=msg.LOG_UNSAVED)
        else:
            check = hash_element.get("check")
            modified = self.char.getModified()
            if check == "1" and modified is None:
                icon.config(image=tick)
                icon.image = tick
                text.config(text=msg.LOG_OKAY)
            else:
                icon.config(image=cross)
                icon.image = cross
                text.config(text=msg.LOG_WARN)