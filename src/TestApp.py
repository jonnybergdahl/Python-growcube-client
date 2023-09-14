import npyscreen


class ValueForm(npyscreen.ActionFormMinimal):
    def create(self):
        self.widget = self.add(npyscreen.TitleText, name="Enter a Value:", value="")


    def on_ok(self):
        # This method is called when the user presses "OK"
        self.parentApp.switchForm(None)  # Exit the application


class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", ValueForm, name="Enter Value")


if __name__ == "__main__":
    app = MyApp()
    app.run()
