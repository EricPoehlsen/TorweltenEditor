import tkinter as tk
from PIL import ImageTk
import config
msg = config.Messages()


class LogScreen(tk.Frame):
    """ The log screen displays the character edit history 

    main (tk.Tk): holding the program
    app (Application): the programs primary screen 
    """

    def __init__(self,main,app):
        tk.Frame.__init__(self,main)
        self.app = app
        self.char = app.char

        # create canvas ... 
        self.log_canvas = tk.Canvas(self, width=770, height=540)
        self.log_canvas.pack(side=tk.LEFT)
        self.log_scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.log_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.log_scroll.config(command=self.log_canvas.yview)
        self.log_canvas.config(yscrollcommand=self.log_scroll.set)

        # for integrity checking ...
        self.skills = {}
        self.attributes = {}
        self.items = {}
        self.contacts = {}

        self.renderLog()

    def renderLog(self):
        
        events_tag = self.char.getEvents()
        stored_hash = int(self.char.getEvents().get("hash"))
        current_hash = 0
        events = events_tag.findall("event")
        y = 65
        
        # building the log display and extracting data for integrity checks
        for event in events:
            # hash for integrity check
            event_hash = self.char.hashElement(event)
            current_hash += event_hash
            
            # common data
            element = event.get("element")
            op = event.get("op", "")
            mod = event.get("mod", "")
            date = event.get("date")

            linebreak = True
            x = 40
            anchor = tk.NW
            if element == "xp":
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
                event_string = self.displayItem(event)
            elif element == "contact":
                event_string = self.displayContact(event)
            else:
                event_string = op + mod

            # show the logline on screen ...

            if linebreak:
                event_string = date + " - " + event_string

            label = tk.Label(self.log_canvas, text=event_string)
            self.log_canvas.create_window(x, y, window=label, anchor=anchor)

            if linebreak:
                y += label.winfo_reqheight()
 
        # checking the log file integrity ... 
        data_integrity = tk.LabelFrame(
            self.log_canvas,
            text="Datenintegrität"
            )
        check_frame = Checkresults(
            data_integrity,
            text="Ereignisliste",
            relief=tk.RIDGE,
            borderwidth=2
            )
        stored_hash = int(events_tag.get("hash"))
        if stored_hash == current_hash:
            check_frame.setStatus("okay")
        else: 
            check_frame.setStatus("error")
        check_frame.pack(side = tk.LEFT)

        # checking the attributes integrity ...
        check_frame = Checkresults(
            data_integrity,
            text="Attribute",
            relief=tk.RIDGE,
            borderwidth=2
            )
        check_frame.setStatus("okay")
        for name in self.attributes:
            char_value = self.char.getAttributeValue(name)
            event_value = self.attributes[name]
            if char_value != event_value:
                check_frame.setStatus("error")
        check_frame.pack(side=tk.LEFT)

        # checking the skills for integrity
        check_frame = Checkresults(
            data_integrity,
            text="Fertigkeiten",
            relief=tk.RIDGE,
            borderwidth=2
            )
        check_frame.setStatus("okay")
        for skill in self.skills:
            id = skill
            char_skill = self.char.getSkillById(id)
            value = char_skill.get("value")
            if self.skills[id] != value:
                check_frame.setStatus("error")
        check_frame.pack(side=tk.LEFT)

        # inventory integrity check
        check_frame = Checkresults(
            data_integrity,
            text="Inventar",
            relief=tk.RIDGE,
            borderwidth=2
            )
        check_frame.setStatus("okay")
        current_items = self.char.getItems()
        for item in current_items:
            id = int(item.get("id"))
            hash_value = self.char.hashElement(item)
            logged_hash = self.items[id]
            if hash_value != logged_hash:
                check_frame.setStatus("error")
        check_frame.pack(side = tk.LEFT)

        # display the result of the integrity checks ... 
        self.log_canvas.create_window(0, 0, window=data_integrity, anchor=tk.NW)

        # ... finally set the canvas scrollbox ... 
        self.log_canvas.config(scrollregion = self.log_canvas.bbox(tk.ALL))

    def displayXP(self,event):
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
        # add data to integrity check
        self.attributes[name] = value
        return event_string

    def displaySkill(self,event):
        op = event.get("op")
        id = int(event.get("id"))
        value = int(event.get("value", "0"))
        skill_name = self.char.getSkillById(str(id)).get("name")
        event_string = op + ": " + skill_name + " - " + str(value)
        # storing data for the integrity check
        self.skills[id] = value
        return event_string

        # data modifications
    def displayData(self, event):
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

    # retrieve inventory data ...
    def displayItem(self, event):
        op = event.get("op")
        name = event.get("name")
        id = int(str(event.get("id")))
        quantity = int(event.get("quantity"))
        hash_value = int(event.get("hash"))
        if op == msg.CHAR_ITEM_ADDED:
            event_string = msg.LOG_ITEM_ADDED % (name, quantity)
        if op == msg.CHAR_ITEM_RENAMED:
            old_name = event.get("mod")
            event_string = msg.LOG_ITEM_RENAMED % (old_name, name)
        else:
            event_string = name + " " + str(quantity) + " " + op
        # for the integrity check ...
        self.items[id] = hash_value
        return event_string

    # retrieve inventory data ...
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

        # for the integrity check ...
        hash_value = int(event.get("hash"))
        self.contacts[id] = hash_value
        return event_string

class Checkresults(tk.Frame):
    """ A two-state status display

    it adds two kwargs: 
    status (string): "okay" or "error" 
    text (string): some kind of descriptive text ...
    """
    def __init__(self,*args,status=None,text=None,**kwargs):
        tk.Frame.__init__(self,*args,**kwargs)
        self.tick = ImageTk.PhotoImage(file="ui_img/tick.png")
        self.cross = ImageTk.PhotoImage(file="ui_img/cross.png")

        self.status = None
        self.icon = tk.Label(self)
        self.icon.pack(side = tk.LEFT)
        self.label = tk.Label(self, text=text)
        self.label.pack(side=tk.RIGHT) 

        if status: 
            self.setStatus(status)

    def setStatus(self,status=None):
        if status == "okay":
            self.icon.config(image = self.tick)
            self.status = status
        elif status == "error":
            self.icon.config(image = self.cross)
            self.status = status
        return self.status
