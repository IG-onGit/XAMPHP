from imports import *


class index:
    ####################################################################################// Load
    def __init__(self, app="", cwd="", args=[]):
        self.app, self.cwd, self.args = app, cwd, args

        if platform.system() != "Windows":
            cli.error("XAMPHP is currently available only for Windows users")
            sys.exit()

        if not ctypes.windll.shell32.IsUserAnAdmin() != 0:
            cli.error("Run your CMD as an administrator when using XAMPHP")
            sys.exit()

        self.sources = os.path.join(self.app, ".system/sources")
        self.on = False
        pass

    def __exit__(self):
        if Localhost.check():
            if self.on:
                cli.done(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            self.stop()
        pass

    ####################################################################################// Main
    def start(self, domain=""):  # (domain) - Start the project with virtual domain
        domain = "localhost" if not domain.strip() else domain.strip()
        Localhost.start("xamphp", self.sources, self.cwd, {"domain": domain})

        self.on = True
        cli.done(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        N = 0
        while True:
            N = 1 if N >= 3 else N + 1
            cli.done(("." * N) + "      ", True)
            time.sleep(2)
        pass

    def stop(self):  # Stop the project if it didn't
        Localhost.stop("xamphp", self.sources, self.cwd)
        pass

    ####################################################################################// Helpers
