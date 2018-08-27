## Import Modules ##
import wx

## Folder Listings ##

## Tray Program Data ##
class ProgramIcon(TaskBarIcon):

    TBMENU_FOLDER = wx.NewId()
    TBMENU_RUN = wx.NewId()
    TBMENU_EXIT = wx.NewId()

    def __init__(self):
        TaskBarIcon.__init__(self)
        self.icon = wx.Icon(TRAY_ICON, wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon, TRAY_TOOLTIP)
        self.Bind(wx.EVT_MENU, self.Folder_Window, id=self.TBMENU_FOLDER)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_EXIT)
        self.Bind(wx.EVT_MENU, self.Run_Process, id=self.TBMENU_RUN)


    def CreatePopupMenu(self, evt=None):
        menu = wx.Menu()
        menu.Append(self.TBMENU_FOLDER, "Select Folders")
        menu.Append(self.TBMENU_RUN, "Run XML Processor")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_EXIT, "Exit")
        return menu

    def Folder_Window(self,evt):


        self.wx_folder_frame = wx.Frame(None, wx.ID_ANY, "Folder List")
        self.panel = wx.Panel(self.wx_folder_frame)
        self.vbox1 = wx.BoxSizer(wx.VERTICAL)
        self.wx_folder_listbox = wx.ListBox(self.panel, choices=folder_list, size=(50,50))
        self.vbox1.Add(self.wx_folder_listbox, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
        self.add_folder_button = wx.Button(self.panel,label="Add Folder")
        self.add_folder_button.Bind(wx.EVT_BUTTON, self.Add_Folder)
        self.vbox1.Add(self.add_folder_button, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.remove_folder_button = wx.Button(self.panel,label="Remove Folder")
        self.remove_folder_button.Bind(wx.EVT_BUTTON, self.Remove_Folder)
        self.vbox1.Add(self.remove_folder_button, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.panel.SetSizer(self.vbox1)
        self.wx_folder_frame.Show()

    def Add_Folder(self,evt):
        self.new_folder = wx.DirSelector("Choose Directory to Monitor:")
        folder_list.append(self.new_folder)
        self.wx_folder_listbox.Append(self.new_folder)
        self.folder_data = open('Folder_List.txt', 'w')
        self.folder_data.writelines(folder_list)
        self.folder_data.close()

    def Remove_Folder(self,evt):
        self.selected_index = self.wx_folder_listbox.GetSelection()
        self.selected_string = self.wx_folder_listbox.GetString(self.selected_index)
        self.wx_folder_listbox.Delete(self.selected_index)
        folder_list.remove(self.selected_string)
        self.folder_data = open('Folder_List.txt', 'w')
        self.folder_data.writelines(folder_list)
        self.folder_data.close()


    def OnTaskBarClose(self,evt):
        self.Destroy()

    def Run_Process(self,evt):
        Folder_Monitor(folder_list)

## Establish Main Window ##
if __name__ == '__main__':
    app = wx.App()
