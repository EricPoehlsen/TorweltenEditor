import tk_ as tk
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
        events = events_tag.findall("event")

        # draw the header
        x, y = 0, 0
        label = tk.Label(self.log_canvas, text=msg.LOG_HEADER)
        self.log_canvas.create_window(
            x,
            y,
            window=label,
            anchor=tk.NW,
        )
        y += label.winfo_reqheight()

        # building the log display
        for event in events:

            op = event.get("op")

            # common data
            element = event.get("element")
            date = event.get("date")

            event_string = ""
            linebreak = True
            display = True
            x = 40
            anchor = tk.NW
            if element == "xp":
                if op == msg.CHAR_UPDATED:
                    event_string = self.displayXP(event)
                    linebreak = False
                    x = 35
                    anchor = tk.NE
                else:
                    event_string = self.displayXP(event)
            elif element == "attribute":
                event_string = self.displayAttribute(event)
            elif element == "skill":
                event_string = self.displaySkill(event)
            elif element == "data":
                event_string = self.displayData(event)
            elif element == "item":
                event_string, display = self.displayItem(event)
            elif element == "account":
                amount = float(event.get("mod", "0"))
                if amount:
                    event_string = self.displayAccount(event)
                else:
                    linebreak = False
            elif element == "contact":
                event_string = self.displayContact(event)
            elif element == "modified":
                event_string = msg.LOG_CORRUPT_FILE
            elif element == "character":
                event_string = self.displayCharacter(event)
            elif element == "edit":
                event_string = self.displayEditMode(event)
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
 
        # ... finally set the canvas scrollbox ...
        self.log_canvas.config(scrollregion=self.log_canvas.bbox(tk.ALL))

    @staticmethod
    def displayXP(event):
        delta = int(float(event.get("mod", "0")))
        if delta > 0:
            event_string = "+"+str(delta)
        else:
            event_string = str(delta)

        op = event.get("op")
        if op == msg.CHAR_INITIAL_XP:
            event_string = msg.LOG_INITIAL_XP + event_string
        return event_string

    @staticmethod
    def displayCharacter(event):
        event_string = ""
        op = event.get("op")
        if op == msg.CHAR_LOADED:
            return msg.LOG_CHAR_LOADED
        if op == msg.CHAR_SAVED:
            return msg.LOG_CHAR_SAVED
        if op == msg.CHAR_CREATED:
            return msg.LOG_CHAR_CREATED
        return event_string

    @staticmethod
    def displayEditMode(event):
        event_string = ""
        modes = {
            "generation": msg.LOG_EDIT_GENERATION,
            "edit": msg.LOG_EDIT_EDIT,
            "simulation": msg.LOG_EDIT_SIM,
            "view": msg.LOG_EDIT_VIEW
        }
        mode = event.get("mod")
        return modes[mode]

    @staticmethod
    def displayAttribute(event):
        name = event.get("name")
        value = int(event.get("value"))
        event_string = msg.LOG_ATTRIBUTE_CHANGED.format(
            name=name.upper(),
            value=value
        )
        return event_string

    def displaySkill(self, event):
        op = event.get("op")
        id = event.get("id")

        event_string = ""
        if op == msg.CHAR_ADDED:
            event_string = msg.LOG_SKILL_ADDED
        if op == msg.CHAR_UPDATED:
            event_string = msg.LOG_SKILL_UPDATED
        if op == msg.CHAR_REMOVED:
            event_string = msg.LOG_SKILL_REMOVED
        name = event.get("name")
        value = event.get("value", "0")

        event_string = event_string.format(name=name, value=value)
        return event_string

    @staticmethod
    def displayData(event):
        op = event.get("op")
        mod = event.get("mod")
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
        name = event.get("name", "")
        value = event.get("value", "")
        event_string = ""
        if op == msg.CHAR_ADDED:
            event_string = msg.LOG_DATA_ADDED
        if op == msg.CHAR_UPDATED:
            event_string = msg.LOG_DATA_UPDATED
            if value == "":
                event_string = msg.LOG_DATA_REMOVED
            elif not mod:
                event_string = msg.LOG_DATA_ADDED

        event_string = event_string.format(
            name=data_str[name],
            value=value,
            old=mod
        )
        return event_string

    def displayItem(self, event):
        display = True
        op = event.get("op")
        mod = event.get("mod")
        name = event.get("name")
        id = int(str(event.get("id")))
        quantity = int(event.get("quantity"))
        event_string = ""
        if op == msg.CHAR_ADDED:
            new = event.get("mod")
            event_string = msg.LOG_ITEM_ADDED.format(
                new=new,
                name=name,
                total=quantity
            )
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
        elif op == msg.CHAR_ITEM_REPAIRED:
            event_string = msg.LOG_ITEM_REPAIRED.format(
                name=name,
                value=mod
            )
        elif op == msg.CHAR_ITEM_SPLIT:
            event_string = msg.LOG_ITEM_SPLIT.format(
                name=name,
                quantity = quantity
            )
        elif op == msg.CHAR_ITEM_SPLIT:
            event_string = msg.LOG_ITEM_JOIN.format(
                name=name,
                quantity=quantity
            )
        elif op == msg.CHAR_ITEM_SELL:
            event_string = msg.LOG_ITEM_SELL.format(
                name=name,
                quantity=quantity
            )
        elif op == msg.CHAR_ITEM_DESTROY:
            event_string = msg.LOG_ITEM_DESTROY.format(
                name=name,
                quantity=quantity
            )
        elif op == msg.CHAR_ITEM_DAMAGED:
            event_string = msg.LOG_ITEM_DAMAGED.format(
                name=name,
                value=mod
            )
        elif op == msg.CHAR_ITEM_BAG or op is None:
            display = False
        else:
            event_string = name + " " + str(quantity) + " " + str(op)
        return event_string, display

    @staticmethod
    def displayAccount(event):
        op = event.get("op", "")
        event_string = ""
        amount = float(event.get("mod", "0"))
        amount_str = "{:+.2f}".format(amount)

        if op == msg.CHAR_STARTING_CAPITAL:
            if amount > 0:
                event_string = msg.LOG_ACCOUNT_CAP_INC
            else:
                event_string = msg.LOG_ACCOUNT_CAP_DEC
            event_string = event_string.format(amount=amount_str)
        else:
            event_string = op + " " + amount_str

        return event_string

    def displayContact(self, event):
        op = event.get("op")
        mod = event.get("mod")
        id = event.get("id")
        contact = self.char.getContactById(id)

        if contact is None:
            return msg.LOG_CONTACT_UNKNOWN +id

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
