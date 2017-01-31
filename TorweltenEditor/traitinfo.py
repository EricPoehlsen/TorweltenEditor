# coding=utf-8
import tkinter as tk
import config

#Display additional information about selected traits ... # #
class TraitInfo:
    def __init__(self,main, event):
        self.main = main
        self.char = main.char
        self.traits = main.traits

        # build the window ...
        width = 200
        height = 50
        x = event.x_root
        y = event.y_root
        geometry = "+"+str(x)+"+"+str(y)
        
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        self.window.geometry(geometry)
        self.window.bind("<FocusOut>", lambda a: self.window.destroy())
        self.frame = tk.Frame(self.window, borderwidth = 3, relief = tk.GROOVE, background = config.Colors.LIGHT_YELLOW)

        # get the information ...
        self.char_trait = self.getCharTrait(event)
        self.trait_name = self.char_trait.get("name")
        self.trait = self.traits.getTrait(self.trait_name)
        self.selected = self.char_trait.find("./selected")
        self.id = self.char_trait.get("id")

        self.trait_xp = self.char_trait.get("xp")
        self.title_frame = tk.Frame(self.frame)
        self.title = tk.Label(self.title_frame, font = "Arial 12 bold", text = self.trait_name)
        self.xp = tk.Label(self.title_frame, font = "Arial 12 bold", text = "("+self.trait_xp+")")

        if (self.char.getEditMode() == "generation"):
            remove_button = tk.Button(self.title_frame, text = "Entfernen", command = self.removeTrait)
            remove_button.pack(side = tk.RIGHT, anchor = tk.E)



        if (int(self.trait_xp) > 0):
            self.xp.config(foreground = config.Colors.DARK_GREEN)
        else:
            self.xp.config(foreground = config.Colors.DARK_RED)
        self.title.pack(side = tk.LEFT, anchor = tk.W)
        self.xp.pack(side = tk.LEFT, anchor = tk.E)
        self.title_frame.pack(fill = tk.X)

        self.info_description = tk.Text(self.frame, wrap = tk.WORD)
        self.trait_specification = ""
        self.trait_ranks = ""
        self.trait_variables = ""

        specification = self.trait.find("./specification")
        if specification is not None:
            self.trait_specification = specification.get("name") + ": " + self.selected.get("spec") + "\n"
            index_start = self.info_description.index(tk.CURRENT)
            self.info_description.insert(tk.CURRENT, self.trait_specification)
            index_end = self.info_description.index(tk.CURRENT)
            self.info_description.tag_add("title",index_start,index_end)
            self.info_description.tag_config("title", font = "Arial 10 bold")
        
        description = self.char_trait.find("description")
        if description is None: description = self.trait.find("./description")
        self.setDescription(description)
        
        ranks = self.trait.findall("./rank")
        if (ranks):
            for rank in ranks:
                rank_id = rank.get("id")
                rank_name = rank.get("name")
                rank_selected = self.selected.get("rank-"+rank_id)
                rank_variable = "\n" + rank_name + ": " + rank_selected + "\n"
                index_start = self.info_description.index(tk.CURRENT)
                self.info_description.insert(tk.CURRENT, rank_variable)
                index_end = self.info_description.index(tk.CURRENT)
                self.info_description.tag_add("title",index_start,index_end)
                self.info_description.tag_config("title", font = "Arial 10 bold")
                
        variables = self.trait.findall("./variable")
        if (variables):
            for variable in variables:
                var_id = variable.get("id")
                var_name = variable.get("name")
                var_selected = self.selected.get("id-"+var_id)
                selected_variable = "\n" + var_name + ": " + var_selected + "\n"
                index_start = self.info_description.index(tk.CURRENT)
                self.info_description.insert(tk.CURRENT, selected_variable)
                index_end = self.info_description.index(tk.CURRENT)
                self.info_description.tag_add("spec",index_start,index_end)
                self.info_description.tag_config("spec", font = "Arial 10 bold")
                description = variable.find("./description[@value='"+var_selected+"']")
                self.setDescription(description)
        
        self.info_description.pack()
        self.frame.pack()

        self.window.focus()

    # retrieve the character trait based on the id passed as text_tag
    def getCharTrait(self, event):
        text = event.widget
        index = text.index(tk.CURRENT)
        tags = text.tag_names(index)
        trait = self.char.getTraitByID(tags[0])
        return trait
        
    def setDescription(self,section):
        if section is not None:
            if section.text is not None: 
                self.info_description.insert(tk.END,section.text)

            text_fragments = section.findall(".//text")
            fragment_count = 0
            for fragment in text_fragments:
                old_index = self.info_description.index(tk.CURRENT)
                self.info_description.insert(tk.END,fragment.text)
                new_index = self.info_description.index(tk.CURRENT)
                fragment_font = fragment.get("font")
                fragment_size = fragment.get("size")
                fragment_style = fragment.get("style")
                format_string = ""
                if (fragment_font):
                    format_string = fragment_font
                else: 
                    format_string = config.Style.FONT

                if (fragment_size):
                    format_string = format_string + " " + fragment_size
                else:
                    format_string = format_string + " " + config.Style.SIZE

                if (fragment_style):
                    format_string = format_string + " " + fragment_style

                fragment_id = "fragment" + str(fragment_count)
                self.info_description.tag_add(fragment_id, old_index, new_index)
                self.info_description.tag_config(fragment_id, font = format_string)
                fragment_count += 1
    def removeTrait(self):
        self.char.removeTraitByID(self.id)
        self.window.destroy()
        self.main.updateTraitList()

